'''
Convert and filter CSV files provided by the Lee-Campbell Research Group 
for input to process mining tools. 

Current filters: non-bannermen only (filter by surname)
                 no vacant positions (filter by given name)
                 some data tidying

== References for data ==

Campbell, C. D., Chen, B., Ren, Y., & Lee, J. (2019). China Government Employee Database-Qing (CGED-Q) Jinshenlu 1900-1912 Public Release [Data set]. https://doi.org/10.14711/dataset/E9GKRS

Chen, B., Campbell, C., Ren, Y., & Lee, J. (2020). Big Data for the Study of Qing Officialdom: The China Government Employee Database-Qing (CGED-Q). Journal of Chinese History, 4(2), 431–460. https://doi.org/10.1017/jch.2020.15

Ren Yuxue, Bijia Chen, Xiaowen Hao, Cameron Campbell and James Lee. 2019. China Government Employee Dataset-Qing dynasty Jinshenlu 1900-1912 Public Release User Guide.

'''


import argparse
from datetime import datetime
from os.path import join
import os.path
import sys

import numpy as np
import pandas as pd
import sqlalchemy 
from sqlalchemy import create_engine

from cgedq.logutil import * 
from cgedq.roledict import knownroles, role_synonyms, hanzinorm, KONGBAI, GUARD
from cgedq.roledict import rank_defaults, topexam, zhuangyuan, bangyan, tanhua
from cgedq.roletrans import loadtransfile
from cgedq.norm import *



# Python 3.7+
denc = 'utf-8'

DATA_DIR = 'data'
# pandas seems to only work with pinyin column names
#fin='cged-q-ab-20220303.dta'
#fin='cg1000.tsv'
# tmlin = 'cged-q-ab-jsl-tml-20221012.dta'
inmemdbstr="sqlite://"
localdbstr="sqlite:///appoint.db"
dbstr=localdbstr


# Tables
OFFICIAL_TAB='official'
POSITION_TAB='position' # split positions
APPT_TAB='appointment'
JSL_RECORDS_TAB='jsl_records'
TML_RECORDS_TAB='tml_records'


BLANK = 'blank'
degreeorig = 'chushen_1_original'

stata_original_source = True  


def text(instr):
    result = instr
    if (instr == ''):
        result = BLANK
    # Is this too coarse. Blank record consolidation should have 
    # already happened before export
    return result


def normhanzi(instr):
    if (instr == ''):
        return BLANK
    res = ''
    keys = hanzinorm.keys()
    for t in instr:
        if t in keys:
            res += hanzinorm[t]
        else:
            res += t
    return res


def extract_events(sevents,seventid,topn=12):
    sevents_blanks = sevents.loc[sevents[jobfield] == BLANK]
    sevents_topjobs = sevents[[jobfield]].groupby(jobfield) \
                             .size() \
                             .nlargest(topn) \
                             .reset_index(name='topjob')
    info(seventid + ' top jobs \n {}'.format(sevents_topjobs) )
    st = set(sevents_topjobs[jobfield])
    sevents_topjobs = sevents[sevents[jobfield].isin(st)]
    sevents_restjobs = sevents[~sevents[jobfield].isin(st)].copy()
    if( len(sevents_restjobs) > 0 ):   
        sevents_restjobs[jobfield] = None
        if stata_original_source:
            sevents_restjobs[jobfield] = \
                'other-' + sevents_restjobs['pinji_category'].astype(str)
        else:
            sevents_restjobs[jobfield] = 'other-' \
                + sevents_restjobs['pinji_numeric'].astype(int).astype(str)
        sevents_topjobs = pd.concat([sevents_topjobs,sevents_restjobs],
                                      ignore_index=True)
    sevents = collapse_continuing_roles_ew(sevents)
    sevents_topjobs = collapse_continuing_roles_ew(sevents_topjobs)
    export_events(sevents,seventid)
    export_events(sevents_topjobs,'top' + seventid)
    export_events(sevents_blanks, seventid + 'blank')


