
import os
import unittest

from pm.logs.statesnaplog import *
from tests.pm import ssnap as tssnap

mpath = os.path.abspath(tssnap.__path__[0])

class StateSnapshotLogTest(unittest.TestCase):

    def test_sslog_from_csv(self):
        expected = \
            {1: [ StateSnapshot(1,1801,
                        set(['Student'])) ,
                  StateSnapshot(1,1802,
                                set(['Student']) ),
                  StateSnapshot(1,1803,
                                set(['Student']) ),
                  StateSnapshot(1,1804,
                                set(['Student']) ),
                  StateSnapshot(1,1805,
                                set(['Drone']) )],
             2: [ StateSnapshot(2,1801,
                                set(['Student','Tutor']) ),
                  StateSnapshot(2,1805,
                                set(['Bludger']) )] }
        cf = os.path.join(mpath,'test_ssnap_log1.csv')
        sslog = sslogFromCSV(cf, 'personid','job','year',
                             types={'personid': int, 'year':int } )
        self.assertEqual( expected, sslog )


    def test_sslog_from_csv_range(self):
        expected = \
            { 1:[ StateSnapshot(1,1801,
                                 set(['Student'])) ,
                   StateSnapshot(1,1802,
                                 set(['Student']) ),
                   StateSnapshot(1,1803,
                                 set(['Student']) ),
                   StateSnapshot(1,1804,
                                 set(['Student']) ),
                   StateSnapshot(1,1805,
                                 set(['Drone']) )],
              2:[ StateSnapshot(2,1801,
                                set(['Student']) ),
                  StateSnapshot(2,1802,
                                    set(['Student','Tutor']) ),
                  StateSnapshot(2,1803,
                                set(['Student','Tutor']) ),
                  StateSnapshot(2,1804,
                                set(['Student','Tutor']) ),
                  StateSnapshot(2,1805,
                                set(['Bludger']) ),
                  StateSnapshot(2,1806,
                                set(['Bludger']) ),
                  StateSnapshot(2,1807,
                                set(['Bludger']) ) ] }
        cf = os.path.join(mpath,'test_ssnap_log_range.csv')
        sslog = sslogWithRanges(cf, 'personid','job','yearStart','yearEnd',
                timeInc=1,
                types={'personid': int, 'yearStart':float, 'yearEnd':float })
        self.assertEqual( expected, sslog )

    def test_sslog_from_csv_rm_succ_dupes(self):
        expected = \
            {1: [ StateSnapshot(1,1801,
                                set(['Student'])) ,
                  StateSnapshot(1,1805,
                                set(['Drone']) )],
             2: [ StateSnapshot(2,1801,
                                set(['Student','Tutor']) ),
                  StateSnapshot(2,1805,
                                set(['Bludger']) ) ] }
        cf = os.path.join(mpath,'test_ssnap_log1.csv')
        sslog = sslogFromCSV(cf, 'personid','job','year',
                             types={'personid': int, 'year':int },
                             keepSuccDupes=False)
        self.assertEqual( expected, sslog )


