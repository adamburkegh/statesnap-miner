

from pm.pmmodels.plpn import *
from pm.ssnap.ssmetrics import *

from tests.pm.pmmodels.pnfragutil import *


ss = frozenset

class MetricsTest(PetriNetTestCase):

    def test_enclose_trace(self):
        iset = ss(['I'])
        fset = ss(['F'])
        self.assertEqual( (iset, ss(['A']), fset), 
                          enclose_trace( (ss(['A']),), iset, fset ) )

    def test_enclose_traces(self):
        log = { (ss(['A']), ): 20,
                (ss(['A']), ss(['A','B'])): 10 }
        elog ={ (ss(['I']), ss(['A']), ss(['F']) ): 20,
                (ss(['I']), ss(['A']), ss(['A','B']), ss(['F']) ): 10 }
        self.assertEqual(elog, enclose_traces(log))

    def test_relevance_choice_equal(self):
        log = { (ss(['A']), ): 20,
                (ss(['B']), ): 10 }
        net = self.net("I -> {tau__1 20.0} -> A -> {tau__2 20.0} -> F")
        self.add(net,  "I -> {tau__3 10.0} -> B -> {tau__4 10.0} -> F ")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        # selector_cost == 0            full coverage
        # trace_compression_cost == 1/30 * 
        #                               20 * -1 * log_2(666/1000)   {A}
        #                               10 * -1 * log_2(334/1000)   {B} 
        self.assertAlmostEqual(0.91829727578, 
                               entropic_relevance(log,net,imark) )

    @unittest.skip("revisit with new roleset termination semantics")
    def test_relevance_multi_terminal(self):
        log = { (ss(['A']) ): 20,
                (ss(['A']), ss(['A','B'])): 10 }
        net = self.net("I -> {tau__1 20.0} -> A -> {tau__2 20.0} -> F")
        self.add(net,  "I -> {tau__1 20.0} -> B -> {tau__2 20.0} -> F ")
        self.add(net,  "I -> {tau__3 10.0} -> A -> {tau__4 10.0} -> F ")
        self.add(net,  "I -> {tau__5 10.0} -> B -> {tau__6 10.0} -> F ")
        pi = findPlace(net,"I")
        print(net)
        imark = singleton_marking(net, [pi])
        # incorrect expected value
        self.assertEqual(0, entropic_relevance(log,net,imark) )

