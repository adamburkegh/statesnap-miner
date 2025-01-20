
from itertools import zip_longest
import logging
from logging import debug, info
import os.path
import sys
import unittest

from pm.ssnap.ssnap import (StateSnapshot, sslogFromCSV, sslogWithRanges, 
                         pruneForNoise, arcsSpanningTran)
from pm.ssnap import ssnap
from pmkoalas.models.petrinet import *
from pmkoalas.models.pnfrag import *
from tests.pm import ssnap as tssnap
from tests.pm.pmmodels.pnfragutil import findTransitionById, findPlaces

mpath = os.path.abspath(tssnap.__path__[0])

logger = logging.getLogger()
# logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def mine(sslog):
    return ssnap.mine(sslog,label="ssmtestrsn")

def mineWithRecode(sslog,expected,final=True):
    result = ssnap.mine(sslog,label="ssmtestrsn",final=final)
    recodePlaces(result,expected)
    return result

def arckey(arc):
    return (type(arc.to_node) == Place, arc.from_node.name, arc.to_node.name) 

def recodePlaces(netToChange,referenceNet):
    '''
    For each place in netToChange, look up the place by name in referenceNet,
    and recreate the place using the id found there.

    Pre: unique place names.
    '''
    newPlaces = {p.name: Place(p.name,pid=p.pid) for p in referenceNet.places }
    extraPlaces = [p for p in netToChange.places if not p.name in newPlaces]
    netToChange._places = set( newPlaces.values() ) | set(extraPlaces)
    newArcs = set()
    for arc in sorted(netToChange.arcs,key=arckey):
        newArc = arc
        if isinstance(arc.from_node,Place) and arc.from_node.name in newPlaces:
            newPlace = newPlaces[arc.from_node.name]
            newArc = Arc(newPlace,arc.to_node)
            debug(f"recoding {arc} to {newArc}")
        if isinstance(arc.to_node,Place) and arc.to_node.name in newPlaces:
            newPlace = newPlaces[arc.to_node.name]
            newArc = Arc(arc.from_node,newPlace)
            debug(f"recoding {arc} to {newArc}")
        newArcs.add(newArc)
    netToChange._arcs = newArcs
    
def makePicky(netToChange:LabelledPetriNet, tranIds:list):
    for tranId in tranIds:
        tran = findTransitionById(netToChange,tranId)
        tran.picky = True

