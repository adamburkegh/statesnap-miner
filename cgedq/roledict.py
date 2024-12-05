# -*- coding: utf-8 -*-

'''
Role dictionaries and mappings for the CGED-Q database from the 
Lee-Campbell Research Group.

Current filters: non-bannermen only (filter by surname)
                 no vacant positions (filter by given name)
                 some data tidying

== References ==

Campbell, C. D., Chen, B., Ren, Y., & Lee, J. (2019). China Government Employee Database-Qing (CGED-Q) Jinshenlu 1900-1912 Public Release [Data set]. https://doi.org/10.14711/dataset/E9GKRS

Chen, B., Campbell, C., Ren, Y., & Lee, J. (2020). Big Data for the Study of Qing Officialdom: The China Government Employee Database-Qing (CGED-Q). Journal of Chinese History, 4(2), 431–460. https://doi.org/10.1017/jch.2020.15

Chen, B. (2019). Origins and Career Patterns of the Qing Government Officials (1850-1912): Evidence from the China Government Employee Dataset-Qing (CGED-Q). HKUST PhD thesis.

Hucker, C. O. (1985). A Dictionary of Official Titles in Imperial China.

Ren Yuxue, Bijia Chen, Xiaowen Hao, Cameron Campbell and James Lee. 2019. China Government Employee Dataset-Qing dynasty Jinshenlu 1900-1912 Public Release User Guide.

'''

import csv



# Tables
OFFICIAL_TAB='official'
POSITION_TAB='position' # split positions
APPT_TAB='appointment'


# Glossary

KONGBAI = '空白'
BLANK = 'blank'
HANLIN = '翰林院'
GUARD= '侍衛'
BLUE_FEATHER='藍翎'
FLOWER_FEATHER='花翎'
CLASS='科'
DIRECTORATE_EDUCATION='國子監'

EXAMINER='考官'  
VICE_EXAMINER='副'+EXAMINER
VICE_EXAMINER2='副考'
CHIEF_EXAMINER='主考'  
GENERAL_EXAMINER='正'+ CHIEF_EXAMINER
HEAVENLY_GENERAL_EXAMINER = '順天正主考'
VICE_CHIEF_EXAMINER='副'+CHIEF_EXAMINER
PRINCIPAL_EXAMINER='正考官'
EDUCATION_COMMISSIONER='學政'
examiners = set([EXAMINER,VICE_EXAMINER,VICE_EXAMINER2,
                 CHIEF_EXAMINER,VICE_CHIEF_EXAMINER,
                 GENERAL_EXAMINER,EDUCATION_COMMISSIONER,
                 PRINCIPAL_EXAMINER])

COURIER='提塘'
couriers = set([COURIER])


INSTRUCTOR  ='教習'
INSTRUCTOR2 ='敎習'
INSTRUCTOR_PREFECTURE   ='教授'
INSTRUCTOR_PREFECTURE2  ='敎授'
# GRAND_MINISTER_INSTRUCTOR='教習大臣' In Hucker but not data
educators = set([INSTRUCTOR,INSTRUCTOR2,
                 INSTRUCTOR_PREFECTURE, INSTRUCTOR_PREFECTURE2])

UPPER_STUDENT='上書房'
UPPER_STUDENT2='上書房'
SOUTHERN_STUDENT='南書房'

students = set([UPPER_STUDENT,SOUTHERN_STUDENT])

CASUAL='行走'
internships=set([SOUTHERN_STUDENT+CASUAL,
                 UPPER_STUDENT+CASUAL])

SCHOLAR='上書房'

SENIOR_CHAIR='正總裁'
CHAIR='總裁'
VICE_CHAIR='副總裁'
VICE_CHAIR_TEMP='副總行走務'

