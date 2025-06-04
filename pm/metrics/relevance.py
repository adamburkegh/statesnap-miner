'''
Alkhammash, H., Polyvyanyy, A., Moffat, A., & Garcia-Banuelos, L. (2021).
Entropic relevance: A mechanism for measuring stochastic process models
discovered from event data. Information Systems, 101922.
https://doi.org/10.1016/j.is.2021.101922

Adapted for role traces where each entry is a set of roles. 
Uniform background model only.
'''


import logging
import math

from pm.logs.statesnaplog import format_trace
from pm.pmmodels.tracefreq import *

# class BackgroundModel(Enum):
#     UNIFORM = 1
#     ZERO_ORDER = 2              
#     RESTRICTED_ZERO_ORDER = 3   # Future
#     ROLE_SET_UNIFORM = 4        


logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info


def model_cost(modelTF: TraceFrequency, trace) -> float: 
		return -1.0 * \
                math.log2( modelTF.freq(trace)/ modelTF.trace_total() )


'''
logTF and modelTF are unused in the universal background cost model,
except for the logActivityCount.

bits_U(t,E,M) = (|t|+1)log_2( |u(E)|+1 )

In the paper a hat notation is used to indicate a terminal symbol
is included. Here we include the +1 in the formula itself.
'''
def uniform_background_cost(logTF,trace):
    return (len(trace) + 1) * math.log2( logTF.role_total()+1 );

def uniform_role_background_cost(logTF,trace):
    return (len(trace) + 1) * math.log2( (2**logTF.role_total())+1 );

# def zero_order_background_cost(logTF:TraceFrequency, roleFreq:EntryFrequency,
#                                trace) -> float:
#     roleCtWithTerminals = roleFreq.entry_total() + logTF.trace_total()
#     sumv = 0
#     for entry in trace:
#         sumv += math.log2( roleFreq.entry_freq(entry) / roleCtWithTerminals)
#     sumv += math.log2( logTF.trace_total() / roleCtWithTerminals )
#     return -1*sumv



background_cost = uniform_background_cost


def selector_cost(logTF: TraceFrequency, modelTF: TraceFrequency) -> float:
    lsum = 0
    full_coverage = True
    for trace in logTF.traces():
        mf = modelTF.freq(trace)
        if mf > 0:
            lsum += logTF.freq(trace)
        else:
            full_coverage = False
    if (lsum == 0) or full_coverage:
        return 0
    rho = lsum / logTF.trace_total()
    return -1 * (rho * math.log2(rho) + (1 - rho)*math.log2(1 - rho));


def trace_compression_cost(logTF: TraceFrequency, 
                           modelTF: TraceFrequency,
                           background_cost) -> float:
    lsum = 0
    mc = 0
    bgc = 0
    for trace in logTF.traces():
        mf = modelTF.freq(trace)
        cost = 0
        if mf > 0:
            cost = logTF.freq(trace) * model_cost(modelTF,trace)
            mc += cost
            debug(f'Compression model cost: {format_trace(trace)!s:33} {cost}')
        else:
            cost = logTF.freq(trace) * background_cost(logTF,trace)
            bgc += cost
            debug(f'Compression bg cost: {format_trace(trace)!s:33} {cost}')
        lsum += cost
    debug(f'Trace compression cost: {lsum / logTF.trace_total()}')
    return lsum / logTF.trace_total()


def log2floor(x:float) -> float:
    return math.floor(math.log2(x))

def elias_gamma(x:float) -> float:
    return 2 * log2floor(x) + 1


def uniform_prelude_cost(logTF: TraceFrequency,modelTF: TraceFrequency):
    return 0


class RelevanceCalculator:
    def relevance(self,logTF: TraceFrequency, modelTF: TraceFrequency) -> float:
        return selector_cost(logTF,modelTF) \
             + trace_compression_cost(logTF,modelTF,self.background_cost)\
             + self.prelude_cost(logTF,modelTF)


class UniformRelevanceCalculator(RelevanceCalculator):
    def __init__(self):
        self.prelude_cost = uniform_prelude_cost
        self.background_cost = uniform_background_cost

uniform_relevance_calculator = UniformRelevanceCalculator()



class UniformRelevanceCalculator(RelevanceCalculator):
    def __init__(self):
        self.prelude_cost = uniform_prelude_cost
        self.background_cost = uniform_role_background_cost

uniform_relevance_roleset_calculator = UniformRelevanceCalculator()


'''
Entropic relevance with uniform background cost model.
'''
def relevance_uniform(logTF: TraceFrequency, modelTF: TraceFrequency) -> float:
    return uniform_relevance_calculator.relevance(logTF, modelTF)


'''
Entropic relevance with uniform roleset background cost model.
'''
def relevance_uniform_roleset(logTF: TraceFrequency, 
                              modelTF: TraceFrequency) -> float:
    return uniform_relevance_roleset_calculator.relevance(logTF,modelTF)




class ZeroOrderRelevanceCalculator(RelevanceCalculator):
    def __init__(self,logTF,modelTF):
        self.prelude_cost = \
                lambda logTf, modelTf: \
                    self.zero_order_prelude_cost(logTf)
        self._roleFreq = EntryFrequency(logTF)
        self.background_cost = \
                lambda logTf, trace: \
                        self.zero_order_background_cost(logTf,
                                                        self._roleFreq,
                                                        trace)
        self._logTF = logTF
        self._modelTF = modelTF


    def zero_order_prelude_cost(self, logTF: TraceFrequency) -> float: 
        entries = self._roleFreq.entries()
        sum = 0
        for entry in entries:
            sum += elias_gamma( entries[entry]+1 )
        return (sum + elias_gamma( logTF.trace_total() +1 ))/logTF.trace_total()

    def zero_order_background_cost(self,logTF:TraceFrequency, 
                                   roleFreq:EntryFrequency, trace) -> float:
        debug(f'zero_order_bg {trace}')
        roleCtWithTerminals = roleFreq.entry_total() + logTF.trace_total()
        sumv = 0
        for entry in trace:
            entrybits =  math.log2( roleFreq.entry_freq(entry) / \
                                    roleCtWithTerminals)
            sumv += entrybits 
            debug(f'    {entry}  ... {entrybits}')
        sumv += math.log2( logTF.trace_total() / roleCtWithTerminals )
        debug(f'    {-1*sumv}') 
        return -1*sumv


'''
Entropic relevance with zero order background cost model.
'''
def relevance_zero_order(logTF: TraceFrequency, modelTF: TraceFrequency)  \
        -> float:
    zoc = ZeroOrderRelevanceCalculator(logTF,modelTF)
    return zoc.relevance(logTF, modelTF)


def show_model_cost(tf,name):
    info( f'Model TF {name}')
    for trace in tf.traces():
        info( f'{trace!s:30}  ... {model_cost(tf,trace)}' )
    info('+++')


