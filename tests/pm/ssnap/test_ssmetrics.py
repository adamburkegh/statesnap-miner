

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
                               entropic_relevance_plpn(log,net,imark) )
        rsnet = to_rsnet(net)
        rsmark = singleton_marking(rsnet, [pi])
        self.assertAlmostEqual(0.91829727578, 
                               entropic_relevance_rsnet(log,rsnet,rsmark) )
        self.assertAlmostEqual(0.91829727578, 
                               entropic_relevance(log,rsnet,rsmark) )

    def test_relevance_multi_terminal(self):
        log = { (ss(['A']) ,): 20,
                (ss(['A','B']) ,): 10,
                (ss(['B']), ss(['A','B']) ): 10,
               }
        net = self.net("I -> {tau__1 20.0} -> A -> {tau__2 20.0} -> F")
        self.add(net,  "I -> {tau__1 20.0} -> B -> {tau__2 20.0} -> F ")
        self.add(net,  "I -> {tau__3 10.0} -> A -> {tau__4 10.0} -> F ")
        self.add(net,  "I -> {tau__5 10.0} -> B -> {tau__6 10.0} -> F ")
        net = to_rsnet(net)
        # First two log traces fit model, third doesn't
        pi = findPlace(net,"I")
        trans = {}
        for tid in range(1,7):
            tran = findTransitionById(net, tid)
            trans[tid] = tran
        for tid in [2,4,6]:
            trans[tid].picky = True
        imark = singleton_marking(net, [pi])
        # log traces == 40
        # selector_cost == 
        #       lsum == 30; rho == 30/40
        #       == -1 * 3/4 * log2(3/4) + (1/4)* log2(1/4) 
        #       == 0.8112781244591328 
        # trace_compression_cost == 
        #       1/40 * 
        #          20 * -1 * log2(1/4)          == 40  {I},{A},{F}
        #          10 * -1 * log2(1/2)          == 10  {I},{A,B},{F}
        #          10 * 4 * log2(2**4+1)        == 163.49851365001356 
        #                                              {I},{B},{F}
        # This calculation is also in test_ssmetrics.test_local_eg_SA2_SE2()
        self.assertAlmostEqual( 7.170606676022, 
                               entropic_relevance(log,net,imark) )



