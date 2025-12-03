
import logging
import sys
import unittest

from pmkoalas.models.pnfrag import *

from pm.pmmodels.conform import reachable_markings
from pm.pmmodels.plpn import Marking
from pm.pmmodels.rsnet import RoleStateNetSemantics, to_rsnet

from tests.pm.pmmodels.pnfragutil import *
from tests.pm.logutil import log_to_stdout


logger = logging.getLogger()
log_to_stdout()


def place_tuple_key(pt):
    place, val = pt
    return  (place.name,place.pid,val) 

def sort_place_tuple_seq(ptl):
    result = []
    for entry in sorted(ptl,key=place_tuple_key):
        result.append(  place_tuple_key(entry) )
    return result

class ReachabilityTest(unittest.TestCase):

    def setUp(self):
        self.parser = PetriNetFragmentParser()

    def net(self,netText,label=None):
        lb = "reachtest"
        if label:
            lb = label
        return self.parser.create_net(lb,netText)

    def add(self,net,netText):
        return self.parser.add_to_net(net,netText)

    def assertMarkingsEqual(self,p1,p2):
        r1 = sorted([sort_place_tuple_seq(x) for x in p1])
        r2 = sorted([sort_place_tuple_seq(x) for x in p2])
        self.assertEqual(r1,r2)

    def test_place_tuple_sort(self):
        self.assertEqual( ('Test',1,3),
                      place_tuple_key((Place(pid=1,name='Test' ),3)) ) 
        self.assertEqual( [ ('ATest',1,4), ('BTest',2,1) ],
                      sort_place_tuple_seq(( (Place(pid=1,name='ATest'),4),
                                            (Place(pid=2,name='BTest'),1) ) ) ) 
        self.assertEqual( [ ('ATest',1,4), ('BTest',2,1) ],
                      sort_place_tuple_seq(( (Place(pid=2,name='BTest'),1),
                                            (Place(pid=1,name='ATest'),4) ) ) ) 

    def test_assert_markings_equal(self):
        self.assertMarkingsEqual(
                {((Place("Drone",pid="3"), 1), 
                  (Place("Student",pid="2"), 1)), 
                 ((Place("I",pid="1"), 1),)},
                {((Place("Student",pid="2"), 1), 
                  (Place("Drone",pid="3"), 1)), 
                 ((Place("I",pid="1"), 1),)} )

    def test_empty_marking(self):
        net = self.net("I -> [tau__1] -> Student")
        net = to_rsnet(net)
        sem = RoleStateNetSemantics( Marking(net,{}) )
        markings = reachable_markings(sem)
        self.assertEqual(set(),markings)

    def test_simple_sequence(self):
        net = self.net("I -> [tau__1] -> Student")
        net = to_rsnet(net)
        init = findPlace(net,"I")
        student = findPlace(net,"Student")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual([((init,1),),
                                  ((student,1),) ],
                                 markings)

    def test_simple_choice(self):
        net = self.net("I -> [tau__1] -> Student")
        self.add(net,  "I -> [tau__2] -> Drone")
        net = to_rsnet(net)
        init, student, drone = findPlaces(net,"I","Student","Drone")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual([( (init,1),),
                                  ( (student,1), ),
                                  ( (drone,1), )],
                                 markings)

    def test_simple_concurrency(self):
        net = self.net("I -> [tau__1] -> Student")
        self.add(net,  "I -> [tau__1] -> Drone")
        net = to_rsnet(net)
        init, student, drone = findPlaces(net,"I","Student","Drone")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual({( (init,1),),
                                  ( (drone,1), (student,1), )},
                                 markings)

    def test_conc_seq(self):
        net = self.net("I -> [tau__1] -> Student")
        self.add(net,                   "Student -> [tau__2] -> Tutor")
        self.add(net,  "I -> [tau__1] -> Drone")
        net = to_rsnet(net)
        init, student, drone, tutor = \
                findPlaces(net,"I","Student","Drone","Tutor")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual([( (init,1),),
                                  ( (drone,1), (student,1), ),
                                  ( (drone,1), (tutor,1), )],
                                 markings)

    def test_loop(self):
        net = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        self.add(net,                   "Student -> [tau__3] -> Student")
        net = to_rsnet(net)
        init, student, final = findPlaces(net,"I","Student","F")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual([( (init,1),),
                                  ( (student,1), ),
                                  ( (final,1), )],
                                 markings)
            
    def test_longer_loop(self):
        net = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        self.add(net,                   "Student -> [tau__3] -> Bludger") 
        self.add(net,                   "Bludger -> [tau__4] -> Student")
        net = to_rsnet(net)
        init, student, bludger, final = \
                findPlaces(net,"I","Student","Bludger", "F")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        self.assertMarkingsEqual([( (init,1),),
                                  ( (bludger,1), ),
                                  ( (student,1), ),
                                  ( (final,1), )],
                                 markings)

    def test_triple_marking(self):
        net = self.net("I -> {tau__1 3.0} -> Student")
        self.add(net,  "Student -> [tau__2] -> Student")
        self.add(net,  "Student -> [tau__2] -> Sweep")
        self.add(net,  "Student -> [tau__3] -> Bludger")
        self.add(net,  "Student -> [tau__4] -> Student")
        self.add(net,  "Student -> [tau__4] -> Tutor")
        self.add(net,  "Student -> [tau__5] -> Drone")
        self.add(net,  "Tutor   -> [tau__5] -> Drone")
        net = to_rsnet(net)
        init, student, sweep, bludger, tutor, drone = \
                findPlaces(net,"I","Student","Sweep", "Bludger", "Tutor", 
                               "Drone")
        sem = RoleStateNetSemantics( Marking(net,{init:1}) )
        markings = reachable_markings(sem)
        debug(markings)
        self.assertMarkingsEqual([( (init,1),),
                                  ( (student,1),),
                                  ( (bludger,1), ),
                                  ( (bludger,1), (sweep,1) ),
                                  ( (bludger,1), (tutor,1) ),
                                  ( (bludger,1), (sweep,1), (tutor,1) ),
                                  ( (student,1), (sweep,1) ),
                                  ( (student,1), (tutor,1) ),
                                  ( (student,1), (sweep,1), (tutor,1) ),
                                  ( (drone,1), ),
                                  ( (drone,1), (sweep,1) )
                                  ],
                                 markings)


# Allows logging to work while running single tests
if __name__ == '__main__':
    logger.level = logging.DEBUG
    tr = unittest.TextTestRunner()
    module = __import__(__name__)
    for part in __name__.split('.')[1:]:
        module = getattr(module, part)
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test_simple_sequence'
    tests = loader.loadTestsFromModule( module )
    tr.run( tests )


