'''
Calculating conformance metrics on magistrate models.
'''

from collections import defaultdict
import os.path

from cgedq.logutil import *
from cgedq.mine import filterByTimeOnInt
from pm.loggen.wpn_loggen import generate_log
from pm.ssnap.ssnap import sslogFromCSV, sslogWithRanges, mine

# setLogLevel(logging.DEBUG)

vard = 'var'

def formatTrace(trace):
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
    info( f"Log size: {lsum}")
    info( f"   Probability of Secretary: {sec/lsum}")
    info( f"   Probability of Secretary and Magistrate joint role: {sm/lsum}")
    info( f"   Probability of Magistrate only: {mm/lsum}")

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


def magprob():
    maglogname = 'var/cged-q-jmagfull.csv'
    tag='jmagfull'
    info("Magistrates")
    info(f"Loading ... {maglogname}" )
    # logfile = os.path.join(vard,maglogname+'.csv')
    sslogeng = sslogWithRanges(maglogname,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    # llog = sslog_to_summary(sslogeng)
    maglog = filterByTimeOnInt(sslogeng, years=15)
    llog = sslog_to_summary(maglog)
    info(f"Discovering ... {tag}")
    model = mine(maglog,label=tag,noiseThreshold=0.002,final=True)
    info(f"Calculating probabilities ... ")
    mlang = generate_log(model,size=10000)
    checklog(mlang)
    info(f"Log probabilities ... ")
    checklog(llog)
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
    info(f"Discovering ... {gradtag}")
    gmodel = mine(maggradlog,label=gradtag,noiseThreshold=0.002,final=True)
    info(f"Calculating probabilities ... ")
    mgradlang = generate_log(gmodel,size=10000)
    checklog(mgradlang)
    info(f"Log probabilities ... ")
    checklog(lglog)


if __name__ == '__main__':
    magprob()

