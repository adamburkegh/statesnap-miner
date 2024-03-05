
from datetime import datetime
import glob
import itertools
import os
import os.path
import sys

import pandas as pd
import pm4py
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from cgedq.logutil import *

from pmkoalas.models.petrinet import LabelledPetriNet
from pmmodels.pnformatter import ScaledFormatter, exportNetToScaledImage
from pmkoalas.models.dotutil import dot_to_img, export_DOT_to_image
import pmmodels.pm4pyviz
from ssnap.ssnap import mine, sslogFromCSV, sslogWithRanges, reportLogStats


setLogLevel(logging.INFO)

# trange = 'cged-q-1900-1912'
trange = 'cged-q'
subset = 'nb-toptrans-京師'

EXPORT = True
ENGFONT = 'Times-Roman'





# Uses custom DOT export instead of direct graphviz integration
def exportTreeToImage(ptree,bdir,fname):
    net, initial, final = pm4py.convert_to_petri_net(ptree)   
    bpmn = pm4py.convert_to_bpmn(ptree)
    # print('BPMN {}'.format(dir(bpmn)) )
    # print('BPMN nodes {}'.format(bpmn.get_nodes()) )
    # print('BPMN flows {}'.format(bpmn.get_flows()) )
    dot = pmmodels.pm4pyviz.netToDOT(net,font='SimSun')
    dotf = os.path.join(bdir,fname+'.dot')
    ptreef = os.path.join(bdir,fname+'.ptml')
    imgpnf = os.path.join(bdir,fname+'_pn.png')
    netf = os.path.join(bdir,fname+'.pnml')
    bpmnf = os.path.join(bdir,fname+'.bpmn')
    imgbpmnf = os.path.join(bdir,fname+'_bpmn.png')
    ptml_exporter.apply(ptree, ptreef)
    pm4py.write_pnml(net,initial,final,netf)
    # dot_to_img(dot,dotf,imgpnf)
    bpmndot = pmmodels.pm4pyviz.bpmnToDOT(bpmn,font='SimSun')
    dot_to_img(bpmndot,dotf,imgbpmnf)
    dot_to_img(dot,dotf,imgpnf)




def mineByRegion(vard):
    gp = vard + '/' + trange + '-nb-toptrans*.csv'
    for cf in [os.path.basename(x)[:-4] for x in glob.glob(gp)]:
        print(cf)
        mine(vard,cf)

def mineRegionTransitions(vard):
    fname = trange+'-nb-trans'
    log_csv = pd.read_csv(os.path.join(vard,fname+'.csv') )
    log_csv = log_csv.sort_values('syntime')
    log_csv['case:concept:name'] = log_csv['synpersonid']
    log_csv['concept:name'] = log_csv['diqu']
    log_csv['time:timestamp'] = log_csv['syntime']
    event_log = log_converter.apply(log_csv)
    params = {inductive_miner.Variants.IMf.value.Parameters.NOISE_THRESHOLD:0.0}
    net, initial_marking, final_marking =  \
        inductive_miner.apply(event_log,
                variant=inductive_miner.Variants.IMf, 
                parameters=params)
    exportTreeToImage(ptree,vard,fname+'regpath')


YMD='%Y%m%d-%H:%M:%S'

def mineJobs(vard,fid):
    fname = trange+'-' + fid
    print("loading ..." + fname )
    event_log = pd.read_csv(os.path.join(vard,fname+'.csv') )
    event_log['end_yyyymm'] = pd.to_datetime(event_log['end_yyyymm'],
                                                format=YMD )
    event_log['person_id'] = str(event_log['person_id'])
    print("sorting ...")
    if EXPORT:
        pm4py.write.write_xes(event_log, os.path.join(vard,fname+'.xes'),
                                case_id_key='person_id')
    print("mining ...")
    ptree = pm4py.discover_process_tree_inductive(event_log,
                                    case_id_key='person_id',
                                    activity_key='synjob', 
                                    timestamp_key='end_yyyymm' )
    exportTreeToImage(ptree,vard,fname)
    print("done")


def filterByTimeOnInt(sslog:set, years: int ) -> set:
    # Not a model of efficiency
    result = {}
    for caseId in sslog:
        trace = sslog[caseId]
        ntrace = []
        head = trace[0]
        for ss in trace:
            if ss.time > head.time + years:
                break
            ntrace.append(ss)
        result[caseId] = ntrace
    return result

