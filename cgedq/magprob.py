'''
Calculating conformance metrics on magistrate models.
'''

from collections import defaultdict
import logging
import os.path

from cgedq.mine import filterByTimeOnInt
from pm.logs.statesnaplog import noiseReduceByVariant, sslogFromCSV, \
        sslogWithRanges
from pm.loggen.wpn_loggen import generate_log
from pm.metrics.relevance import relevance_uniform_roleset, \
        relevance_zero_order, show_model_cost
from pm.metrics.earthmovers import unit_earthmovers
from pm.pmmodels.tracefreq import RoleTraceFrequency
from pm.ssnap.ssnap import mine

logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
#logging.basicConfig(level=logging.DEBUG, format="%(message)s")
logging.basicConfig(level=logging.INFO, format="%(message)s")


vard = 'var'


def formatFrozen(fset):
    outstr = "{" 
    first = True
    for entry in fset:
        if not first:
            outstr += ","
        first = False
        outstr += entry
    outstr += "}"
    return outstr

def formatTrace(trace):
    init = "rt["
    outstr = init
    first = True
    for roles in trace:
        if not first:
            outstr += ",\n   "
        first = False
        outstr += formatFrozen(roles)
    outstr += "]"
    return outstr


def checklog(log):
    lsum = 0 ;  zsum = 0
    secretary = 'Secretary (of Ministry or Board)'
    magistrate = 'County Magistrate'
    secmag = frozenset([secretary,magistrate])
    magtrace = (frozenset([magistrate]),)
    magtracem = (frozenset(['I']),frozenset([magistrate]),frozenset(['F']) )   
    sm = 0 ; sec = 0; mm = 0
    for trace in log:
        # print(f"{formatTrace(trace)} ... {log[trace]}" )
        lsum += log[trace]
        if secmag in trace:
            sm += log[trace]
        for ss in trace:
            if secretary in ss:
                sec += log[trace]
        if trace == magtrace or trace == magtracem:
            mm += log[trace]
    info( f"  Size: {lsum}")
    info( f"    Probability of Secretary: {sec/lsum}")
    info( f"    Probability of Secretary and Magistrate joint role: {sm/lsum}")
    info( f"    Probability of Magistrate only: {mm/lsum}")


def listsecmag(log):
    lsum = 0 ;  zsum = 0
    secretary = 'Secretary (of Ministry or Board)'
    magistrate = 'County Magistrate'
    secmag = frozenset([secretary,magistrate])
    magtrace = (frozenset([magistrate]),)
    magtracem = (frozenset(['I']),frozenset([magistrate]),frozenset(['F']) )   
    sm = 0 ; sec = 0; mm = 0
    print(f"Joint secretary and magistrates:")
    for trace in log:
        # print(f"{formatTrace(trace)} ... {log[trace]}" )
        lsum += log[trace]
        if secmag in trace:
            # print(f"Joint secretary and magistrate:")
            print(f"{formatTrace(trace)} ... {log[trace]}" )
            # print(f"{trace} ... {log[trace]}" )
            sm += log[trace]
        for ss in trace:
            if secretary in ss:
                sec += log[trace]
        if trace == magtrace or trace == magtracem:
            mm += log[trace]


def sslog_to_summary(sslog):
    result = defaultdict(int)
    for case in sslog:
        trace = []
        for rs in sslog[case]:
            ss = frozenset(rs.activities)
            trace.append(ss)
        entry = tuple(trace)
        result[entry] += 1
    return result


def metrics(rep1,rep2,desc):
    tf1 = RoleTraceFrequency(rep1)
    tf2 = RoleTraceFrequency(rep2)
    # info(tf1)
    # info(tf2)
    ru = relevance_uniform_roleset(tf1,tf2)
    rz = relevance_zero_order(tf1,tf2)
    uem = unit_earthmovers(tf1,tf2)
    #info(f"    Entropic model cost")
    #show_model_cost(tf1,"tf1")
    #show_model_cost(tf2,"tf2")
    info(f"{desc}: ... :: " )
    info(f"        Entropic relevance (uniform roleset bg): {ru:>7.3f}")
    info(f"        Entropic relevance (zero order bg)     : {rz:>7.3f}")
    info(f"        Unit earth movers                      : {uem:>7.3f}")


