import unittest

from pmkoalas.models.pnfrag import *
from pmmodels.plpn import *


def findPlace(net,label):
    """
    Return first node with this label
    """
    for place in net._places:
        if label == place.name:
            return place


def findTran(net,label):
    """
    Return first node with this label
    """
    for tran in net._transitions:
        if label == tran.name:
            return tran




class PTNetSemanticsTest(unittest.TestCase):
    def setUp(self):
        self.parser = PetriNetFragmentParser()

    def test_single_sequence(self):
        net = BuildablePetriNet("single_seq")
        self.parser.add_to_net(net, "I -> [a] -> F")
        initial = findPlace(net,"I")
        final = findPlace(net,"F")
        atran = findTran(net,"a")
        iMarking = singleton_marking(net, [initial])
        fMarking = singleton_marking(net, [final])
        sem = PetriNetSemantics(iMarking)
        self.assertEqual( set([atran]), sem.enabled() ) 
        post = sem.remark(atran)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_two_choice(self):
        pi = Place("I")
        pf = Place("F")
        ta = Transition("a")
        tb = Transition("b")
        net = LabelledPetriNet([pi,pf],[ta,tb],  
                               [Arc(pi,ta), Arc(pi,tb),
                                Arc(ta,pf), Arc(tb,pf)],
                               "two_choice")
        iMarking = singleton_marking(net, [pi])
        fMarking = singleton_marking(net, [pf])
        sem = PetriNetSemantics(iMarking)
        self.assertEqual( set([ta,tb]), sem.enabled() ) 
        post = sem.remark(ta)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_three_choice(self):
        pi = Place("I")
        pf = Place("F")
        ta = Transition("a")
        tb = Transition("b")
        tc = Transition("c")
        net = LabelledPetriNet([pi,pf],[ta,tb,tc],  
                               [Arc(pi,ta), Arc(pi,tb), Arc(pi,tc),
                                Arc(ta,pf), Arc(tb,pf), Arc(tc,pf)],
                               "three_choice")
        iMarking = singleton_marking(net, [pi])
        fMarking = singleton_marking(net, [pf])
        sem = PetriNetSemantics(iMarking)
        self.assertEqual( set([ta,tb,tc]), sem.enabled() ) 
        post = sem.remark(tc)
        self.assertEqual( set([]), sem.enabled() ) 
        self.assertEqual( fMarking, post )

    def test_concurrency(self):
        pi = Place("I")
        p1 = Place("p1")
        p2 = Place("p2")
        pf = Place("F")
        ta = Transition("a")
        tb = Transition("b")
        net = LabelledPetriNet([pi,p1,p2,pf],[ta,tb],  
                               [Arc(pi,ta), 
                                Arc(ta,p1), Arc(ta,p2),
                                Arc(p1,tb), Arc(p2,tb),
                                Arc(tb,pf)],
                               "two_choice")
        iMarking = singleton_marking(net, [pi])
        marking1 = singleton_marking(net, [p1,p2])
        fMarking = singleton_marking(net, [pf])
        sem = PetriNetSemantics(iMarking)
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