def extract_norm_events(sevents_in,seventid,officials,positions,appointments,
                        topn=12):
    sevents_blanks = sevents_in.loc[sevents_in[jobfield] == BLANK]
    people = set(sevents_in['person_id'])
    info(seventid + ' officials: {} \n '.format(len(people)) )
    sappointments = appointments[appointments.person_id.isin(people)].copy()
    sofficials = officials[officials.person_id.isin(people)].copy()
    info(seventid + ' sofficials: {} \n '.format( len(sofficials) ) )
    sevents = sofficials.merge(sappointments,on='person_id')
    if stata_original_source:
        sevents.loc[sevents.synjob==BLANK,jobfield] = \
                    'other-' + sevents['pinji_category'].astype(str)
    else:
        sevents.loc[sevents.synjob==BLANK,jobfield] = \
                    'other-' + sevents['pinji_numeric'].astype(int).astype(str)
    sevents_topjobs = sevents[[jobfield]].groupby(jobfield) \
                             .size() \
                             .nlargest(topn) \
                             .reset_index(name='topjob')
    info(seventid + ' top jobs \n {}'.format(sevents_topjobs) )
    st = set(sevents_topjobs[jobfield])
    sevents_topjobs = sevents[sevents[jobfield].isin(st)].copy()
    sevents_restjobs = sevents[~sevents[jobfield].isin(st)].copy()
    if( len(sevents_restjobs) > 0 ):   
        if stata_original_source:
            sevents_restjobs[jobfield] = \
                'other-' + sevents_restjobs['pinji_category'].astype(str)
            sevents_restjobs[jobfieldeng] = \
                'other-' + sevents_restjobs['pinji_category'].astype(str)
        else:
            sevents_restjobs[jobfield] = 'other-' \
                + sevents_restjobs['pinji_numeric'].astype(int).astype(str)
            sevents_restjobs[jobfieldeng] = 'other-' \
                + sevents_restjobs['pinji_numeric'].astype(int).astype(str)
        sevents_topjobs = pd.concat([sevents_topjobs,sevents_restjobs],
                                      ignore_index=True)
    # sevents = collapse_continuing_roles(sevents)
    # debug(sevents.columns)
    #sevents_topjobs = collapse_continuing_roles(sevents_topjobs)
    export_events(sevents,seventid)
    export_events(sevents_topjobs,'top' + seventid)
    export_events(sevents_blanks, seventid + 'blank')

def export_events(events,suffix):
    outf = join('var','cged-q-' + suffix + '.csv')
    events.to_csv(outf, encoding=denc,index=False)
    info('Exported {} rows to {}'.format(len(events),outf) )


jsl_converters = {'record_number': np.int64, 'core_guanzhi': normhanzi,  # text
              'guanzhi': text, 'guanzhi_2': text, 
              'jigou_1': normhanzi, 'jigou_2': normhanzi, 'jigou_3': normhanzi,
              'diqu': text, 'person_id': text, 'year': np.float64,
              'chushen_category': text, 'chushen_1_original': text, 
              'pinji_detailed': text, 'xing': text }


tml_converters = {'person_id': text, 'xuhao_jsl': text  # text
                    }

def use_converters(df,convs):
    for conv in convs:
        df[conv] = df[conv].map( convs[conv] )

def loadrec(fin,converters):
    fpathj = join(DATA_DIR,fin)
    fpath = fpathj
    info(f'Loading data from {fpath} at {datetime.now()} ...')
    if not os.path.isfile(fpath):
        fpath = fin
        if not os.path.isfile(fpath):
            error(f"No such file {fpath} or {fpathj}")
            sys.exit(1)
    if fin.endswith('tsv'):
        recs = pd.read_csv( fpath , sep='\t', converters=converters )
    elif fin.endswith('csv'):
        recs = pd.read_csv( fpath , converters=converters )
    elif fin.endswith('dta'):
        recs = pd.read_stata( fpath )
        if converters:
            use_converters(recs,converters)
        stata_original_source = True # side effect
    else:
        error(f"Unrecognised format {fpath}")
        sys.exit(1)
    info( "{} rows loaded at {}".format(len(recs),datetime.now() ) )
    return recs

