import unittest

from pm.pmmodels.tracefreq import *
from pm.metrics.earthmovers import *

ss = frozenset




# From Alkhammash paper
ltf_e1 = TraceFrequency(  
              { ('a','b'): 1200, ('a','e'): 300, ('a','b','c','d'): 220, 
                ('a','b','c'): 100, ('a','e','e'): 100, 
                ('a','b','c','d','e'): 80 }  )

ltf_e2 = TraceFrequency(  
              { ():50, ('a','b'): 50, ('a','b','c'): 50, 
                ('a','e','a','a','e'): 40, ('a','e','e'): 20, 
                ('a','b','c','d'): 10, ('a','b','c','d','e'): 10,
                ('a','b','e','e'): 10, ('a','b','c','f','f'): 10 }  )

mtf_a1 = TraceFrequency(
              { ('a','b'): 160, ('a','b','c'):20, ('a','b','c','d'):45,
                ('a','b','c','d','e'):15, ('a','b','f'):80, ('a','e'):60,
                ('a','e','e'):20 } )

mtf_a2 = TraceFrequency(
              { (): 256, ('a'): 384, ('a','b'):192, ('a','b','c'): 48,
                ('a','b','c','f'):12,
                ('a','b','c','f','f'):3, ('a','b','e'):96, 
                ('a','b','c','f','d'):3, ('a','b','c','d'):12,
                ('a','b','c','d','e'):12, 
                ('a','b','c','f','d','e'):3, 
                ('null'):3 } )

# Local for rolesets
ltf_se1 = RoleTraceFrequency(  
              { (ss(['a']) ): 20, 
                (ss(['a']), ss(['a','b'])): 10 } )

ltf_se2 = RoleTraceFrequency(
              { (ss(['I']),ss(['A']),ss(['F'])): 20,     
                (ss(['I']),ss(['A','B']),ss(['F'])): 10,
                (ss(['I']),ss(['B']),ss(['B','A']),ss(['F'])): 10
               } )

mtf_sa1 = RoleTraceFrequency(
              { (ss(['a','b'])): 20,     
                (ss(['a']), ss(['a','b'])): 10 } )

mtf_sa2 = RoleTraceFrequency(
              { (ss(['I']),ss(['A']),ss(['F'])): 250,     
                (ss(['I']),ss(['B']),ss(['F'])): 250,     
                (ss(['I']),ss(['A','B']),ss(['F'])): 500     
               })





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





