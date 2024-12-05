'''
Extract cohorts by district
'''


from datetime import datetime
from cgedq.conv import *
from cgedq.logutil import * 
from cgedq.mine import mineJobStates, mineJobStatesByRange
from cgedq.trans import loadplacetransfile


def mine_export_job(job,tag,jevents,tmlrec,officials,positions,appointments,
                    rtrans, noise=0,pfloor=0):
    add_translations(jevents,rtrans)
    events = jevents.merge(tmlrec,on=['person_id','year'])
    info(f"Merged columns {list(events.columns.values)}")
    sjevents = events[events['synjob'] == '知縣'].copy()
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
                    officials,positions,appointments,topn=10 )
    mineJobStatesByRange('var',tag,noise=noise,years=[5,10,15,20,25,80])



def mine_by_job(job,tag,fin,rebuild_db,tmlin,inputtype,datadir):
    info(f"Started at {datetime.now()}")
    ds = load_datasets(fin,rebuild_db,tmlin,inputtype,datadir)
    mine_export_job(job,tag,ds.events,ds.tmlrec,ds.officials,ds.positions,
                   ds.appointments,ds.trans,noise=0.001)
    info(f"Finished at {datetime.now()}")


def main():
    args = main_parse()
    mine_by_job('知縣','jmagistrate', args.cgedqfile,args.rebuild,args.tmlfile,
                args.inputtype, args.datadir)


if __name__ == "__main__":
    main()