def use_converters(df,convs):
    for conv in convs:
        df[conv] = df[conv].map( convs[conv] )



def process_raw_tml(tmlin):
    if tmlin is None:
        return None
    tmlrec = loadrec(tmlin,converters=tml_converters)
    info(f"Timinglu: {tmlrec}")
    info(f"TML columns {list(tmlrec.columns.values)}")
    info(f"TML columns {tmlrec.dtypes}")
    info(tmlrec[['person_id','xuhao_jsl']])
    return tmlrec

def process_raw_cgedq(fin):
    debug('Known roles: {}'.format(knownroles) )
    cgedq  = loadrec(fin,converters=jsl_converters)

    # xuhao 序号 is the person identifier within an edition
    # clean the seasonal marker rows without this
    cgedq['xuhao'] = cgedq['xuhao'].replace('',np.nan)
    cgedq.dropna(subset=['xuhao'], inplace=True)

    # cgedq.dropna(subset=['year'], inplace=True)

    # select only non-banner officials using surname 
    # see Table 1 in Chen (2020) 
    cgedq['xing'] = cgedq['xing'].replace(BLANK,np.nan)
    cgedq.dropna(subset=['xing'], inplace=True)

    # remove vacant positions with blank given names. 
    # See p443 in Chen
    cgedq['ming'] = cgedq['ming'].replace('',np.nan)
    cgedq['ming'] = cgedq['ming'].replace(KONGBAI,np.nan) 
    # Sorry little Bobby Kongbai
    cgedq.dropna(subset=['ming'], inplace=True)

    # Replace null pinji_category (ie rank) with a default
    # pinji_category has a conversion bug when using csv
    if not stata_original_source:
        cgedq['pinji_category'] =  \
            cgedq['pinji_category'].fillna(DEFAULT_RANK)
        cgedq['pinji_numeric'] = \
            cgedq['pinji_numeric'].fillna(DEFAULT_RANK, inplace=True)
    if stata_original_source:
        cgedq['pinji_category'] =  \
                cgedq['pinji_category'].rename_categories(rank_defaults )

    cgedq[personfield] = cgedq[personfield].replace(BLANK,np.nan)
    cgedq.dropna(subset=[personfield], inplace=True)

    info( "{} clean and filtered rows".format(len(cgedq)) )

    # sorting may not be the best way given the composite key
    cq = cgedq.sort_values( by=['person_id','year'] )[cols]
    cq['date_yyyymm'] = np.floor(cq.year).astype(int).astype(str)   \
                + (np.modf(cq.year)[0]*12+3).astype(int) \
                .astype(str).str.pad(2, side='left', fillchar='0') \
                + '01-00:00:00'
    cq['synjob'] = cq['core_guanzhi']
    return cq

def process_clean_cgedq(fin):
    cq = loadrec(fin,converters=jsl_converters)
    # cq['synjob'] = cq['core_guanzhi']
    return cq


personfield = 'person_id'
#jobfield='guanzhi'
#jobfield='core_guanzhi'
jobfield='synjob'
jobfield2='synjob2'
jobfieldeng=jobfield+'_eng'
jobfield2eng=jobfield2+'_eng'
degreefield='chushen_category'

cols=['record_number','person_id','xing','ming','zihao',
      'core_guanzhi','guanzhi','guanzhi_2', 
      'pinji_category','pinji_detailed',
      'diqu','xuhao','year','jigou_1','jigou_2','jigou_3',
      'chushen_category','chushen_1_original','chushen_2_original',
      'chushen_order','chushen_order_2','chushen_1','chushen_2',
      'chushen_1_jinshi_from_ganzhi']

if not stata_original_source:
    cols += ['pinji_numeric']