COLLOQ='經筵'    # The classics colloquium
READER = '講官'
COLLOQ_READER=COLLOQ + READER
VICE_CHAIR_RECORDS='會典館副總裁'
VICE_CHAIR_RECORDS2='會典館副總裁務'
CHAIR_RECORDS='會典館' + CHAIR
scholars=set([VICE_CHAIR_RECORDS,VICE_CHAIR_RECORDS2,CHAIR_RECORDS,
              COLLOQ_READER])

ACADEMICIAN='學士'
GRAND_SECRETARY='大學士'
GRAND_SECRETARY2='大學士務'
CABINET_ACADEMICIAN='內閣學士'
CABINET_SECRETARY='内阁中书'
ASSISTANT_GRAND_SECRETARY='協辦大學士'
ASSISTANT_GRAND_SECRETARY2='協辦大學務'
ASSISTANT_GRAND_SECRETARY3='協辦大學士務'
ASSISTANT_GRAND_SECRETARY4='賞協辦大學士'
VICE_MINISTER='侍郎'
MINISTER='尚書'
MINISTER2='尚書銜'
GRAND_MINISTER='大臣' # Grand Minister?
BOARD_DIRECTOR='郎中'
GRAND_MINISTER_STATE='軍機大臣'
PROB_GRAND_MINISTER_STATE='軍機大臣'
seniorroles=set([BOARD_DIRECTOR,CABINET_ACADEMICIAN,
                 CABINET_SECRETARY,
                 ASSISTANT_GRAND_SECRETARY,ASSISTANT_GRAND_SECRETARY2,
                 ASSISTANT_GRAND_SECRETARY3,
                 GRAND_SECRETARY,GRAND_SECRETARY2,
                 VICE_MINISTER,
                 MINISTER,MINISTER2,
                 GRAND_MINISTER,
                 GRAND_MINISTER_STATE,PROB_GRAND_MINISTER_STATE])


ORDER_OF_PEACOCK='賞戴花翎' # Lit eye of peacock feather
ORDER_OF_PEACOCK_II='賞戴雙眼花翎' # Lit two eyed peacock feather
FIRST_BUTTON='頭品頂戴'
PURPLE_BRIDLE='賞用紫韁'
YELLOW_JACKET='賞穿黃馬褂'
BY_IMPERIAL_DECREE='欽命'
honours = set([BY_IMPERIAL_DECREE,
               ORDER_OF_PEACOCK, ORDER_OF_PEACOCK_II,
               FIRST_BUTTON,PURPLE_BRIDLE,YELLOW_JACKET])

CHANCELLOR_HANLIN='翰林院掌院學士'
CHANCELLOR_HANLIN2='翰林院掌院學士務'
hanlin = set([CHANCELLOR_HANLIN,CHANCELLOR_HANLIN2])

COMPANION_HEIR='中允'
JG_HEIR='太子少保'
SC_HEIR='太子太保'
MENTOR_HEIR='春坊庶子'
SPRING_COURT='春坊'
SPRINGC_HEIR=SPRING_COURT+COMPANION_HEIR
ADMONISHER='贊善'
SPRINGC_ADMONISHER=SPRING_COURT+ADMONISHER
heircompanions=set([COMPANION_HEIR,JG_HEIR,SC_HEIR,SPRINGC_HEIR,MENTOR_HEIR])

HEIR_ADMIN='詹事府詹事'
JUNIOR_HEIR_ADMIN='詹事府少詹事'
heiradmin = set([HEIR_ADMIN,JUNIOR_HEIR_ADMIN])

YUQING_PALACE_ATTENDANT='毓慶宫行走'
palaceroles = set([YUQING_PALACE_ATTENDANT])

