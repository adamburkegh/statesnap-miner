'''
Mine a place-labelled SLPN from a state snapshot log.
'''

import csv
from dataclasses import dataclass
from typing import Any
from operator import attrgetter

from pmkoalas.models.petrinet import *
from logging import debug, info



class StateSnapshot:
    def __init__(self,caseId,time,activities):
        self._caseId = caseId
        self._time = time
        self._activities = frozenset(activities)

    @property
    def caseId(self):
        return self._caseId

    @property
    def time(self):
        return self._time

    @property
    def activities(self):
        return self._activities

    def __eq__(self,other):
        if type(self) == type(other):
            return (self._caseId,self._time,self._activities) \
                    ==  (other._caseId,other._time,other._activities)

    def __hash__(self):
        return hash( (self._caseId, self._time, self._activities) )

    def __repr__(self):
        return f"StateSnapshot: {self.caseId} @ {self.time} = {self.activities}"

'''
Adds transition and its connecting arcs. Returns set of arcs. 
'''
def arcsSpanningTran(fromActs,tran,toActs,atop) -> set:
    arcs =  [Arc(atop[pl],tran) for pl in fromActs]
    arcs += [Arc(tran,atop[pl]) for pl in toActs]
    return set(arcs)

'''
Side effect: mutates atot.
'''
def addTransition(fromPlaces,toPlaces,tranId,atot,tweights) -> Transition:
    if (fromPlaces,toPlaces) in atot:
        tran = atot[(fromPlaces,toPlaces)]
        tweights[tran] = tweights[tran] + 1 
    else:
        tranId += 1
        tran = silent_transition(tid = tranId)
        atot[(fromPlaces,toPlaces)] = tran
        tweights[tran] = 1
    return tran

'''
Adds places for activities if absent. Returns the new place identifier.
Side effect: mutates atop.
'''
def addPlaces(atop: dict, activities: set, pid: int) -> int: 
    for act in activities:
        if not act in atop:
            pid += 1
            pl = Place(name=act,pid=pid)
            atop[act] = pl
    return pid

def arcSetDiff(s1,s2):
    if s1 == s2:
        return "Same"
    result = f"#S1 = {len(s1)}\n"
    for arc in s1:
        result += f"    {arc} {arc.__hash__()}\n"
    result += f"#S2 = {len(s2)}\n"
    for arc in s2:
        result += f"    {arc} {arc.__hash__()}\n"
    result += "In S1, not in S2:\n"
    for arc in s1:
        if arc not in s2:
            result += f"    {arc}\n"
    result += "\nIn S2, not in S1:\n"
    for arc in s2:
        if arc not in s1:
            result += f"    {arc}\n"
    result += f"Union: {s1 | s2} \n"
    result += f"Intersect: {s1 & s2} \n"
    return result

def minePure(sslog: dict,label=None,final=True) -> LabelledPetriNet:
    debug("mine()")
    arcs = set()
    atop = {}
    atot = {}
    # Mutating the weight changes the hash of the transition object
    # and Python set comparisons start breaking because the implementation
    # caches the hash
    tweights = {}
    tranId = 0
    pid = 1
    initialPlace = Place(name='I',pid=1)
    atop[initialPlace.name] = initialPlace
    if final:
        pid = 2
        finalPlace = Place(name='F',pid=pid)
        atop[finalPlace.name] = finalPlace
    for caseId in sslog:
        trace = sslog[caseId]
        prevAct = None
        for snap in trace:
            fact = frozenset(snap.activities)
            if not prevAct:
                prevAct = frozenset([initialPlace.name])
            pid = addPlaces(atop,fact,pid)
            tran = addTransition(prevAct,fact,tranId,atot,tweights)
            tranId = max(tranId,tran.tid)
            newarcs = arcsSpanningTran(prevAct,tran,fact,atop)
            arcs |= newarcs
            prevAct = fact
        # final logic goes here
        if final:
            tran = addTransition(prevAct,finalPlace.name,tranId,atot,tweights)
            tranId = max(tranId,tran.tid)
            newarcs |= arcsSpanningTran(prevAct,tran,finalPlace.name,atop)
            arcs |= newarcs
    places = set( atop.values() ) | set([initialPlace])
    if final:
        places |= set([finalPlace])
    transitions = set()
    for tran in atot.values():
        tran.weight = tweights[tran]
        transitions.add(tran)
    return LabelledPetriNet( places = places, transitions = transitions, 
                             arcs = arcs, name=label )