def collapse_continuing_roles(edf):
    info("collapsing roles ...")
    pjob = edf.sort_values(['person_id',jobfield,'pinji_category','year']) \
                .groupby(['person_id',jobfield,'pinji_category']) 
    starts = pjob.agg({'year':'min','date_yyyymm':'min'}) \
                 .rename(columns={'year':'start_year',
                                 'date_yyyymm':'start_yyyymm'})
    result = starts.join( pjob.agg({'year':'max','date_yyyymm':'max'}) \
                              .rename(columns={'year':'end_year',
                                               'date_yyyymm':'end_yyyymm'}) )
    return result.reset_index()

def collapse_continuing_roles_ew(edf):
    # TODO consolidate the two collapse functions
    pjob = edf.sort_values(['person_id',jobfield,'year']) \
            .groupby(['person_id',jobfield]) \
            .first()
    return pjob.reset_index()

def mid_careers(edf,start_year=1830):
    MAX_YEAR = 2000
    pfe = edf.sort_values(by=[personfield]) \
             .groupby([personfield])['year'].min() \
             .reset_index() 
    mids = pfe[(pfe.person_id != BLANK) ]  
    mids = mids[mids.person_id.str[:4].astype(int) < np.floor(start_year) ]
    debug("People already mid-career \n {} \n".format(mids) )
    return set(mids[personfield])


# Very specific data problems that are candidates for repair in the main
# data source. Deprecated
def record_specific_repair_huchao(ds):
    # provincial governor misclassified as a fairly junior commander
    huchao = '182312141700'
    debug('Repairing ...')
    debug(cq.loc[cq['person_id'] == huchao])
    ds.loc[(ds['person_id'] == huchao) & (ds['core_guanzhi'] == '總兵官'),
             jobfield] = '提督'
    ds.loc[(ds['person_id'] == huchao) & (ds['core_guanzhi'] == '總兵官'),
             'pinji_category'] = '1-3'
    ds.loc[(ds['person_id'] == huchao) & (ds['core_guanzhi'] == '總兵官'),
            'core_guanzhi'] = '提督'


def normalize_events(ds,trans):
    officials = ds[['person_id','xing','ming']] \
                  .groupby('person_id') \
                  .first().reset_index()
    # 'chushen_category','chushen_1_original']].copy()
    # officials can have multiple degrees, traverse multiple locations,
    # and even have multiple variants of their name
    info('Officials: {}'.format(officials) )
    appointments = ds[['person_id',jobfield,'date_yyyymm','year', \
                        'pinji_category']].copy()
    appointments.drop_duplicates(inplace=True)
    appointments = normalize_positions_df(appointments,knownroles)
    appointments[jobfield] = appointments[jobfield].replace(role_synonyms)
    appointments = collapse_continuing_roles(appointments)
    add_translations(appointments,trans)
    info('Appointments: {}'.format(appointments) )
    positions = ds[[jobfield]].copy()
    positions.drop_duplicates(inplace=True)
    positions = normalize_positions(positions,knownroles)
    positions[jobfield] = positions[jobfield].replace(role_synonyms)
    positions.drop_duplicates(inplace=True)
    info('Positions: {}'.format(positions) )
    return (officials,positions,appointments)

def rsToStr(rs):
    res = ""
    for row in rs:
        for val in row:
            res += val + '\t'
        res += '\n'
    return res

def validation():
    info('Validating ...')
    engine = dbengine()
    with engine.connect() as conn:
        rs = engine.execute(    
                       "SELECT person_id, count(*) ct FROM official " 
                     + "GROUP BY person_id "
                     + "HAVING ct > 1" )
        dno = [row[0] for row in rs]
        if dno:
            warn('Officials breaking normalization: {}'.format(len(dno)))
            pids = str(dno).replace('[','(').replace(']',')')
            rs = engine.execute(    
                       "SELECT * FROM official "
                     + "WHERE person_id in " + pids )
            warn( rsToStr(rs) )
    

def events_position_syn(events):
    events[jobfield2] = events[jobfield]
    events[jobfield].replace( role_synonyms )

