
import logging
import os
import sys
from cgedq.mine import filterByTimeOnInt, mineByTime, mineJobStatesByRange
from pm.pmmodels.pnformatter import exportNetToScaledImage
from pm.ssnap.ssnap import sslogFromCSV, minePLPN, reportLogStats

logging.basicConfig(level=logging.INFO)


def minePLPNByTime(vard,fname,sslog:set,years:int,noise=0.0,font=None,
                   final=True):
    sslogn = filterByTimeOnInt(sslog, years)
    reportLogStats(sslogn, fname+ "_y" + str(years))
    plpn = minePLPN(sslogn,label=fname,noiseThreshold=noise,final=False)
    exportNetToScaledImage(vard,
            f"{fname}_n{10000*noise:04.0f}_ss{str(years).zfill(3)}y_plpn",plpn,
                           sslog, font)


def init_trans():
    trans = loadroletransfile()
    return trans



def magtails():
    tag = 'jmagtails' # sys.argv[1]
    # noise = 0.0005  # mess
    # noise = 0.001   # blows stack for RSN
    noise = 0.002 
    # noise = 0.003
    # noise = 0.01
    years = 25
    fname = f'cged-q-{tag}'
    vard = 'var'
    logfile = os.path.join(vard,fname+'.csv')
    sslog = sslogFromCSV(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeCol='year',
                         types = {'year':float },
                         keepSuccDupes=False)
    # reportLogStats(sslog,oname)
    # info("Mining states ..." )
    mineByTime(vard=vard,fname=fname,sslog=sslog,years=years,noise=noise,
               final=True)
    # minePLPNByTime(vard=vard,fname=fname,sslog=sslog,years=years,noise=noise,
    #            final=False)


def magintendant():
    tag = 'jmagintend' # sys.argv[1]
    # noise = 0.0005  # mess
    # noise = 0.001   # blows stack for RSN
    # noise = 0.002 
    # noise = 0.003
    noise = 0.01
    years = 25
    fname = f'cged-q-{tag}'
    vard = 'var'
    logfile = os.path.join(vard,fname+'.csv')
    sslog = sslogFromCSV(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeCol='year',
                         types = {'year':float },
                         keepSuccDupes=False)
    minePLPNByTime(vard=vard,fname=fname,sslog=sslog,years=years,noise=noise,
               final=False)


def magintendanttop():
    tag = 'jmagintendtop' # sys.argv[1]
    # noise = 0.01
    noise=0.0
    years = 25
    fname = f'cged-q-{tag}'
    vard = 'var'
    logfile = os.path.join(vard,fname+'.csv')
    sslog = sslogFromCSV(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeCol='year',
                         types = {'year':float },
                         keepSuccDupes=False)
    minePLPNByTime(vard=vard,fname=fname,sslog=sslog,years=years,noise=noise,
               final=False)


def mag():
    tag = 'jmagfull' # sys.argv[1]
    # tag = 'topjmagfull' # sys.argv[1]
    # noise = 0.0002      # blows stack using trace-variant noise reduction
    # noise = 0.001
    # noise = 0.001 
    # noise = 0.002 
    #for noise in [0.001, 0.002, 0.005]:
    for noise in [0.002]:
        #mineJobStatesByRange('var',tag,noise,years=[10,15,20,25])
        mineJobStatesByRange('var',tag,noise,years=[15])


def maggrad():
    tag = 'jmaggrad' 
    mineJobStatesByRange('var',tag,noise=0.002,years=[15])


if __name__ == '__main__':
    mag()
    # maggrad()
    # magtails()
    # magintendant()
    # magintendanttop()