def filterByTimeOnDate(sslog:set, years: int ) -> set:
    # Not a model of efficiency
    byCase = {}
    result = set()
    for ss in sslog:
        if ss.caseId in byCase:
            byCase[ss.caseId] |= set([ss])
        else:
            byCase[ss.caseId] = set([ss])
    for case in byCase:
        states = sorted( byCase[case], key = lambda ss: ss.time )
        head = states[0] 
        # Note this only works because we know the day of month is always
        # set to 1 in earlier code. Otherwise we would hit 29 Feb problems like 
        # here 
        # https://stackoverflow.com/questions/32799428/adding-years-in-python
        cutoff = datetime.strptime(head.time,YMD)
        cutoff = cutoff.replace(year=cutoff.year + years)
        cuts = cutoff.strftime(YMD)
        states = [ ss for ss in states if ss.time <= cuts  ]
        result |= set(states)
    return result


def exportNetToImage(vard,oname,pn):
    dotStr = convert_net_to_dot(pn)
    export_DOT_to_image(vard,oname,dotStr)

def mineByTime(vard,fname,sslog:set,years:int,noise=0.0,font=None):
    sslogn = filterByTimeOnInt(sslog, years)
    reportLogStats(sslogn, fname+ "_y" + str(years))
    pn = mine(sslogn,noiseThreshold=noise)
    tsum = sum([tran.weight for tran in pn.transitions])
    info(f'Total weights: {tsum} ... weight threshold: {noise*tsum}')
    exportNetToScaledImage(vard,
            f"{fname}_n{10000*noise:04.0f}_ss{str(years).zfill(3)}y",pn,sslog,
            font)
    # exportNetToImage(vard,f"{fname}_ss{str(years).zfill(3)}y",pn)

def mineJobStates(vard,fid,noise=0.0):
    fname = f'{trange}-{fid}'
    fnameeng = fname + 'eng'
    info("Loading ..." + fname )
    logfile = os.path.join(vard,fname+'.csv')
    oname = fname + '_ss'
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    reportLogStats(sslog,oname)
    sslogeng = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    info("Mining states ..." )
    # pn = mine(sslog)
    # exportNetToImage(vard,oname,pn)
    #mineByTime(vard,fname,sslog,1,noise)
    mineByTime(vard,fname,sslog,2,noise)
    mineByTime(vard,fname,sslog,3,noise)
    mineByTime(vard,fname,sslog,5,noise)
    # mineByTime(vard,fname,sslog,10)
    mineByTime(vard,fnameeng,sslogeng,2,noise,font=ENGFONT)
    mineByTime(vard,fnameeng,sslogeng,3,noise,font=ENGFONT)
    mineByTime(vard,fnameeng,sslogeng,5,noise,font=ENGFONT)
    


def mineJobStatesFullOnly(vard,fid):
    fname = trange+'-' + fid
    info("Loading ..." + fname )
    logfile = os.path.join(vard,fname+'.csv')
    oname = fname + '_ss'
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    info(sslog)
    info("Mining states ..." )
    pn = mine(sslog)
    exportNetToImage(vard,oname,pn)



def main():
    # mineByRegion('var')
    # mineRegionTransitions('var')
    if len(sys.argv) > 1:
        trange = sys.argv[1]
    # mineJobs('var','tophanlin')
    # mineJobs('var','topjinshi')
    # mineJobs('var','toptoppers')
    # mineJobs('var','toptoppersinit')
    # mineJobs('var','toppersnoguards')
    # mineJobs('var','toptoppersnoguards')
    # mineJobs('var','toppers')
    # mineJobs('var','topguards')
    # mineJobs('var','guards')
    # mineJobs('var','topzynoguardsn20')
    # mineJobStates('var','topzynoguardsn20')
    # mineJobStates('var','topzynoguardsn50')
    # mineJobStates('var','topzynoguardsnall')
    # mineJobStates('var','topnoguardsn20')
    # mineJobStates('var','topnoguardsnall')
    # mineJobStates('var','bynoguardsnall')
    # mineJobStates('var','thnoguardsnall')
    mineJobStates('var','zyjtnall')
    # mineJobStates('var','byjtall')
    # mineJobStates('var','thjtnall')
    mineJobStates('var','t1jtall')
    # mineJobStates('var','t2jtall') too many states
    # mineJobStates('var','topt2jtn05') 
    # mineJobStates('var','topt2jtn05',0.0005) 
    #mineJobStates('var','topt2jtn10',0.0005) 
    mineJobStates('var','topt12jtn07',0.0008) 
    #mineJobStates('var','topt2jtn10') # already hard to read
    #mineJobStates('var','test2')
    # mineJobStates('var','zypurple')
    # mineJobStates('var','topjinshi')
    # mineJobStatesFullOnly('var','zypurple')
    # mineJobStatesFullOnly('var','178610052600')
    info("Done")


if __name__ == '__main__':
    main()