def dbengine():
    # Was Future=False due to pandas sqlalchemy 2.0 bug
    # https://github.com/pandas-dev/pandas/issues/40686#issuecomment-872031119
    # https://stackoverflow.com/questions/70067023/pandas-and-sqlalchemy-df-to-sql-with-sqlalchemy-2-0-fututre-true-throws-an-er
    return create_engine(dbstr, echo=False)

def recreate_event_db(officials,positions,appointments,events=None,tmlrec=None):
    engine = dbengine()
    with engine.connect() as conn:
        officials.to_sql(OFFICIAL_TAB,con=conn,index=False,
                     index_label='person_id',if_exists='replace')
        positions.to_sql(POSITION_TAB,con=conn,index=False,index_label=jobfield,
                     if_exists='replace')
        appointments.to_sql(APPT_TAB,con=conn,if_exists='replace')
        if not events is None:
            events.to_sql(JSL_RECORDS_TAB,con=conn,if_exists='replace')
            # CREATE INDEX jsr_pid_yr on  jsl_records (person_id,year);
        if not tmlrec is None:
            tmlrec.to_sql(TML_RECORDS_TAB,con=conn,if_exists='replace')

def selectfrominit(sevents,msg):
    pnmids = mid_careers(sevents) 
    contpn = set(sevents[personfield])
    pninit = sevents[~sevents[personfield].isin(pnmids)].copy()
    info(msg.format( len(contpn) ) )
    return pninit




def filter_basic(cq):
    events = pd.DataFrame(data=cq)
    events_position_syn(events)

    info("Events {}\n".format(events) )

    # Restrict to jingshi region 
    # regions = events['diqu'].unique()
    # info ("Regions \n{} ".format(regions) )

    # core_guanzhi -> jigou_2 -> jigou_1
    jgmask = (events[jobfield] == BLANK) & (events['jigou_2'].isin(knownroles) )
    events.loc[jgmask, jobfield] = events.loc[jgmask, 'jigou_2']

    jgmask = (events[jobfield] == BLANK) & (events['jigou_1'].isin(knownroles) )
    events.loc[jgmask,jobfield] = events.loc[jgmask, 'jigou_1']

    events[degreefield] = \
            events[degreefield].replace( {'Jinshi': '進士',
                                  'Juren': '舉人'} )
    events[jobfield] = \
            events[jobfield].replace( role_synonyms ) 
    return events


def apply_trans(trans):
    return lambda hz: trans[hz].translation if hz in trans else hz

def add_translations(cq,trans):
    cq[jobfieldeng] = cq[jobfield].apply(apply_trans(trans))
    return cq


