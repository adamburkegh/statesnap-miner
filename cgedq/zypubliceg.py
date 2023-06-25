'''
Example using the state snapshot miner on publicly released 1850-1864 data for
Tier 1 officials.
'''

import ssnap.ssnap as snapminer
from cgedq.mine import mineByTime
from pmmodels.pnformatter import exportNetToScaledImage

logfile = 'data/cged-q-zyjtnall_1850-1864.csv'

sslog = snapminer.sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)

of = 'zypublic'
pn = mineByTime('.',of,sslog,years=3)

sslogeng = snapminer.sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob_eng',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)

of = 'zypubliceng'
pn = mineByTime('.',of,sslogeng,years=3,font='Times-Roman')

print('Done.')