INSPECTOR='稽察'
GRAND_INSPECTOR_GRANARIES='稽察京通十七倉大臣'
GRAND_INSPECTOR_GRANARIES2='稽察京通十七倉大臣務'
INSPECTOR_GRANARIES='稽查京通十七倉'
GRAND_SECRETARY_PRONOUNCEMENTS='大學士稽察欽奉上諭事件處'
PRONOUNCEMENTS='稽察欽奉上諭事件處' 
# Sometimes daxueshi title prefixes multiple offices
# We just split the office for now instead of anything more complicated
INSPECTOR_GIORO_ACADEMY='稽察翼覺羅學'
INSPECTOR_GIORO_ACADEMY2='稽查翼覺羅學'
INSPECTOR_IMPERIAL_ACADEMY='稽察翼宗學'
inspectors = set([GRAND_INSPECTOR_GRANARIES,GRAND_INSPECTOR_GRANARIES2,
                  INSPECTOR_GRANARIES,
                  GRAND_SECRETARY_PRONOUNCEMENTS,
                  PRONOUNCEMENTS,
                  INSPECTOR_GIORO_ACADEMY,INSPECTOR_GIORO_ACADEMY2,
                  INSPECTOR_IMPERIAL_ACADEMY])

SERVICE='務'
CONTROLLER = '掌'

DIRECTOR_STUDIES='司業'
CAPITAL_GOVERNOR='順天府府尹'
midroles=set([DIRECTOR_STUDIES,CAPITAL_GOVERNOR])

MANAGER='管理'

CENSOR = '監察御史'
CHIEF_CENSOR='都察院都御史'
CHIEF_CENSOR2='務都察院都御史'
CENSOR_INSPECTING='巡視'
censors = set([CENSOR,CHIEF_CENSOR,CHIEF_CENSOR2])

CHIEF_SHIFU='總師傅'
CHIEF_SHIFU2='總師傅'
masters = set([CHIEF_SHIFU,CHIEF_SHIFU2])

BACHELOR = '庶吉士'
DAY_OFFICIAL='日講起居注官' 
DAY_READER='日講起居官'
JUNIOR_COMPILER='编修'
JUNIOR_COMPILER2='編修' 
SENIOR_COMPILER='修撰' 
ATTENDANT_READER='侍讀'
ATTENDANT='侍講'
LIBATIONER=DIRECTORATE_EDUCATION+'祭酒'
LIBRARIAN='洗馬'
MINOR_CAPITAL_OFFICIAL='小京官'
juniorroles=[BACHELOR,DAY_OFFICIAL,JUNIOR_COMPILER,SENIOR_COMPILER,
             ATTENDANT_READER,ATTENDANT,COLLOQ_READER,
             LIBATIONER,LIBRARIAN,MINOR_CAPITAL_OFFICIAL]

ADMIN='事務'
ADMIN2='侍務'
SECRETARY='主事'    # of a department or board

COUNTY_MAGISTRATE = '知縣'
COUNTY_PREFECT = '知府'
countyroles = [COUNTY_MAGISTRATE,COUNTY_PREFECT]

DEPARTMENT_MAGISTRATE = '知州'
magistrates = [DEPARTMENT_MAGISTRATE]

DEFAULT_RANK=8

qingprovinces = ['安徽','福建','甘肅','廣東','廣西','貴州','河南','湖北','湖南',
                '江蘇','江西','陝西','山東','山西','四川','雲南','浙江','直隸',
                '新疆','奉天','吉林','黑龍江','臺灣']
regions = ['湖廣','京畿','江南','陝甘'] + qingprovinces
# 順天 Capital province during the Qing
FULL_PROVINCE='全省'

directions = ['北','南','東','西','中']

hanzinorm = { '宮': '宫',
              '内': '內',
              '衞':'衛',
              '戸':'戶',
              '顶':'頂',
              '郞':'郎',
              '検':'檢'}

departments = set(['禮部', # Rites
                   '戶部', # Revenue
                   '兵部', # War
                   '工部', # Works
                   '吏部', # Personnel
                   '刑部'  # Justice
                   ])

OFFICE='館'
offices = set(['國史館', # History
               '實録館', # Records
               '會典館', # Statutes
               '方畧館', # Planning
               '方略館', # Planning, synonym
               '馬館','馬？'    # Horses 
               ])

