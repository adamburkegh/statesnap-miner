
from itertools import zip_longest
import os.path
import unittest

from pm.ssnap.ssnap import (StateSnapshot, sslogFromCSV, sslogWithRanges, 
                         pruneForNoiseByTranWeight, arcsSpanningTran)
from pm.ssnap import ssnap
from pmkoalas.models.petrinet import *
from pmkoalas.models.pnfrag import *
import logging
from logging import debug, info
from tests.pm import ssnap as tssnap


# logging.getLogger().setLevel(logging.DEBUG)

def mine(sslog):
    return ssnap.minePLPN(sslog,label="ssmtestplpn")

def mineWithRecode(sslog,expected,final=False):
    result = ssnap.minePLPN(sslog,label="ssmtestplpn",final=final)
    recodePlaces(result,expected)
    return result

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
    for arc in netToChange.arcs:
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
    

class StateSnapshotMinerTest(unittest.TestCase):

    def setUp(self):
        self.parser = PetriNetFragmentParser()

    def net(self,netText,label=None):
        lb = "ssmtestplpn"
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
        expected = self.net("I -> [tau__1] -> Student")
        sslog = {1: [ StateSnapshot(1,1700,set(['Student'])) ] }
        pn = mine(sslog)
        self.assertNetEqual(expected,pn)

    def test_singleton_final(self):
        expected = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        sslog = {1: [ StateSnapshot(1,1700,set(['Student'])) ] }
        pn = mineWithRecode(sslog,expected,final=True)
        self.assertNetEqual(expected,pn)

    def test_single_state_two_places(self):
        expected = self.net("I -> [tau__1] -> Student")
        self.add(expected,  "I -> [tau__1] -> Sweep")
        sslog = {1:[ StateSnapshot(1,1700,
                     set(['Student','Sweep'])) ]  }
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)

    def test_single_state_two_places_final(self):
        expected = self.net("I -> [tau__1] -> Student -> [tau__2] -> F")
        self.add(expected,  "I -> [tau__1] -> Sweep   -> [tau__2] -> F")
        sslog = {1: [ StateSnapshot(1,1700,
                      set(['Student','Sweep'])) ]  }
        pn = mineWithRecode(sslog,expected,final=True)
        self.assertNetEqual(expected,pn)

    def test_one_case_two_seq_states(self):
        sslog = {1: [ StateSnapshot(1,1700,
                           set(['Sweep'])) ,
                      StateSnapshot(1,1701,
                           set(['Student']) ) ] } 
        pn = mine(sslog)
        expected = self.net("I -> [tau__1] -> Sweep -> [tau__2] -> Student")
        self.assertNetEqual(expected,pn)


    def test_two_cases_two_states(self):
        expected = self.net("I -> [tau__1] -> Sweep")
        self.add(expected,  "I -> [tau__2] -> Student")
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
        sslog = {1: [ StateSnapshot(1,1700,
                                    set(['Student'])) ,
                      StateSnapshot(1,1701,
                                    set(['Student','Sweep']) ),
                      StateSnapshot(1,1702,
                                    set(['Student']) )   ]}   
        pn = mineWithRecode(sslog,expected)
        self.assertNetEqual(expected,pn)


    def test_multi_cases_weight(self):
        expected = self.net("I -> {tau__1 1.0} -> Student")
        self.add(expected,  "I -> {tau__2 3.0} -> Sweep")
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
        self.assertEqual(len( result.arcs ), 8) 
        self.assertEqual(len( result.transitions ), 3) 
        self.assertEqual(len( result.places ), 3) 


    def test_prune_for_noise(self):
        hedge = self.net("I -> {tau__1 341.0} -> Sweep")
        self.add(hedge,  "I -> {tau__2 2.0} -> Student")
        self.add(hedge,  "I -> {tau__2 2.0} -> Sweep")
        self.add(hedge,  "I -> {tau__3 100.0} -> Student")
        expected = self.net("I -> {tau__1 341.0} -> Sweep")
        self.add(expected,"I -> {tau__3 100.0} -> Student")
        result = pruneForNoiseByTranWeight(hedge,0.01)
        self.assertNetEqual( expected, result )
        result = pruneForNoiseByTranWeight(hedge,0.001)
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
    sitems1 = sorted(net1.arcs, 
                     key=lambda arc: (arc.from_node.name,arc.to_node.name ) ) 
    sitems2 = sorted(net2.arcs, 
                     key=lambda arc: (arc.from_node.name,arc.to_node.name ) ) 
    sz = zip_longest(sitems1,sitems2,fillvalue="") 
    for (s1,s2) in sz:
        debug(f"{s1}\t{s2}\t{s1 == s2}")
    debug("")




