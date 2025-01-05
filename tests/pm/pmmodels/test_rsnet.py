import unittest

from pm.pmmodels.plpn import *
from pm.pmmodels.rsnet import *




class RoleStateNetSemanticsTest(unittest.TestCase):
    def test_single_sequence(self):
        initial = Place("I")
        final = Place("F")
        atran = RSTransition("a")
        net = LabelledPetriNet([initial,final],[atran],
                               [Arc(initial,atran),Arc(atran,final)],
                               "single_seq")
        iMarking = singleton_marking(net, [initial])
        fMarking = singleton_marking(net, [final])
        sem = RoleStateNetSemantics(iMarking)
        self.assertEqual( set([atran]), sem.enabled() ) 
        post = sem.remark(atran)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_single_sequence_marked(self):
        initial = Place("I")
        final = Place("F")
        atran = RSTransition("a")
        net = LabelledPetriNet([initial,final],[atran],
                               [Arc(initial,atran),Arc(atran,final)],
                               "single_seq")
        marking = singleton_marking(net, [initial,final])
        sem = RoleStateNetSemantics(marking)
        self.assertEqual( set([]), sem.enabled() ) 

    def test_two_choice(self):
        pi = Place("I")
        pf = Place("F")
        ta = RSTransition("a")
        tb = RSTransition("b")
        net = LabelledPetriNet([pi,pf],[ta,tb],  
                               [Arc(pi,ta), Arc(pi,tb),
                                Arc(ta,pf), Arc(tb,pf)],
                               "two_choice")
        iMarking = singleton_marking(net, [pi])
        fMarking = singleton_marking(net, [pf])
        sem = RoleStateNetSemantics(iMarking)
        self.assertEqual( set([ta,tb]), sem.enabled() ) 
        post = sem.remark(ta)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )


    def test_two_choice_one_picky(self):
        pi = Place("I")
        pf = Place("F")
        ta = RSTransition("a")
        tb = RSTransition("b",pickyt=True)
        net = LabelledPetriNet([pi,pf],[ta,tb],  
                               [Arc(pi,ta), Arc(pi,tb),
                                Arc(ta,pf), Arc(tb,pf)],
                               "two_choice_one_picky")
        iMarking = singleton_marking(net, [pi])
        fMarking = singleton_marking(net, [pf])
        sem = RoleStateNetSemantics(iMarking)
        self.assertEqual( set([ta,tb]), sem.enabled() ) 
        post = sem.remark(ta)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_three_choice(self):
        pi = Place("I")
        pf = Place("F")
        ta = RSTransition("a")
        tb = RSTransition("b")
        tc = RSTransition("c")
        net = LabelledPetriNet([pi,pf],[ta,tb,tc],  
                               [Arc(pi,ta), Arc(pi,tb), Arc(pi,tc),
                                Arc(ta,pf), Arc(tb,pf), Arc(tc,pf)],
                               "three_choice")
        iMarking = singleton_marking(net, [pi])
        fMarking = singleton_marking(net, [pf])
        sem = RoleStateNetSemantics(iMarking)
        self.assertEqual( set([ta,tb,tc]), sem.enabled() ) 
        post = sem.remark(tc)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_concurrency(self):
        pi = Place("I")
        p1 = Place("p1")
        p2 = Place("p2")
        pf = Place("F")
        ta = RSTransition("a")
        tb = RSTransition("b")
        net = LabelledPetriNet([pi,p1,p2,pf],[ta,tb],  
                               [Arc(pi,ta), 
                                Arc(ta,p1), Arc(ta,p2),
                                Arc(p1,tb), Arc(p2,tb),
                                Arc(tb,pf)],
                               "conc")
        iMarking = singleton_marking(net, [pi])
        marking1 = singleton_marking(net, [p1,p2])
        fMarking = singleton_marking(net, [pf])
        sem = RoleStateNetSemantics(iMarking)
        self.assertEqual( set([ta]), sem.enabled() ) 
        try:
            sem.remark(tb)
            self.fail("Should not be able to fire disabled transition")
        except ValueError:
            None
        post = sem.remark(ta)
        self.assertEqual( marking1, post) 
        self.assertEqual( set([tb]), sem.enabled() ) 
        post = sem.remark(tb)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )


    def test_concurrency_marked(self):
        pi = Place("I")
        p1 = Place("p1")
        p2 = Place("p2")
        pf = Place("F")
        ta = RSTransition("a")
        tb = RSTransition("b")
        net = LabelledPetriNet([pi,p1,p2,pf],[ta,tb],  
                               [Arc(pi,ta), 
                                Arc(ta,p1), Arc(ta,p2),
                                Arc(p1,tb), Arc(p2,tb),
                                Arc(tb,pf)],
                               "conc")
        marking1 = singleton_marking(net, [pi,p1])
        sem = RoleStateNetSemantics(marking1)
        self.assertEqual( set([]), sem.enabled() ) 

    def test_concurrency_marked_block(self):
        pi = Place("I","pi")
        p1 = Place("p1","p1")
        p2 = Place("p2","p2")
        p3 = Place("p3","p3")
        p4 = Place("p4","p4")
        pf = Place("F","pf")
        ta = RSTransition("a")
        tb = RSTransition("b")
        tc = RSTransition("c")
        td = RSTransition("d")
        net = LabelledPetriNet([pi,p1,p2,p3,p4,pf],[ta,tb,tc,td],  
                               [Arc(pi,ta), 
                                Arc(ta,p1), Arc(ta,p3),
                                Arc(p1,tb), Arc(tb,p2),
                                Arc(p3,tc), Arc(tc,p3),
                                Arc(p2,td), Arc(p4,td),
                                Arc(td,pf)],
                               "conc-block")
        marking1 = singleton_marking(net, [p1,p3])
        sem = RoleStateNetSemantics(marking1)
        self.assertEqual( set([tb,tc]), sem.enabled() ) 


    def test_concurrency_marked_picky(self):
        pi = Place("I","pi")
        p1 = Place("p1","p1")
        p2 = Place("p2","p2")
        p3 = Place("p3","p3")
        p4 = Place("p4","p4")
        pf = Place("F","pf")
        ta = RSTransition("a")
        tb = RSTransition("b")
        tc = RSTransition("c",True)
        td = RSTransition("d")
        net = LabelledPetriNet([pi,p1,p2,p3,p4,pf],[ta,tb,tc,td],  
                               [Arc(pi,ta), 
                                Arc(ta,p1), Arc(ta,p3),
                                Arc(p1,tb), Arc(tb,p2),
                                Arc(p3,tc), Arc(tc,p3),
                                Arc(p2,td), Arc(p4,td),
                                Arc(td,pf)],
                               "conc-block-picky")
        marking1 = singleton_marking(net, [p1,p3])
        sem = RoleStateNetSemantics(marking1)
        self.assertEqual( set([tb]), sem.enabled() ) 

    def test_sequence_with_escape_routes(self):
        pi = Place("I","pi")
        p1 = Place("p1","p1")
        p2 = Place("p2","p2")
        pf = Place("F","pf")
        ta = RSTransition("a")
        tb = RSTransition("b")
        t_pc = RSTransition("p_c",True)
        t_pd = RSTransition("p_d",True)
        net = LabelledPetriNet([pi,p1,p2,pf],[ta,tb,t_pc,t_pd],  
                               [Arc(pi,ta), Arc(ta,p1), Arc(p1,tb), Arc(tb,p2),
                                Arc(p1,t_pc), Arc(t_pc,pf),
                                Arc(p2,t_pd), Arc(t_pd,pf)],
                               "seq-escape")
        marking1 = singleton_marking(net, [pi])
        sem = RoleStateNetSemantics(marking1)
        self.assertEqual( set([ta]), sem.enabled() ) 
        sem.remark(ta)
        marking2 = singleton_marking(net, [p1])
        sem = RoleStateNetSemantics(marking2)
        self.assertEqual( set([tb,t_pc]), sem.enabled() ) 
        fmarking = sem.remark(t_pc)
        self.assertEqual( set([pf]), set(fmarking.mark.keys()) ) 


