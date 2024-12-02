'''
Extract cohorts by region
'''


from datetime import datetime
from cgedq.conv import *
from cgedq.logutil import * 
from cgedq.mine import mineJobStates
from cgedq.roledict import regions
from cgedq.trans import loadplacetransfile


def export_regions(jevents,tmlrec,officials,positions,appointments,rtrans,
                   ptrans,noise=0):
    add_translations(jevents,rtrans)
    events = jevents.merge(tmlrec,on=['person_id','year'])
    info(f"Merged columns {list(events.columns.values)}")
    # t1events = events[events['甲第'].isin( set([1]) )].copy()
    # t2events = events[events['甲第'].isin( set([2]) )].copy()
    t12events = events[events['甲第'].isin( set([1,2]) )].copy()
    #
    # t1init = selectfrominit(t1events, "Tier 1 graduates {}" )
    # t2init = selectfrominit(t2events, "Tier 2 graduates {}" )
    t12init = selectfrominit(t12events, "Tier 1&2 graduates {}" )
    #
    #guard_mask = events[jobfield].str.contains(GUARD)
    #guards = events.query('@guard_mask').copy()
    #allguards = set(guards[personfield])
    #
    ct = 1
    for region in regions:
        rt = 'r' + str(ct)
        if region in ptrans:
            rt = ptrans[region]
        tag = 't12' + rt
        print(tag)
        revent = t12init[t12init['ren_sheng'] == region].copy()
        if len(revent) > 0:
            info(f"Extraction for {tag}")
            extract_norm_events(revent,tag,
                    officials,positions,appointments,topn=10 )
            mineJobStates('var',tag,noise=noise)
        else:
            info(f"Skipping empty region {region}")
        ct += 1


def load_place_pinyin():
    ptransobj = loadplacetransfile()
    return { p:ptransobj[p].pinyin for p in ptransobj}


def mine_regions(fin,rebuild_db,tmlin,inputtype,datadir):
    info(f"Started at {datetime.now()}")
    ptrans = load_place_pinyin()
    print(f'Places {ptrans}')
    ds = load_datasets(fin,rebuild_db,tmlin,inputtype,datadir)
    export_regions(ds.events,ds.tmlrec,ds.officials,ds.positions,
                   ds.appointments,ds.trans,ptrans,noise=0.05)
    info(f"Finished at {datetime.now()}")


def main():
    args = main_parse()
    mine_regions(args.cgedqfile,args.rebuild,args.tmlfile,args.inputtype,
            args.datadir)


if __name__ == "__main__":
    main()


