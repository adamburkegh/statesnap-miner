
'''
Take the tails of each trace in a log after a specific role occurs
(here county magistrates).
'''

import logging
import os

logger = logging.getLogger( __name__ )

from cgedq.logutil import *
from pm.ssnap.ssnap import (sslogWithRanges, sslogToCSV, filter_by_role, 
                            keep_top_roles, take_tails)

def magcount(logfile):
    info(f"Loading ... {logfile}" )
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    info(len(sslog))


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


def magintendanttails(logfile,newlogpath):
    info(f"Loading ... {logfile}" )
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    tailslog = take_tails(sslog,'知縣',2)
    tailslog = filter_by_role(tailslog,'分巡')
    sslogToCSV(tailslog,newlogpath,caseIdCol='person_id',activityCol='synjob',
               timeCol='year')
    info(f"Output written to ... {newlogpath}")


def magintendanttailstop(logfile,newlogpath):
    info(f"Loading ... {logfile}" )
    sslog = sslogWithRanges(logfile,
                         caseIdCol='person_id',activityCol='synjob',
                         timeColStart='start_year',timeColEnd='end_year',
                         types = {'start_year':float,'end_year':float  },
                         keepSuccDupes=False)
    tailslog = take_tails(sslog,'知縣',2)
    tailslog = filter_by_role(tailslog,'分巡')
    tailslog = keep_top_roles(tailslog, 7, drop=True) 
    sslogToCSV(tailslog,newlogpath,caseIdCol='person_id',activityCol='synjob',
               timeCol='year')
    info(f"Output written to ... {newlogpath}")


if __name__ == '__main__':
    fname = 'var/cged-q-jmagfull.csv'
    ftail = 'var/cged-q-jmagtails.csv'
    magtails('知縣',fname,ftail)
    # magintendanttails(fname,'var/cged-q-jmagintend.csv')
    # magintendanttailstop(fname,
    #                      'var/cged-q-jmagintendtop.csv')
    # magcount(fname)