def clip(rep1):
    ''' 
    Remove top and tail of each trace, particularly for when they are the 
    I and F place labels.
    '''
    elements = {}
    for trace in rep1:
        ctrace = trace[1:-1]
        elements[ctrace] = rep1[trace]
    return elements


def magprob():
    maglogname = 'var/cged-q-jmagfull.csv'
    tag='jmagfull'
    info("Magistrates")
    info(f"Loading ... {maglogname}" )
    noise = 0.002
    gensize = 10000
    # logfile = os.path.join(vard,maglogname+'.csv')
    sslogeng = sslogWithRanges(maglogname,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    # llog = sslog_to_summary(sslogeng)
    maglog = filterByTimeOnInt(sslogeng, years=15)
    llog = sslog_to_summary(maglog)
    nlog = sslog_to_summary( noiseReduceByVariant(maglog,noise) )
    info(f"Discovering ... {tag}")
    model = mine(maglog,label=tag,noiseThreshold=noise,final=True)
    info(f"Calculating probabilities ... ")
    mlang = generate_log(model,size=gensize)
    info(f"  Model probabilities ... ")
    checklog(mlang)
    info(f"  Log probabilities (noise) ... ")
    checklog(llog)
    info(f"  Log probabilities (de-noised) ... ")
    checklog(nlog)
    #
    info("Palace Grad Magistrates")
    maggradslogname = 'var/cged-q-jmaggrad.csv'
    gradtag = 'jmaggrad'
    info(f"Loading ... {maggradslogname}" )
    # logfile = os.path.join(vard,maglogname+'.csv')
    ssgradlogeng = sslogWithRanges(maggradslogname,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)   
    maggradlog = filterByTimeOnInt(ssgradlogeng, years=15)   
    lglog = sslog_to_summary(maggradlog)
    nglog = sslog_to_summary( noiseReduceByVariant(maggradlog,noise) )
    info(f"Discovering ... {gradtag}")
    gmodel = mine(maggradlog,label=gradtag,noiseThreshold=noise,final=True)
    info(f"Calculating probabilities ... ")
    mgradlang = generate_log(gmodel,size=gensize)
    info(f"  Model probabilities ... ")
    checklog(mgradlang)
    info(f"  Log probabilities (noise) ... ")
    checklog(lglog)
    info(f"  Log probabilities (de-noised) ... ")
    checklog(nglog)
    #
    info("Metrics ...")
    mclip = clip(mlang)
    mgradclip = clip(mgradlang)
    metrics(llog,lglog,"    magistrate all vs palace, noise, log vs log")
    metrics(llog,mclip,"    magistrate all, noise, log vs model")
    metrics(lglog,mgradclip,"    magistrate palace grads, noise, log vs model")
    metrics(nlog,nglog,"    magistrate all vs palace, de-noise, log vs log")
    metrics(nlog,mclip,"    magistrate all, de-noise, log vs model")
    metrics(nglog,mgradclip,"    magistrate palace grads, de-noise, log vs model")
    metrics(mclip,mgradclip,"    magistrate all vs palace, model vs model")
    metrics(mgradclip,mclip,"    magistrate palace vs all, model vs model")


def magsectrace():
    info("Palace Grad Magistrates")
    maggradslogname = 'var/cged-q-jmaggrad.csv'
    gradtag = 'jmaggrad'
    info(f"Loading ... {maggradslogname}" )
    # logfile = os.path.join(vard,maglogname+'.csv')
    ssgradlogeng = sslogWithRanges(maggradslogname,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)   
    maggradlog = filterByTimeOnInt(ssgradlogeng, years=15)   
    lglog = sslog_to_summary(maggradlog)
    listsecmag(lglog)


if __name__ == '__main__':
    # magprob()
    magsectrace()