'''
Prune transitions with weights below a noise threshold, their arcs, and if no arcs connecting them exist, the corresponding places.

This noise reduction can produce disconnected nets if there is no role conflation for low-frequency places. For example if the noise threshold is two, the following net will be disconnected after noise reduction.

(I)  -> [1] -> (p1) -> [1] -> (p4)
(I)  -> [1] -> (p2) -> [1] -> (p4) -> [4] -> (p5)
(I)  -> [1] -> (p3) -> [1] -> (p4)
(I)  -> [3]                               -> (p6)

(This follows the ASCII art notation of the pnfrag tool. Repeated place nodes with the same label represent the same place.)

This gets noise reduced to:

(I)  -> [3] -> (p6)
(p4) -> [4] -> (p5)

Which is disconnected.
'''
def pruneForNoise(pnet,noiseThreshold):
    tsum = 0
    for tran in pnet.transitions:
        tsum += tran.weight
    weightThreshold = noiseThreshold * tsum
    debug(f'weight threshold: {weightThreshold}')
    keeptrans = set([tran for tran in pnet.transitions \
                        if tran.weight > weightThreshold])
    keeparcs = set([arc for arc in pnet.arcs \
                    if arc.from_node in keeptrans or arc.to_node in keeptrans])
    keepplaces = set([arc.from_node for arc in keeparcs \
                            if arc.from_node in pnet.places ])
    keepplaces = keepplaces.union(
                    set([arc.to_node for arc in keeparcs \
                            if arc.to_node in pnet.places ]) )
    result = LabelledPetriNet(keepplaces,keeptrans,keeparcs,pnet.name)
    return result

def mine(sslog: dict, label=None, noiseThreshold=0.0, final=False) \
            -> LabelledPetriNet:
    pnet = minePure(sslog,label,final)
    if noiseThreshold > 0:
        return pruneForNoise(pnet,noiseThreshold)
    else:
        return pnet



def getField(row,col,types):
    if types and col in types:
        return types[col]( row[col] )
    else:
        return row[col]

def sslogFromCSV(csvfile,caseIdCol,activityCol,timeCol,keepSuccDupes=True,
                 types : dict = None, encoding='utf-8' ) -> set :
    '''
    Load a state snapshot log from a CSV with a header.

    If keepSuccDupe is False, states that repeat over time are pruned.
    '''
    sslog = None
    with open(csvfile,encoding=encoding) as csvf:
        reader = csv.DictReader(csvf)
        sslog = sslogParse(reader,caseIdCol,activityCol,timeCol,keepSuccDupes,
                           types, encoding)
    return sslog

def sslogWithRanges(csvfile,caseIdCol,activityCol,timeColStart,timeColEnd,
                    timeInc=0.25, keepSuccDupes=True, types : dict = None, 
                    encoding='utf-8' ) -> set :
    '''
    Load a state snapshot log from a CSV with a header. The file is expected 
    to be normalised on the time dimension by using time ranges in columns
    timeColStart and timeColEnd instead of restated for each time period.
    Otherwise behaves as sslogFromCSV.
    '''
    sslogIn = []
    with open(csvfile,encoding=encoding) as csvf:
        reader = csv.DictReader(csvf)
        for row in reader:
            caseId = getField(row,caseIdCol,types)
            startTime =  getField(row,timeColStart,types)
            endTime =  getField(row,timeColEnd,types)
            activity = getField(row,activityCol,types)
            ctTime = startTime
            while (ctTime <= endTime):
                nrow = row.copy()
                nrow[timeColStart] = ctTime
                sslogIn.append(nrow)
                ctTime += timeInc
    return sslogParse(sslogIn,caseIdCol,activityCol,timeColStart,keepSuccDupes,
                      types,encoding)

def sslogParse(rowData,caseIdCol,activityCol,timeCol,keepSuccDupes=True,
                types : dict = None, encoding='utf-8' ) -> dict :
    ctToSS = {}
    for row in rowData:
        caseId = getField(row,caseIdCol,types)
        time =  getField(row,timeCol,types)
        activity = getField(row,activityCol,types)
        ss = None
        if (caseId,time) in ctToSS:
            oldSS = ctToSS[ (caseId,time) ] 
            newact = set(oldSS.activities); newact.add(activity)
            ss = StateSnapshot(caseId,time,newact )
        else:
            ss = StateSnapshot(caseId,time,set([activity]) )
        ctToSS[(caseId,time)] = ss
    return ssSetToLog(ctToSS,keepSuccDupes)


def ssSetToLog(ctToSS: dict,keepSuccDupes) -> dict :
    sslog = dict()
    prevState = None
    ctTrace = []
    for (caseId,time) in sorted( ctToSS ):
        if prevState and caseId == prevState.caseId:
            ss = ctToSS[ (caseId,time) ] 
            if keepSuccDupes or (prevState.activities != ss.activities):
                ctTrace.append(ss)
        else: # new case
            if prevState:
                sslog[prevState.caseId] = ctTrace
            ctTrace = [ ctToSS[ (caseId,time) ] ] 
        prevState = ctToSS[ (caseId,time) ] 
    sslog[prevState.caseId] = ctTrace
    return sslog

def reportLogStats(sslog: dict,logname: str = None):
    result = ""
    if logname:
        result += f"== Log: {logname} ==\n"
    result += f"  Cases: {len(sslog)}"
    states = 0
    minRoles = 1
    maxRoles = 1
    for case in sslog:
        for ss in sslog[case]:
            states += 1
            minRoles = min(minRoles,len(ss.activities))
            maxRoles = max(maxRoles,len(ss.activities))
    result += f"  Min / max #roles: {minRoles} / {maxRoles}\n"
    result += f"  # states: {states}"
    info(result)