BUREAU='司'
bureaus = set(['文選司', # Appointments
               '考功司', # Evaluations
               '儀制司', # Ceremonies 
               '儀鳳司', # Music
               '屯田司', # Farms
               '武庫司', # Provisions
               '武選司', # Military Appointments
               '車駕司','車馬司','車鴐司',  # Military Communications
               '營繕司', # Encampment?
               '都水司', # Capital water?
               '驗封司','騐封司',   # Border inspector?
               '稽勳司','稽勲司','積勳司',      # Inspectors of merit?
               '職方司', # Duties?
               '虞衡司'  # Hunting? Prediction?
                ])

VICE_BUREAU_DIRECTOR='員外郎'
CAPITAL_OFFICIAL='京官'
SALT_CONTROLLER = '鹽運使司運同'

BANNER_SCHOOL='八旗官學'
raremgroffices = set(['溝渠河道會典館', # Canal Excavation
                      '界亭等處地方', # Jieting and surrounds, maybe
                      BANNER_SCHOOL + GRAND_MINISTER + '會典館'
                        # Office of the banner school records
                      ])

WENYUAN = '文淵閣'
halls =     set([ '體仁閣', 
                  '東閣',
                  WENYUAN,
                  '內閣'] ) 

HALL_LIT_PROFUNDITY = WENYUAN + '校理'
hall_membership = set([ HALL_LIT_PROFUNDITY ])

BANNER_SCHOOL='八旗官學'
schools= set([BANNER_SCHOOL])


# Role and organization can be same here
SURVEILLANCE_CIRCUIT='分巡'
MILITARY_SCIRCUIT='兵備道'
circuit_types = set([SURVEILLANCE_CIRCUIT,MILITARY_SCIRCUIT ] )
subcircuits = set(['湖南辰永沅靖',
                   '湖南辰沅永靖',
                   '迤東驛堡'] )  # Could break out province eg Hunan


ganzhi = ['庚寅','庚辰',
          '戊辰','辛未',
          '己丑',
          '丙戌','丙子',
          '癸未','丁丑','甲戌']

PROVINCIAL_TEMPS='司行走'

GUARD='侍衛'
METRO_COMMAND='侍衛司'
guards = set([GUARD,METRO_COMMAND,
             '頭等'+ GUARD,'御前'+GUARD])

PROVINCIAL_COMMANDER='提督'
regional_military = set([PROVINCIAL_COMMANDER])


SURV='分巡'
SURV2='題分巡'
surveillors=set([SURV,SURV2])

PETITIONER = '請旨'
petitioners = set([PETITIONER])

ROUTES = set(['山東等處',
              '江西通省',
              '湖北通省等處',
              '西乾鄜等處地方',
              '湖北通省等處地方'])
TRANSPORT_CONTROLLER = '督糧道'
TRANSPORT_CONTROLLER2 = '督粮道'
transportofficials = set([TRANSPORT_CONTROLLER,TRANSPORT_CONTROLLER2])

POLICE_OFFICES= set(['江村司','火井漕'])
POLICE_CHIEF = '巡檢'
POLICE_CHIEF2 = '巡検'

knownroles = []

knownroles += countyroles
knownroles += magistrates
knownroles += examiners
knownroles += educators
knownroles += students
knownroles += internships
knownroles += juniorroles
knownroles += midroles
knownroles += censors
knownroles += scholars
knownroles += seniorroles
knownroles += honours
knownroles += hall_membership
knownroles += palaceroles
knownroles += hanlin
knownroles += heiradmin
knownroles += heircompanions
knownroles += inspectors
knownroles += masters
knownroles += surveillors
knownroles += petitioners
knownroles += guards
knownroles += regional_military



role_synonyms = {}




def new_synonyms( new_synonym_list, knownroles=knownroles, 
                 role_synonyms=role_synonyms):
    nsd = dict(new_synonym_list)
    knownroles += nsd.keys()
    role_synonyms |= nsd
    return (knownroles,role_synonyms)


