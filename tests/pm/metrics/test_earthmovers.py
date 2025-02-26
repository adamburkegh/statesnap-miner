import unittest

from pm.pmmodels.tracefreq import *
from pm.metrics.earthmovers import *

ss = frozenset



ltf_e1 = TraceFrequency(  
              { ('a','b'): 1200, ('a','e'): 300, ('a','b','c','d'): 220, 
                ('a','b','c'): 100, ('a','e','e'): 100, 
                ('a','b','c','d','e'): 80 }  )


# Local for rolesets
ltf_se1 = RoleTraceFrequency(  
              { (ss(['a']) ): 20, 
                (ss(['a']), ss(['a','b'])): 10 } )

mtf_sa1 = RoleTraceFrequency(
              { (ss(['a','b'])): 20,     
                (ss(['a']), ss(['a','b'])): 10 } ) 





class UnitEarthMoversTest(unittest.TestCase):

    def test_identical(self):
        ltf = TraceFrequency( { 'a': 1, 'ba': 7 } )
        self.assertAlmostEqual(1, unit_earthmovers(ltf,ltf) )
        self.assertAlmostEqual(1, unit_earthmovers(mtf_sa1,mtf_sa1) )
    
    def test_zero(self):
        tf1 = TraceFrequency( { 'a': 1, 'ba': 7 } )
        tf2 = TraceFrequency( { 'cd': 1, 'e': 7 } )
        self.assertAlmostEqual(0, unit_earthmovers(tf1,tf2) )

    def test_partial(self):
        tf1 = TraceFrequency( { 'a': 1, 'ba': 7 } )
        tf2 = TraceFrequency( { 'a': 1, 'c': 7 } )
        self.assertAlmostEqual(0.125, unit_earthmovers(tf1,tf2) )

    def test_roleset(self):
        self.assertAlmostEqual(1/3, unit_earthmovers(ltf_se1,mtf_sa1) )





