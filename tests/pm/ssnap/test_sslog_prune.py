import unittest

from pm.ssnap.ssnap import  *


class StateSnapshotLogTest(unittest.TestCase):

    def test_sstrace_to_variant(self):
        trace =  [ StateSnapshot(1,1700, set(['Student'])),
                   StateSnapshot(1,1701, set(['Sweep']))]
        expected = ( set(['Student']),set(['Sweep']) )
        result = sstrace_to_variant(trace)
        self.assertEqual(expected,result)


    def test_noise_reduce_no_reduction(self):
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ],
                 2: [ StateSnapshot(2,1701,
                                    set(['Sweep']) ) ] ,
                 3: [ StateSnapshot(3,1705,
                                    set(['Sweep']) ) ],
                 4: [ StateSnapshot(4,1701,
                                    set(['Sweep']) ) ] }
        result = noiseReduceByVariant(sslog,0.1)
        self.assertEqual(sslog,result)

    def test_noise_reduce_reduction(self):
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ],
                 2: [ StateSnapshot(2,1701,
                                    set(['Sweep']) ) ] ,
                 3: [ StateSnapshot(3,1705,
                                    set(['Sweep']) ) ],
                 4: [ StateSnapshot(4,1701,
                                    set(['Sweep']) ) ] }
        result = noiseReduceByVariant(sslog,0.3)
        expected = {2: [ StateSnapshot(2,1701,
                                    set(['Sweep']) ) ] ,
                 3: [ StateSnapshot(3,1705,
                                    set(['Sweep']) ) ],
                 4: [ StateSnapshot(4,1701,
                                    set(['Sweep']) ) ] }
        self.assertEqual(expected,result)


