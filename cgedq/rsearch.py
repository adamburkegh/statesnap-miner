
'''
Take the tails of each trace in a log after a specific role occurs
(here county magistrates).
'''

import logging
import os

logger = logging.getLogger( __name__ )

from cgedq.logutil import *
from pm.ssnap.ssnap import (sslogWithRanges, sslogToCSV, filter_by_roleset) 


def rsearch(logfile,newlogpath):
    info(f"Loading ... {logfile}" )
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    slog = filter_by_roleset(sslog,['知縣','知州'])
    sslogToCSV(slog,newlogpath,caseIdCol='person_id',activityCol='synjob',
               timeCol='year')
    info(f"Output written to ... {newlogpath}")



if __name__ == '__main__':
    fname = 'var/cged-q-jmagistrate.csv'
    fout = 'var/cged-q-jmagdept.csv'
    #magtails('知縣',fname,ftail)
    # magintendanttails(fname,'var/cged-q-jmagintend.csv')
    rsearch(fname, fout)



