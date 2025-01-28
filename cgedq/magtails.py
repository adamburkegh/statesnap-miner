
'''
Take the tails of each trace in a log after a specific role occurs
(here county magistrates).
'''

import logging
import os

logger = logging.getLogger( __name__ )

from cgedq.logutil import *
from pm.ssnap.ssnap import sslogWithRanges, sslogToCSV, take_tails

def magtails(role,logfile,newlogpath):
    info(f"Loading ... {logfile}" )
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    tailslog = take_tails(sslog,role,2)
    sslogToCSV(tailslog,newlogpath,caseIdCol='person_id',activityCol='synjob',
               timeCol='year')
    info(f"Output written to ... {newlogpath}")


if __name__ == '__main__':
    fname = 'var/cged-q-jmagistrate.csv'
    ftail = 'var/cged-q-jmagtails.csv'
    magtails('知縣',fname,ftail)



