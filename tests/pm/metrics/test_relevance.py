import unittest

from pm.metrics.relevance import *

ss = frozenset



class TraceFrequencyTest(unittest.TestCase):

    def test_simple(self):
        mtf = TraceFrequency( { 'a': 2, 'b': 3 } )
        self.assertEqual( 2, mtf.freq('a') )
        self.assertEqual( 0, mtf.freq('No such') )
        self.assertEqual( 5, mtf.trace_total() )
        self.assertEqual( 2, mtf.role_total() )


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





class EntropicRelevanceTest(unittest.TestCase):

    def test_model_cost_error(self):
        mtf = TraceFrequency( { 'a': 2 } )
        self.assertRaises( ValueError, model_cost, mtf, ( 'no such' ) )

    def test_model_cost_strings(self):
        mtf = TraceFrequency( { 'a': 1, 'ba': 7 } )
        self.assertEqual( 3, model_cost( mtf, 'a' ) )

    def test_uniform_background_cost_rolesets(self):
        ltf = TraceFrequency( { 'a': 1, 'ba': 7 } )
        self.assertAlmostEqual( 4.6438562, 
                               uniform_role_background_cost( ltf, 'c' ) )

    def test_uniform_background_cost_strings(self):
        ltf = TraceFrequency( { 'a': 1, 'ba': 7 } )
        self.assertAlmostEqual( 3.169925,
                               uniform_background_cost( ltf, 'c' ) )

    def test_paper_eg_A1_E1(self):
        self.assertAlmostEqual( 2.17209347, relevance_uniform(ltf_e1,mtf_a1) )
        self.assertAlmostEqual( 0.0, selector_cost(ltf_e1,mtf_a1) )

    def test_paper_eg_A1_E1_roleset(self):
        self.assertAlmostEqual( 2.17209347,
                                relevance_uniform_roleset(ltf_e1,mtf_a1) )

    def test_paper_eg_A2_E1(self):
        self.assertAlmostEqual( 4.3122556, 
                                trace_compression_cost(ltf_e1,mtf_a2,
                                                       uniform_background_cost))
        self.assertAlmostEqual( 5.0341837, 
                                relevance_uniform(ltf_e1,mtf_a2) )
        self.assertAlmostEqual( 0.7219281, selector_cost(ltf_e1,mtf_a2) )

    def test_paper_eg_A1_E2(self):
        self.assertAlmostEqual( 7.2714396,
                                relevance_uniform(ltf_e2,mtf_a1) )
        self.assertAlmostEqual( 0.9895875, selector_cost(ltf_e2,mtf_a1) )

    def test_paper_eg_A1_E2_roleset(self):
        self.assertAlmostEqual( 0.9895875, selector_cost(ltf_e2,mtf_a1) )
        self.assertAlmostEqual( 12.4154603,
                                relevance_uniform_roleset(ltf_e2,mtf_a1) )

    def test_paper_eg_A2_E2(self):
        self.assertAlmostEqual( 7.62615559,
                                relevance_uniform(ltf_e2,mtf_a2))
        self.assertAlmostEqual( 0.85545081, selector_cost(ltf_e2,mtf_a2) )

    def test_local_eg_SA1_SE1(self):
        self.assertAlmostEqual( 4.54252079,
                                relevance_uniform_roleset(ltf_se1,mtf_sa1))
        self.assertAlmostEqual( 0.9182958, selector_cost(ltf_se1,mtf_sa1) )

    def test_local_eg_SA2_SE2(self):
        self.assertAlmostEqual( 0.8112781244591328, 
                               selector_cost(ltf_se2,mtf_sa2) )
        self.assertAlmostEqual( 7.170606676022,
                                relevance_uniform_roleset(ltf_se2,mtf_sa2))

    def show_model_cost_output(self):
        # show_model_cost(mtf_a1,'MTF A1')
        # show_model_cost(mtf_sa1,'MTF SA1')
        # show_model_cost(ltf_e2,'LTF E2')
        show_model_cost(mtf_sa2,'MTF SA2')




