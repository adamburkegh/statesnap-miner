'''
Log generators on stochastic models.
'''

from dataclasses import dataclass
from logging import *
import math

from ssnap.ssnap import StateSnapshot
from pmmodels.plpn import *




class WeightedTokenGameStateLogGenerator:
    def __init__(self, semantics: PetriNetSemantics, log_size: int, 
                       max_trace_length: int = 100):
        self.semantics = semantics
        self.log_size = log_size
        # self.stack = []
        # Java implementation uses a local state stack to avoid 
        # blowing the Java call stack recursion limit
        self.max_trace_length = max_trace_length

    def generate(self) -> set:
        ''' 
        Returns a light state log: a dict[tuple[set(str)]: int].
        The tuple[set(str)] are traces, the strings are role labels, and the 
        ints are trace counts.
        '''
        self.have_warned = False
        return self.generate_from_mark(self.semantics._mark,self.log_size,())

    def generate_from_mark(self,ct_mark: Marking,budget:int,
                           parent_trace: tuple):
        debug( f"gen_from_mark( {ct_mark.mark}, {budget}, {parent_trace} ) " )
        total_weight = 0
        allocated = 0
        tow = {}
        result = {}
        new_trace = parent_trace + (self.state_snap_from_marking(ct_mark),)
        enabled = self.semantics.enabled()
        if enabled == set():
            # debug( f"  termination  return {new_trace}:{budget} " )
            return { new_trace: budget }
        if len(new_trace) >= self.max_trace_length:
            if not self.have_warned:
                self.have_warned = True
                warning( f"Log generation max trace length "
                         f"{self.max_trace_length} exceeded" )
            return { new_trace: budget }
        for tran in enabled:
            total_weight += tran.weight
        for tran in enabled:
            raw_budget = math.floor(budget * tran.weight / total_weight)
            allocated += raw_budget
            tow[tran] = raw_budget
        leftover = budget - allocated
        if leftover:
            self.allocate_leftover(tow,leftover)
        for tran in enabled:
            new_mark = self.semantics.remark(tran)
            sublog = self.generate_from_mark(new_mark,tow[tran],new_trace)
            self.semantics.mark = ct_mark
            result = bag_union( result, sublog)
        # debug( f"  continuation return {result} " )
        return result

    def state_snap_from_marking(self,mark: Marking) -> set:
        act = frozenset( [m.name for m in mark.mark ]  )
        return act

    def allocate_leftover(self,tow,leftover):
        balance = leftover
        strans = sorted( tow.keys(), 
                             key= lambda t: (t.name, tow[t], t.tid) )
        for tran in strans:
            if balance == 0:
                return 
            tow[tran] = tow[tran] + 1
            balance -= 1
        if balance > 0:
            error( ValueError("Underallocated budget in log generator") )


def bag_union( dict1: dict, dict2: dict ):
    result = {}
    for key in dict1:
        if key in dict2:
            result[key] = dict1[key] + dict2[key]
        else:
            result[key] = dict1[key]
    for key in dict2:
        if key not in result:
            result[key] = dict2[key]
    return result