class StateSnapshotMinerRoleStateNetTest(unittest.TestCase):

    def setUp(self):
        stream_handler.stream = sys.stdout
        self.parser = PetriNetFragmentParser()

    def net(self,netText,label=None):
        lb = "ssmtestrsn"
        if label:
            lb = label
        return self.parser.create_net(lb,netText)

    def add(self,net,netText):
        return self.parser.add_to_net(net,netText)

    def assertNetEqual(self,net1,net2):
        self.assertEqual(net1,net2,verbosecmp(net1,net2))

    def test_recode_places(self):
        net1 = self.net("I -> [tau] -> Sweep__1")
        net2 = self.net("I -> [tau] -> Sweep__2")
        recodePlaces(net1,net2)
        self.assertNetEqual(net1,net2)

    def test_singleton(self):
        expected = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        makePicky(expected,[2])
        sslog = {1: [ StateSnapshot(1,1700,set(['Student'])) ] }
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)

    def test_singleton_no_final(self):
        expected = self.net("I -> [tau__1] -> Student")
        sslog = {1: [ StateSnapshot(1,1700,set(['Student'])) ] }
        pn = mineWithRecode(sslog,expected,final=False)
        self.assertNetEqual(expected,pn)

    def test_singleton_trace_variant(self):
        expected = self.net("I -> {tau__1 2.0} -> Student -> {tau__2 2.0} -> F")
        makePicky(expected,[2])
        sslog = {1: [ StateSnapshot(1,1700,set(['Student'])) ],
                 2: [ StateSnapshot(1,1700,set(['Student'])) ],}
        pn = mineWithRecode(sslog,expected)
        arcdebug(expected,pn)
        self.assertNetEqual(expected,pn)

    def test_single_state_two_places(self):
        expected = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        self.add(expected,  "I -> [tau__1] -> Sweep   -> [tau__2] -> F")
        makePicky(expected,[2])
        sslog = {1: [ StateSnapshot(1,1700,
                      set(['Student','Sweep'])) ]  }
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)

    def test_one_case_two_seq_states(self):
        sslog = {1: [ StateSnapshot(1,1700,
                           set(['Sweep'])) ,
                      StateSnapshot(1,1701,
                           set(['Student']) ) ] } 
        expected = self.net(
            "I -> [tau__1] -> Sweep -> [tau__2] -> Student -> [tau__4] -> F")
        self.add(expected,                   "Sweep -> [tau__3] -> F")
        makePicky(expected,[3,4])
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)


    def test_two_cases_two_states(self):
        expected = self.net("I -> [tau__1] -> Sweep")
        self.add(expected,  "I -> [tau__2] -> Student")
        self.add(expected,                   "Sweep -> [tau__3] -> F")
        self.add(expected,                 "Student -> [tau__4] -> F")
        makePicky(expected,[3,4])
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Sweep']))],
                 2: [ StateSnapshot(2,1701,
                                    set(['Student']) ) ] } 
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)

    def test_add_concurrent_role(self):
        expected = self.net("I -> [tau__1] -> Student")
        self.add(expected,  "Student -> [tau__2] -> Student")
        self.add(expected,  "Student -> [tau__2] -> Sweep")
        self.add(expected,  "Student -> [tau__3] -> F")
        self.add(expected,  "Student -> [tau__4] -> F")
        self.add(expected,    "Sweep -> [tau__4] -> F")
        makePicky(expected,[3,4])
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ,
                      StateSnapshot(1,1701,
                                    set(['Student','Sweep']) )]}   
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)


    def test_lose_concurrent_role(self):
        expected = self.net("I -> [tau__1] -> Student")
        self.add(expected,  "Student -> [tau__2] -> Student")
        self.add(expected,  "Student -> [tau__2] -> Sweep")
        self.add(expected,  "Student -> [tau__3] -> Student")
        self.add(expected,  "Sweep   -> [tau__3] -> Student")
        self.add(expected,  "Student -> [tau__4] -> F")
        self.add(expected,  "Student -> [tau__5] -> F")
        self.add(expected,    "Sweep -> [tau__5] -> F")
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ,
                      StateSnapshot(1,1701,
                                    set(['Student','Sweep']) ),
                      StateSnapshot(1,1702,
                                    set(['Student']) )   ]}   
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)


    def test_multi_cases_weight(self):
        expected = self.net(
                "I -> {tau__1 1.0} -> Student")
        self.add(expected,  
                "I -> {tau__2 3.0} -> Sweep")
        self.add(expected,           "Student -> [tau__3] -> F")
        self.add(expected,             "Sweep -> {tau__4 3.0} -> F")
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ],
                 2: [ StateSnapshot(2,1701,
                                    set(['Sweep']) ) ] ,
                 3: [ StateSnapshot(3,1705,
                                    set(['Sweep']) ) ],
                 4: [ StateSnapshot(4,1701,
                                    set(['Sweep']) ) ] }   
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)

    def test_two_conc_one_choice_one(self):
        expected = self.net("I -> {tau__1 3.0} -> Student")
        self.add(expected,  "Student -> [tau__2] -> Student")
        self.add(expected,  "Student -> [tau__2] -> Sweep")
        self.add(expected,  "Student -> [tau__3] -> Bludger")
        self.add(expected,  "Student -> [tau__4] -> Student")
        self.add(expected,  "Student -> [tau__4] -> Tutor")
        self.add(expected,  "Student -> [tau__5] -> Drone")
        self.add(expected,  "Tutor   -> [tau__5] -> Drone")
        #
        # self.add(expected,    "Sweep -> [tau__7] -> F")
        self.add(expected,  "Bludger -> [tau__6] -> F")
        self.add(expected,    "Drone -> [tau__7] -> F")
        self.add(expected,  "Student -> [tau__8] -> F")
        # self.add(expected,    "Tutor -> [tau__10] -> F")
        #
        self.add(expected,  "Bludger -> [tau__9] -> F")
        self.add(expected,    "Sweep -> [tau__9] -> F")
        self.add(expected,  "Student -> [tau__10] -> F")
        self.add(expected,    "Sweep -> [tau__10] -> F")
        #self.add(expected,  "Student -> [tau__12] -> F")
        #self.add(expected,  "Bludger -> [tau__12] -> F")
        #self.add(expected,  "Student -> [tau__13] -> F")
        #self.add(expected,    "Drone -> [tau__13] -> F")
        self.add(expected,  "Student -> [tau__11] -> F")
        self.add(expected,    "Tutor -> [tau__11] -> F")
        self.add(expected,    "Drone -> [tau__12] -> F")
        self.add(expected,    "Sweep -> [tau__12] -> F")
        #self.add(expected,    "Sweep -> [tau__17] -> F")
        #self.add(expected,    "Tutor -> [tau__17] -> F")
        #self.add(expected,  "Bludger -> [tau__18] -> F")
        #self.add(expected,    "Drone -> [tau__18] -> F")
        self.add(expected,  "Bludger -> [tau__13] -> F")
        self.add(expected,    "Tutor -> [tau__13] -> F")
        #self.add(expected,    "Drone -> [tau__20] -> F")
        #self.add(expected,    "Tutor -> [tau__20] -> F")
        #
        self.add(expected,  "Bludger -> [tau__14] -> F")
        self.add(expected,    "Sweep -> [tau__14] -> F")
        self.add(expected,    "Tutor -> [tau__14] -> F")
        self.add(expected,  "Student -> [tau__15] -> F")
        self.add(expected,    "Sweep -> [tau__15] -> F")
        self.add(expected,    "Tutor -> [tau__15] -> F")
        #
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ,
                      StateSnapshot(1,1701,
                                    set(['Student','Sweep']) )],
                 2: [ StateSnapshot(2,1705,
                                    set(['Student']) ),
                      StateSnapshot(2,1709,
                                    set(['Bludger']) )],
                 3: [ StateSnapshot(3,1706,
                                    set(['Student']) ),
                      StateSnapshot(3,1709,
                                    set(['Student','Tutor']) ),
                      StateSnapshot(3,1710,
                                    set(['Drone']) ) ] }   
        pn = mineWithRecode(sslog,expected)
        arcdebug(expected,pn)
        pnfragdebug(expected)
        pnfragdebug(pn)
        makePicky(expected,range(6,16))
        #debug(f'expected {expected}')
        #debug(f'result {pn}')
        self.assertEqual( expected._transitions, pn._transitions)
        self.assertNetEqual(expected,pn)

    def test_tran_mutation_in_set(self):
        # Subtle Python bugs can emerge when changing hash values while
        # objects are in sets 
        sslog = {1: [StateSnapshot(1,1830.75, {'Senior Compiler'}) ],
                 2: [StateSnapshot(2,1892.5 , {'Senior Compiler'}), 
                     StateSnapshot(2,1893.5 , {'Principal Examiner', 
                                               'Senior Compiler'}),
                     StateSnapshot(2,1893.75, {'Senior Compiler'})]    }
        # have to avoid recode as it will hide the set issue
        result = mine(sslog)
        # Note this includes the picky transitions and the final place
        self.assertEqual(len( result.arcs ), 13) 
        self.assertEqual(len( result.transitions ), 5) 
        self.assertEqual(len( result.places ), 4) 


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

    def test_prune_for_noise(self):
        hedge = self.net("I -> {tau__1 341.0} -> Sweep")
        self.add(hedge,  "I -> {tau__2 2.0} -> Student")
        self.add(hedge,  "I -> {tau__2 2.0} -> Sweep")
        self.add(hedge,  "I -> {tau__3 100.0} -> Student")
        expected = self.net("I -> {tau__1 341.0} -> Sweep")
        self.add(expected,"I -> {tau__3 100.0} -> Student")
        result = pruneForNoise(hedge,0.01)
        self.assertNetEqual( expected, result )
        result = pruneForNoise(hedge,0.001)
        self.assertNetEqual( hedge, result )

    def test_add_spanning_tran(self):
        studentP = Place("Student",1)
        sweepP   = Place("Sweep",2)
        atop = {"Student": studentP, "Sweep": sweepP }
        # tran = Transition(1)
        tran = silent_transition(1)
        arcExp = set([Arc(studentP,tran),Arc(tran,sweepP)])
        result = arcsSpanningTran( set(["Student"]), tran, set(["Sweep"]),atop )
        self.assertTrue( Arc(studentP,tran) in result )
        self.assertTrue( Arc(tran,sweepP) in result )
        self.assertTrue( Arc(studentP,tran) in arcExp )
        self.assertTrue( Arc(tran,sweepP) in arcExp )
        self.assertEqual(arcExp,result)
        self.assertEqual(arcExp,arcExp | result)