def export_roles(exportfname,encoding='utf-8'):
    with open(exportfname,'w',encoding=encoding,newline='') as outf:
        ew = csv.writer(outf)
        for role in knownroles:
            ew.writerow([role])


# students
role_synonyms |= {UPPER_STUDENT2: UPPER_STUDENT}

provincial_censors =  \
    [(CONTROLLER + province + '道'+ CENSOR,CENSOR)  \
                            for province in regions] + \
    [(CENSOR_INSPECTING + direction + '城' + province + '道'+ CENSOR,CENSOR)  \
                            for direction in directions \
                            for province in regions]  + \
    [(CENSOR_INSPECTING + direction + '城' + CONTROLLER + province + '道' \
                        + CENSOR,CENSOR)  \
                            for direction in directions \
                            for province in regions]  + \
    [(province + '道'+ CENSOR,CENSOR) \
                            for province in regions] 
known_roles, role_synonyms = new_synonyms(provincial_censors)

role_synonyms |= { CHIEF_CENSOR2: CHIEF_CENSOR }

provincial_examiners = \
    [ province + examiner for province in regions for examiner in examiners] 
role_synonyms |= dict([(province+examiner,examiner) 
                        for province in regions for examiner in examiners] )
role_synonyms |= {HEAVENLY_GENERAL_EXAMINER : GENERAL_EXAMINER}
knownroles += provincial_examiners
province_ec = [(province + FULL_PROVINCE + EDUCATION_COMMISSIONER, 
                EDUCATION_COMMISSIONER) for province in regions ]
knownroles, role_synonyms = new_synonyms(province_ec)

provincial_couriers = \
    [ (province + courier,courier) for province in regions 
                                   for courier in couriers]
known_roles, role_synonyms = new_synonyms(provincial_couriers)

role_synonyms |= {INSTRUCTOR2 : INSTRUCTOR,
                  INSTRUCTOR_PREFECTURE2: INSTRUCTOR_PREFECTURE} 

provincial_bachelors = [ province + HANLIN + BACHELOR for province in regions]
role_synonyms |= dict([(pb,BACHELOR) for pb in provincial_bachelors])
knownroles += provincial_bachelors + [BACHELOR+SERVICE]
role_synonyms |= {BACHELOR+SERVICE:BACHELOR}

ganzhi_bachelors =  [ gz + HANLIN + BACHELOR for gz in ganzhi]
ganzhi_bachelors += [ gz + '恩科' + HANLIN + BACHELOR for gz in ganzhi]
# print( "Ganzhi bachelors {}".format(ganzhi_bachelors) )
role_synonyms |= dict([(gb,BACHELOR) for gb in ganzhi_bachelors])
knownroles += ganzhi_bachelors

provincial_board_directors = [(BOARD_DIRECTOR + province + PROVINCIAL_TEMPS,
                              BOARD_DIRECTOR) for province in regions ]
knownroles, role_synonyms = new_synonyms(provincial_board_directors)


degreeorig = 'chushen_1_original'

zhuangyuan  = '狀元'    # 1st in jinshi exam (or perhaps some other exams)
bangyan     = '榜眼'    # 2nd
tanhua      = '探花'    # 3rd

topexam = set([zhuangyuan,bangyan,tanhua])
# topexam = set([zhuangyuan])

deptbaseroles=[ADMIN,CAPITAL_OFFICIAL,VICE_MINISTER,MINISTER]
deptroles = [department + role for department in departments \
                                for role in deptbaseroles]
deptroles += [department + role + SERVICE for department in departments \
                                for role in deptbaseroles]
role_synonyms |= dict([(department+role,role) \
                                for department in departments \
                                for role in deptbaseroles] )
role_synonyms |= dict([(department+role+SERVICE,role) \
                                for department in departments \
                                for role in deptbaseroles] )
knownroles += deptroles