def export_variants(events,officials,positions,appointments,trans):
    add_translations(events,trans)
    jinshi = events[events[degreefield] == '進士' ].copy()

    export_events(events,'all-clean')
    export_events(jinshi, 'jinshi-clean')

    zy = events[events[degreeorig].isin( set([zhuangyuan])  )].copy()
    zyinit = selectfrominit(zy, "Zhuangyuan (from init) {}" )

    by = events[events[degreeorig].isin( set([bangyan])  )].copy()
    byinit = selectfrominit(by, "Bangyan (2nd) (from init) {}" )

    th = events[events[degreeorig].isin( set([tanhua])  )].copy()
    thinit = selectfrominit(th, "Tanhua (3rd) (from init) {}" )

    toppers = events[events[degreeorig].isin(topexam)].copy()
    toppersinit = selectfrominit(toppers, "Top 3 (from init) {}" )

    guard_mask = events[jobfield].str.contains(GUARD)
    guards = events.query('@guard_mask').copy()
    midguards = mid_careers(guards)
    allguards = set(guards[personfield])
    contguards = allguards.difference(midguards)
    info("Guards {} mid-career {} remainder {} ".format( 
                    len(allguards),len(midguards),len(contguards) ) )
    guardevents = events[events.person_id.isin(contguards)].copy()

    zynoguards = zyinit[~zyinit[personfield].isin(allguards)].copy()
    bynoguards = byinit[~byinit[personfield].isin(allguards)].copy()
    thnoguards = thinit[~thinit[personfield].isin(allguards)].copy()
    toppersnoguards = \
            toppersinit[~toppersinit[personfield].isin(allguards)].copy()

    # hanlinstaff_mask = events['core_guanzhi'].str.contains(HANLIN)  \
    #                  | events['jigou_2'].str.contains(HANLIN) 
    # hanlinstaff = set(events.query('@hanlinstaff_mask').person_id)
    # hanlinevents = events[events.person_id.isin(hanlinstaff)].copy()

    # extract_events(hanlinevents,'hanlin')
    # extract_events(jinshi,'jinshi')
    # extract_events(toppers,'toppers')
    # extract_events(toppersinit,'toppersinit')
    # extract_events(toppersnoguards,'toppersnoguards',topn=14)
    # extract_events(guardevents,'guards',topn=20)
    # extract_norm_events(toppers,'toppersn',officials,positions,appointments)
    # extract_norm_events(toppersinit,'toppersinitn',officials,positions,appointments)
    extract_norm_events(jinshi,'jinshi',
                    officials,positions,appointments,topn=len(jinshi) )

    extract_norm_events(zynoguards,'zynoguardsn20',
                    officials,positions,appointments,topn=20)
    extract_norm_events(zynoguards,'zynoguardsn50',
                    officials,positions,appointments,topn=50)
    extract_norm_events(zynoguards,'zynoguardsnall', officials,
                        positions,appointments,topn=len(zynoguards) )

    extract_norm_events(bynoguards,'bynoguardsnall', officials,positions,
                        appointments,topn=len(bynoguards) )
    extract_norm_events(thnoguards,'thnoguardsnall', officials,positions,
                        appointments,topn=len(thnoguards) )

    extract_norm_events(toppersnoguards,'topnoguardsn20', officials,positions,
                        appointments,topn=20)
    extract_norm_events(toppersnoguards,'topnoguardsn50', officials,positions,
                        appointments,topn=50)
    extract_norm_events(toppersnoguards,'topnoguardsnall',officials,positions,
                        appointments,topn=len(toppersnoguards) )

def export_tml_variants(jevents,tmlrec,officials,positions,appointments,trans):
    add_translations(jevents,trans)
    events = jevents.merge(tmlrec,on=['person_id','year'])
    t1events = events[events['甲第'].isin( set([1]) )].copy() 
    t2events = events[events['甲第'].isin( set([2]) )].copy() 

    zy = t1events[t1events[degreeorig].isin( set([zhuangyuan])  )].copy()
    zyinit = selectfrominit(zy, "Zhuangyuan (from init) {}" )

    by = t1events[t1events[degreeorig].isin( set([bangyan])  )].copy()
    byinit = selectfrominit(by, "Bangyan (2nd) (from init) {}" )

    th = t1events[t1events[degreeorig].isin( set([tanhua])  )].copy()
    thinit = selectfrominit(th, "Tanhua (3rd) (from init) {}" )

    toppers = t1events[t1events[degreeorig].isin(topexam)].copy()
    toppersinit = selectfrominit(toppers, "Top 3 (from init) {}" )

    t1init = selectfrominit(t1events, "Tier 1 graduates {}" )
    t2init = selectfrominit(t2events, "Tier 2 graduates {}" )

    guard_mask = events[jobfield].str.contains(GUARD)
    guards = events.query('@guard_mask').copy()
    midguards = mid_careers(guards)
    allguards = set(guards[personfield])
    contguards = allguards.difference(midguards)
    info("Guards {} mid-career {} remainder {} ".format( 
                    len(allguards),len(midguards),len(contguards) ) )
    guardevents = events[events.person_id.isin(contguards)].copy()

    zynoguards = zyinit[~zyinit[personfield].isin(allguards)].copy()
    bynoguards = byinit[~byinit[personfield].isin(allguards)].copy()
    thnoguards = thinit[~thinit[personfield].isin(allguards)].copy()
    toppersnoguards = \
            toppersinit[~toppersinit[personfield].isin(allguards)].copy()

    extract_norm_events(zynoguards,'zyjtnall',
                    officials,positions,appointments,topn=len(zynoguards) )
    extract_norm_events(bynoguards,'byjtall',
                    officials,positions,appointments,topn=len(bynoguards) )
    extract_norm_events(thnoguards,'thjtnall',
                officials,positions,appointments,topn=len(thnoguards) )

    extract_norm_events(t1init,'t1jtall',
                    officials,positions,appointments,topn=len(t1init) )
    extract_norm_events(t2init,'t2jtall',
                    officials,positions,appointments,topn=len(t2init) )
    extract_norm_events(t2init,'t2jtn05',
                    officials,positions,appointments,topn=5 )
    extract_norm_events(t2init,'t2jtn10',
                    officials,positions,appointments,topn=10 )
    extract_norm_events(t2init,'t12jtn07',
                    officials,positions,appointments,topn=10 )