def arcdebug(net1,net2):
    debug('arcdebug()')
    sitems1 = sorted(net1.arcs, 
                     key=lambda arc: (arc.from_node.name,arc.to_node.name ) ) 
    sitems2 = sorted(net2.arcs, 
                     key=lambda arc: (arc.from_node.name,arc.to_node.name ) ) 
    sz = zip_longest(sitems1,sitems2,fillvalue="") 
    for (s1,s2) in sz:
        debug(f"{s1}\t{s2}\t{s1 == s2}")
    debug("")

def trandebug(pn,tran,visited) -> set:
    output = set()
    for arc in pn.arcs:
        if arc not in visited and arc.to_node == tran:
            output |= {arc}
            debug(arc)
    for arc in pn.arcs:
        if arc not in visited and arc.from_node == tran:
            output |= {arc}
            debug(f'            {arc}')
    return output


def pnfragdebug(pn):
    debug(f'pnfragdebug({pn.name})')
    output = set()
    initPlace, finalPlace = findPlaces(pn,'I','F')
    for arc in pn.arcs:
        if arc.from_node == initPlace:
            debug(arc)
            output |= {arc}
            output |= trandebug(pn,arc.to_node,output)
    for tran in sorted(pn.transitions,key=lambda t:t.tid):
        output |= trandebug(pn,tran,output)


# Allows logging to work while running single tests
if __name__ == '__main__':
    logger.level = logging.DEBUG
    tr = unittest.TextTestRunner()
    module = __import__(__name__)
    for part in __name__.split('.')[1:]:
        module = getattr(module, part)
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test_singleton_no_final'
    # loader.testMethodPrefix = 'test_multi_cases_weight'
    tests = loader.loadTestsFromModule( module )
    tr.run( tests )


