'''
Mine a place-labelled SLPN from a state snapshot log.
'''

from collections import defaultdict
from datetime import datetime
from itertools import chain, combinations
import logging
from typing import Any
from operator import attrgetter

from pmkoalas.models.petrinet import *
from pm.logs.statesnaplog import *
from pm.pmmodels.conform import reachable_markings, sort_place_tuple_seq
from pm.pmmodels.rsnet import *


logger = logging.getLogger(__name__)
debug, info = logger.debug, logger.info





'''
Adds transition and its connecting arcs. Returns set of arcs. 
'''
def arcsSpanningTran(fromActs,tran,toActs,atop) -> set:
    arcs =  [Arc(atop[pl],tran) for pl in fromActs]
    arcs += [Arc(tran,atop[pl]) for pl in toActs]
    return set(arcs)

'''
Side effect: mutates atot and tweights.
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

def minePurePLPN(sslog: dict,label=None,final=True) -> LabelledPetriNet:
    debug("minePLPN()")
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

def addRSNetFinalTransitions(partialNet, atot, atop, tranId, tweights, arcs, 
                             initialPlace, finalPlace, finals, finalRS,
                             unobservedWeight=0.8):
    '''
    Mutates input parameters, particularly atot and arcs.
    '''
    marking = Marking( partialNet, {initialPlace:1} )
    sem = RoleStateNetSemantics(marking)
    markings = reachable_markings(sem)
    # debug(f'activities {len(activities)}')
    # debug(f'placeSubsets {len(set(placeSubsets))} {placeSubsets}')
    debug(f'atop {atop}')
    nameMarkings = \
        sorted([tuple(sorted([place.name for place, ct in marking])) \
                             for marking in markings])
    debug(f'nameMarkings {nameMarkings}')
    for placeNames in nameMarkings:
        # debug(f'    marking {marking}')
        # placeNames = frozenset([place.name for place, ct in marking])
        debug(f'    places {placeNames}')
        # picky transitions going to final
        if len(placeNames) == 0:    # skip empty set
            continue
        if placeNames == (initialPlace.name,):
            # no final transition from initial place
            continue
        tranId += 1
        tran = silent_transition(tid=tranId)
        tran.picky = True
        tran.observed = True
        fPlaceNames = frozenset(placeNames)
        if fPlaceNames in finals:
            tweights[tran] = finals[fPlaceNames]
        else:
            tweights[tran] = unobservedWeight
            tran.observed = False
        atot[(fPlaceNames,finalRS)] = tran
        tranId = max(tranId,tran.tid)
        newarcs = arcsSpanningTran(fPlaceNames,tran,finalPlace.name,atop)
        arcs |= newarcs

def minePureRoleStateNet(sslog: dict,label=None, final=True) -> RoleStateNet:
    '''
    Mine a RoleStateNet, which has picky transitions to a final place for all 
    reachable markings. 
    '''
    debug("minePureRoleStateNet()")
    arcs = set()
    activities = set()
    atop = {}
    atot = {}
    # Mutating the weight changes the hash of the transition object
    # and Python set comparisons start breaking because the implementation
    # caches the hash
    tweights = {}
    tranId = 0
    pid = 1
    initialPlace = Place(name='I',pid=1)
    initRS =  frozenset([initialPlace.name])
    atop[initialPlace.name] = initialPlace
    pid = 2
    finals = {}
    for caseId in sorted(sslog.keys()):
        trace = sslog[caseId]
        prevAct = None
        for snap in trace:
            fact = frozenset(snap.activities)
            activities.update(fact)
            if not prevAct:
                prevAct = initRS
            pid = addPlaces(atop,fact,pid)
            tran = addTransition(prevAct,fact,tranId,atot,tweights)
            tranId = max(tranId,tran.tid)
            newarcs = arcsSpanningTran(prevAct,tran,fact,atop)
            arcs |= newarcs
            prevAct = fact
        if prevAct in finals:
            finals[prevAct] += 1
        else:
            finals[prevAct] = 1
    if final:
        finalPlace = Place(name='F',pid=pid)
        finalPlace.final = True
        atop[finalPlace.name] = finalPlace
        finalRS = frozenset([finalPlace])
        places = set( atop.values() ) | set([initialPlace,finalPlace]) 
    else:
        places = set( atop.values() ) | set([initialPlace]) 
    transitions = set()
    for tran in atot.values():
        transitions.add(tran)
    partialNet = RoleStateNet( places = places, transitions = transitions, 
        arcs = arcs, name=label )
    if final:
        addRSNetFinalTransitions(partialNet, atot, atop, tranId, tweights, 
                                 arcs, initialPlace, finalPlace, finals, 
                                 finalRS)
        places = set( atop.values() ) | set([initialPlace,finalPlace]) 
    else:
        places = set( atop.values() ) | set([initialPlace]) 
    transitions = set()
    debug(f'tweights {tweights}')
    debug(f'atot {atot}')
    for tran in atot.values():
        tran.weight = tweights[tran]
        transitions.add(tran)
    return RoleStateNet( places = places, transitions = transitions, 
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
def pruneForNoiseByTranWeight(pnet,noiseThreshold):
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


def minePLPN(sslog: dict, label=None, noiseThreshold=0.0, final=False) \
            -> LabelledPetriNet:
    pnet = minePurePLPN(sslog,label,final)
    if noiseThreshold > 0:
        return pruneForNoiseByTranWeight(pnet,noiseThreshold)
    else:
        return pnet

def mineRoleStateNet(sslog: dict, label=None, noiseThreshold=0.0,final=True) \
            -> RoleStateNet:
    if noiseThreshold > 0:
        nrlog =  noiseReduceByVariant(sslog, noiseThreshold) 
        return minePureRoleStateNet(nrlog,label,final)
    else:
        return minePureRoleStateNet(sslog,label,final)

mine = mineRoleStateNet