def process(fin,rebuild_db,tmlin,inputtype,datadir):
    global DATA_DIR 
    DATA_DIR = datadir
    trans = loadtransfile()
    tmlrec = process_raw_tml(tmlin)
    cq = None;  events = None
    if inputtype == 'raw':    
        cq = process_raw_cgedq(fin)
    if inputtype == 'clean':
        cq = process_clean_cgedq(fin)
    events = filter_basic(cq)
    (officials,positions,appointments) = normalize_events(events,trans)
    if rebuild_db:
        # Refers to rebuilding the originating record tables
        # Only needed when new data dump or hanzi normalization changes
        recreate_event_db(officials,positions,appointments,events,tmlrec) 
    else:
        recreate_event_db(officials,positions,appointments) 
    export_variants(events,officials,positions,appointments,trans)
    if not tmlrec is None:
        export_tml_variants(events,tmlrec,officials,positions,appointments,
                            trans)
    info(f"Finished at {datetime.now()}")

def process_public_extract():
    '''
    Cut-down version of process() to produce the extract of public data year 
    ranges.
    '''
    global DATA_DIR 
    DATA_DIR = 'data'
    fin = 'cged-q-ab-20220303.dta'
    tmlin = 'cged-q-ab-jsl-tml-20221012.dta'
    trans = loadtransfile()
    tmlrec = process_raw_tml(tmlin)
    cq = process_raw_cgedq(fin)
    events = filter_basic(cq)
    startyear = 1850
    public_mask1 = events.year.between(startyear,1864)
    # public_mask2 = events.year.between(1900,1910)
    events1 = events.query('@public_mask1').copy()
    # events2 = events.query('@public_mask2').copy()
    (officials,positions,appointments) = normalize_events(events1,trans)
    recreate_event_db(officials,positions,appointments) 
    export_variants(events1,officials,positions,appointments,trans)
    export_tml_variants(events,tmlrec,officials,positions,appointments,trans)
    tml_public_mask1 = tmlrec.year.between(startyear,1864)
    tmloutf = join('var',f'tml-{startyear}-public.csv')
    tmlrecp = tmlrec.query('@tml_public_mask1').copy()
    tmlrecp.to_csv(tmloutf, encoding=denc,index=False)
    info(f"Exported {len(tmlrecp)} TML records to {tmloutf}.")
    info(f"Finished public extract at {datetime.now()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cgedqfile')
    parser.add_argument('-i','--inputtype',choices=['raw','clean'], 
                        default='raw')
    parser.add_argument('--tmlfile')
    parser.add_argument('--rebuild',action='store_true',default=False)
    parser.add_argument('--datadir',default='data')
    args = parser.parse_args()
    fin = args.cgedqfile
    process(fin,args.rebuild,args.tmlfile,args.inputtype,args.datadir)


if __name__ == "__main__":
    main()
    # process_public_extract()




