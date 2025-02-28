'''
Definitions and functions for state snapshot logs, collections of sequences of
role sets.
'''


from collections import defaultdict
import csv





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



def sslogToCSV(sslog: dict, csvfile: str, caseIdCol,activityCol,timeCol,
               encoding='utf-8' ) -> set :
    '''
    Export a state snapshot log to a CSV file with a header.
    '''
    with open(csvfile,'w',encoding=encoding) as csvf:
        writer = csv.DictWriter(csvf,
                                fieldnames=[caseIdCol,activityCol,timeCol] )
        writer.writeheader()
        for caseId in sslog:
            trace = sslog[caseId]
            for ss in trace:
                for role in ss.activities:
                    row = {caseIdCol: caseId, activityCol: role,
                                   timeCol:ss.time }
                    writer.writerow( row )

def sslogWithRanges(csvfile,caseIdCol,activityCol,timeColStart,timeColEnd,
                    timeInc=0.25, keepSuccDupes=True, types : dict = None,
                    encoding='utf-8' ) -> dict :
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
    return ssDictToLog(ctToSS,keepSuccDupes)

def ssDictToLog(ctToSS: dict,keepSuccDupes) -> dict :
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
        result += f"== Log: {logname} == \n    @ {datetime.now()}\n"
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



def sstrace_to_variant(sstrace) -> tuple:
    lresult = [ss.activities for ss in sstrace]
    return tuple(lresult)

def noiseReduceByVariant(sslog: dict, noiseThreshold) -> dict:
    '''
    Remove trace variants where proportional frequency is less than the noise
    threshold.
    '''
    if noiseThreshold <= 0:
        return sslog
    variants = defaultdict(int)
    total = 0
    for ss in sslog:
        variant = sstrace_to_variant(sslog[ss])
        variants[variant] += 1
        total += 1
    threshold = noiseThreshold * total
    result = {}
    for ss in sslog:
        variant = sstrace_to_variant(sslog[ss])
        if variants[variant] >= threshold:
            result[ss] = sslog[ss]
    return result


def take_tails(sslog: dict, role, min_length:int=1) -> dict:
    '''
    Truncates each trace before the first occurrence of role. Returns sslog.
    '''
    result = {}
    for caseId in sslog:
        trace = sslog[caseId]
        newTrace = []
        inTail = False
        for ss in trace:
            if inTail:
                newTrace.append(ss)
            if role in ss.activities:
                inTail = True
                newTrace.append(ss)
        if len(newTrace) >= min_length:
            result[caseId] = newTrace
    return result


def filter_by_role(sslog: dict, role) -> dict:
    '''
    Keep only traces with role. Returns sslog.
    '''
    result = {}
    for caseId in sslog:
        trace = sslog[caseId]
        inTail = False
        for ss in trace:
            if role in ss.activities:
                result[caseId] = trace
                continue
    return result

def filter_by_roleset(sslog: dict, roles: list) -> dict:
    '''
    Keep only traces with an entry with all roles. Returns sslog.
    '''
    result = {}
    for caseId in sslog:
        trace = sslog[caseId]
        inTail = False
        for ss in trace:
            found = True
            for role in roles:
                if role not in ss.activities:
                    found = False
                    continue
            if found:
                result[caseId] = trace
    return result

def keep_top_roles(sslog: dict, keeptop:int, drop=False,
                   conflaterole='other') -> dict:
    '''
    Replace most frequent roles, as determined by keeptop. Conflate remaining
    roles into single role with label conflaterole. Returns sslog.
    '''
    result = {}
    rolefreq = defaultdict(int)
    for caseId in sslog:
        trace = sslog[caseId]
        for ss in trace:
            for role in ss.activities:
                rolefreq[role] += 1
    toproles = sorted([(-value,role) for (role,value) in rolefreq.items()])
    toproles = [role for (value,role) in toproles][:keeptop]
    for caseId in sslog:
        trace = sslog[caseId]
        newTrace = []
        inTail = False
        for ss in trace:
            if drop:
                newact = [role for role in ss.activities if role in toproles]
            else:
                newact = [role if role in toproles else conflaterole \
                            for role in ss.activities]
            newss = StateSnapshot(ss.caseId,ss.time,frozenset(newact) )
            newTrace.append(newss)
        result[caseId] = newTrace
    return result


def format_trace(trace):
    outstr = "["
    first = True
    for ss in trace:
        if first:
            first = False
        else:
            outstr += ", "
        outstr += f"{set(ss)}"
    outstr += "]"
    return outstr