managerroles = set([ADMIN,ADMIN2])
managers = [(MANAGER + department + role,MANAGER + role) \
                                        for department in departments \
                                        for role in managerroles ]
managers = [(MANAGER + office,MANAGER) for office in \
                (offices | raremgroffices | set([DIRECTORATE_EDUCATION]) ) ]
knownroles, role_synonyms = new_synonyms(managers)


provincial_bureau_baseroles = [SECRETARY,MINOR_CAPITAL_OFFICIAL,
                               VICE_BUREAU_DIRECTOR]
provincial_bureau_roles =  \
    [(role + province + BUREAU, role) \
        for province in regions \
        for role in provincial_bureau_baseroles ] + \
    [(role + province, role) \
        for province in regions \
        for role in provincial_bureau_baseroles ] + \
    [(role + province + BUREAU + CASUAL, role + CASUAL)  \
        for province in regions \
        for role in provincial_bureau_baseroles ] 
knownroles, role_synonyms = new_synonyms(provincial_bureau_roles)
knownroles += [VICE_BUREAU_DIRECTOR,VICE_BUREAU_DIRECTOR+CASUAL]


bureaubaseroles = [SECRETARY,BOARD_DIRECTOR,VICE_BUREAU_DIRECTOR,
                   MINOR_CAPITAL_OFFICIAL ]
bureauroles = [(SECRETARY + bureau,SECRETARY) for bureau in bureaus ] \
            + [(role + bureau + CASUAL,role + CASUAL) \
                    for bureau in bureaus \
                    for role in bureaubaseroles ]
knownroles, role_synonyms = new_synonyms(bureauroles)

saltroles = [SALT_CONTROLLER]
knownroles += saltroles

#senior
role_synonyms |= { ASSISTANT_GRAND_SECRETARY2: ASSISTANT_GRAND_SECRETARY,
                   ASSISTANT_GRAND_SECRETARY3: ASSISTANT_GRAND_SECRETARY,
                   ASSISTANT_GRAND_SECRETARY4: ASSISTANT_GRAND_SECRETARY,
                   MINISTER2: MINISTER,
                   GRAND_SECRETARY2: GRAND_SECRETARY}


# intern secretaries
intern_secs = [(SECRETARY + region + '司' + CASUAL,SECRETARY + CASUAL)  \
                    for region in regions ]
knownroles, role_synonyms = new_synonyms(intern_secs)

collegeroles = [DIRECTOR_STUDIES]
collegians = [ DIRECTORATE_EDUCATION + role for role in collegeroles ]
role_synonyms |= dict( [(DIRECTORATE_EDUCATION+role,role) 
                                       for role in collegeroles ] )
knownroles += collegians

recordsroles = [SCHOLAR,CHAIR,SENIOR_CHAIR,VICE_CHAIR,VICE_CHAIR_TEMP]
recofficials = [office + role for role in recordsroles 
                              for office in offices]
role_synonyms |= dict( [(office+role,role) for role in recordsroles
                                           for office in offices] )
knownroles += recofficials

classicsroles = [READER,DAY_OFFICIAL,DAY_READER]
classicists = [COLLOQ + role for role in classicsroles]
# synonymize? Check ranks first
knownroles += classicists

hallroles = [ACADEMICIAN,GRAND_SECRETARY]
hallofficials = [hall + role for hall in halls for role in hallroles]
role_synonyms |= dict([(hall + role,role) for hall in halls 
                                          for role in hallroles])
role_synonyms |= dict([(hall + GRAND_SECRETARY2,GRAND_SECRETARY) 
                                    for hall in halls ])
knownroles += hallofficials + [GRAND_SECRETARY2]

# role_synonyms |= {INSPECTOR_GIORO_ACADEMY2: INSPECTOR_GIORO_ACADEMY,
#                   GRAND_INSPECTOR_GRANARIES2: GRAND_INSPECTOR_GRANARIES}
role_synonyms |= dict( [(inspector, INSPECTOR) for inspector in inspectors  ] ) 

