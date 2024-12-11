

from pm.loggen.wpn_loggen import *
from pm.metrics.relevance import relevance_uniform_roleset
from pm.pmmodels.plpn import *
from pm.pmmodels.tracefreq import TraceFrequency, RoleTraceFrequency
from pmkoalas.models.petrinet import LabelledPetriNet


DEFAULT_LOG_GRANULARITY = 1000 

def enclose_trace(trace: tuple, iset: set, 
                  fset: set) -> tuple:
    return tuple([iset] + list(trace) + [fset])   


'''
Add entries corresponding to the initial and final places in a Petri net to 
each log entry.
'''
def enclose_traces(log:dict, initial_place_label='I',
                   final_place_label='F') -> dict:
    result = {}
    iset = frozenset([initial_place_label])
    fset = frozenset([final_place_label])
    for t in log:
        nt = enclose_trace(t,iset,fset)
        result[nt] = log[t]
    return result

def entropic_relevance(log: dict, model: LabelledPetriNet, marking: Marking, 
                       loggran=DEFAULT_LOG_GRANULARITY) -> float:
    elog = enclose_traces(log)
    ltf = RoleTraceFrequency(elog)
    print('Log TF')
    print(ltf)
    sem = PLPNSemantics(marking)
    wslg = WeightedTokenGameStateLogGenerator(sem,loggran)
    mtf = RoleTraceFrequency(wslg.generate())
    print('Model TF')
    print(mtf)
    return relevance_uniform_roleset(ltf, mtf)

