'''
Extract cohorts by district
'''


from datetime import datetime
import logging
from cgedq.conv import *
from cgedq.logutil import * 
from cgedq.mine import mineJobStates, mineJobStatesByRange
from cgedq.trans import loadplacetransfile

logger = logging.getLogger( __name__ )
# logger.setLevel( logging.DEBUG )


def mine_export_job(job,tag,jevents,tmlrec,officials,positions,appointments,
                    rtrans, topn, noise=0):
    add_translations(jevents,rtrans)
    events = jevents.merge(tmlrec,on=['person_id','year'])
    info(f"Merged columns {list(events.columns.values)}")
    sjevents = events[events['synjob'] == job].copy()
    jpeople = sjevents['person_id'].unique()
    if len(sjevents) == 0:
        print('No events')
        return
    print(f'Found {len(sjevents)} events')
    events = events[events['person_id'].isin(jpeople) ]
    # officials = officials[officials.person_id.isin(jpeople)].copy()
    rt = '(No translation)'
    if job in rtrans:
        rt = rtrans[job].translation
    jinit = selectfrominit(events, 
                            "Officials who served as " + job + " " + rt + \
                                    ": {}" )
    if len(jinit) == 0:
        print( f'No events after filtering for mid-career officials' )
        return
    extract_norm_events(jinit,tag,
                    officials,positions,appointments,topn=topn )
    mineJobStatesByRange('var',tag,noise=noise,years=[15,20])
    # mineJobStatesByRange('var',tag,noise=noise,years=[5,10,15,20,25,80])
    # mineJobStatesByRange('var','top'+tag,noise=2*noise,years=[5,10,15,20,25,80])



def mine_by_job(job,tag,noise,fin,rebuild_db,tmlin,inputtype,datadir,topn=10):
    info(f"Started at {datetime.now()}")
    ds = load_datasets(fin,rebuild_db,tmlin,inputtype,datadir)
    mine_export_job(job,tag,ds.events,ds.tmlrec,ds.officials,
                    ds.positions,ds.appointments,ds.trans,topn,noise)
    info(f"Finished at {datetime.now()}")


def main():
    logging.basicConfig(level=logging.INFO)
    args = main_parse()
    mine_by_job('知縣','jmagistrate', 0.0005, args.cgedqfile,args.rebuild,
                args.tmlfile, args.inputtype, args.datadir,topn=12)
    #mine_by_job('知縣','jmagistrate', 0.001, args.cgedqfile,args.rebuild,
    #            args.tmlfile, args.inputtype, args.datadir)
    # mine_by_job('文淵閣校理','jprofound', 0.002, args.cgedqfile,args.rebuild,
    #            args.tmlfile, args.inputtype, args.datadir)
    # mine_by_job('中允','jcomp', 0.002, args.cgedqfile,args.rebuild,
    #             args.tmlfile, args.inputtype, args.datadir)


if __name__ == "__main__":
    main()


