
from pm.pmmodels.tracefreq import TraceFrequency


def unit_earthmovers(tf1:TraceFrequency,tf2:TraceFrequency):
    '''
    The first parameter defines the support. 
    For log-model comparison, tf1 is considered the log.
    '''
    cumulative = 0
    for trace in tf1.traces():
        p1 = tf1.freq(trace) / tf1.trace_total()
        p2 = tf2.freq(trace) / tf2.trace_total()
        cumulative += max(p1-p2,0)
    return 1 - cumulative