regional_censors = [(CONTROLLER + region + '道' + CENSOR,  
                     CENSOR ) for region in regions ]
knownroles, role_synonyms = new_synonyms(regional_censors)


# hanlin
role_synonyms |= { CHANCELLOR_HANLIN2: CHANCELLOR_HANLIN }

# masters
role_synonyms |= { CHIEF_SHIFU2: CHIEF_SHIFU } 

blue_ganzhi_guards =  [ BLUE_FEATHER + GUARD + gz + CLASS for gz in ganzhi ]
role_synonyms |= dict([(gg,BLUE_FEATHER+GUARD) for gg in blue_ganzhi_guards])
flower_ganzhi_guards = [ FLOWER_FEATHER + GUARD + gz + CLASS for gz in ganzhi ]
role_synonyms |= dict([(gg,FLOWER_FEATHER+GUARD) 
                        for gg in flower_ganzhi_guards])
knownroles += blue_ganzhi_guards + flower_ganzhi_guards

provincial_military = [province + rank for province in regions
                                       for rank in regional_military ]
knownroles += provincial_military
role_synonyms |= dict([(province + rank,rank) for province in regions
                                              for rank in regional_military ] )


circuit_surveillors = [(surv+circuit+circuit_type,surv) \
                            for surv in surveillors \
                            for circuit in subcircuits \
                            for circuit_type in circuit_types]
knownroles, role_synonyms = new_synonyms(circuit_surveillors)

transportroles = [(route + role,TRANSPORT_CONTROLLER) \
                        for role in transportofficials \
                        for route in ROUTES ]
knownroles, role_synonyms = new_synonyms(transportroles)


police = [(POLICE_CHIEF2,POLICE_CHIEF)] + \
         [(office + POLICE_CHIEF,POLICE_CHIEF) for office in POLICE_OFFICES] + \
         [(office + POLICE_CHIEF2,POLICE_CHIEF)  \
                    for office in POLICE_OFFICES] 
knownroles, role_synonyms = new_synonyms(police)
knownroles += [POLICE_CHIEF]


# Spring court of the Heir Apparent
role_synonyms |= {SPRINGC_ADMONISHER: ADMONISHER,
                  '春坊贊善銜': ADMONISHER, 
                  SPRINGC_HEIR: COMPANION_HEIR,
                  '春坊中允銜': COMPANION_HEIR }

role_synonyms |= { '翰林院编修':   JUNIOR_COMPILER, # Hanlin roles
                  '翰林院編修':   JUNIOR_COMPILER,
                  JUNIOR_COMPILER2: JUNIOR_COMPILER,
                  '翰林院修撰':   '修撰',
                  '翰林院庶吉士': '庶吉士',
                  '翰林院侍讀': '侍讀',
                  '翰林院侍講': '侍講',
                  '內閣學士': CABINET_ACADEMICIAN,
                  VICE_CHAIR_RECORDS2: VICE_CHAIR_RECORDS,
                  '吉士': '庶吉士',
                  INSTRUCTOR2 : INSTRUCTOR, 
                  '翰林院檢討':   '檢討',
                  '翰林院撿討':   '檢討',   # transcription 檢
                  '翰林院編檢討': '編檢討', # 'bianjiantao'
                  '翰林院庶吉士庚辰科': '院庶吉士', # ganzhi variant  
                  # Military
                  '撫標中軍叅將': '叅將', # Staff captain
                  '漕標中軍副將': '副將', # Brigadier / fujiang
                  '督標中軍副將': '副將'
                  }

NO_RANK = 'no-rank'
rank_defaults = {'Unassigned/missing': NO_RANK,
                 'Not guanzhi': NO_RANK,  
                 'None': NO_RANK,
                 '未入流': NO_RANK}



rs = role_synonyms.copy(); rs.pop('吉士',None)
knownroles += list(rs.keys())




if __name__ == '__main__':
    export_roles('role.csv')

