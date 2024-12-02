'''
Alkhammash, H., Polyvyanyy, A., Moffat, A., & Garcia-Banuelos, L. (2021).
Entropic relevance: A mechanism for measuring stochastic process models
discovered from event data. Information Systems, 101922.
https://doi.org/10.1016/j.is.2021.101922

Adapted for role traces where each entry is a set of roles. 
Uniform background model only.
'''


import math

# class BackgroundModel(Enum):
#     UNIFORM = 1
#     ZERO_ORDER = 2              # Future
#     RESTRICTED_ZERO_ORDER = 3   # Future
#     ROLE_SET_UNIFORM = 4        

debug = print

class TraceFrequency:
    def __init__(self,elements:dict = {}):
        self._elements = elements
        self._trace_total = sum( elements.values() )
        self._roles = set( [r for t in self._elements for r in t] ) 

    def freq(self,trace):
        if trace in self._elements:
            return self._elements[trace]
        return 0

    def trace_total(self):
        return self._trace_total

    def role_total(self):
        return len(self._roles)

    '''
    Treat return value as read-only.
    '''
    def traces(self):
        return self._elements.keys()

class RoleTraceFrequency(TraceFrequency):
    def __init__(self,elements:dict = {}):
        self._elements = elements
        self._trace_total = sum( elements.values() )
        self._roles = \
                set( [r for t in self._elements for rs in t for r in rs] ) 


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
            # debug(f'Compression model cost: {trace!s:33} {cost}')
        else:
            cost = logTF.freq(trace) * background_cost(logTF,trace)
            bgc += cost
            # debug(f'Compression bg cost: {trace!s:33} {cost}')
        lsum += cost
    return lsum / logTF.trace_total()


def uniform_prelude_cost(logTF: TraceFrequency,modelTF: TraceFrequency):
    return 0

prelude_cost = uniform_prelude_cost


def relevance(logTF: TraceFrequency, modelTF: TraceFrequency,
              background_cost) -> float:
    return selector_cost(logTF,modelTF) \
         + trace_compression_cost(logTF,modelTF,background_cost) \
         + prelude_cost(logTF,modelTF)


'''
Entropic relevance with uniform background cost model.
'''
def relevance_uniform(logTF: TraceFrequency, modelTF: TraceFrequency):
    return relevance(logTF,modelTF,uniform_background_cost)


'''
Entropic relevance with uniform roleset background cost model.
'''
def relevance_uniform_roleset(logTF: TraceFrequency, modelTF: TraceFrequency):
    return relevance(logTF,modelTF,uniform_role_background_cost)


