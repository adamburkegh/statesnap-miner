
import tempfile
import unittest

from pmkoalas.models.pnfrag import *
from loggen.wpn_loggen import *


def findPlace(net,label):
    """
    Return first node with this label
    """
    for place in net._places:
        if label == place.name:
            return place

ss = frozenset


class  WeightedTokenGameStateLogGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.parser = PetriNetFragmentParser()

    def net(self,netText,label=None):
        lb = "ssmtest"
        if label:
            lb = label
        return self.parser.create_net(lb,netText)

    def add(self,net,netText):
        return self.parser.add_to_net(net,netText)


    def test_simple_seq(self):
        net = self.net("I -> [tau] -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,10)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 10  }
        self.assertEqual(expected, lg)

    def test_two_choice(self):
        net = self.net("I -> [tau] -> F")
        self.add(net,  "I -> [upsilon] -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,10)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 10  }
        self.assertEqual(expected, lg)

    def test_choice_paths(self):
        net = self.net("I -> {a 3.0} -> A -> {b} -> F")
        self.add(net,  "I -> {c 7.0} -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,10)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 7,
                     ( ss(["I"]), ss(["A"]), ss(["F"]) ) : 3  }
        self.assertEqual(expected, lg)

    def test_conc(self):
        net = self.net("I -> [tau__1] -> A -> [tau__2] -> F")
        self.add(net,  "I -> [tau__1] -> B -> [tau__2] -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,10)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["A","B"]), ss(["F"]) ) : 10  }
        self.assertEqual(expected, lg)

    def test_round_alpha(self):
        net = self.net("I -> {a 3.0} -> A -> {b} -> F")
        self.add(net,  "I -> {c 7.0} -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,11)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 7,
                     ( ss(["I"]), ss(["A"]), ss(["F"]) ) : 4  }
        self.assertEqual(expected, lg)

    def test_round_by_allocation(self):
        net = self.net("I -> {a__1 6.0} -> A -> {b} -> F")
        self.add(net,  "I -> {a__2 4.0} -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,11)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 5,
                     ( ss(["I"]), ss(["A"]), ss(["F"]) ) : 6  }
        self.assertEqual(expected, lg)

    def test_round_by_id(self):
        net = self.net("I -> {a__1 5.0} -> A -> {b} -> F")
        self.add(net,  "I -> {a__2 5.0} -> F")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,9)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["F"]) ) : 4,
                     ( ss(["I"]), ss(["A"]), ss(["F"]) ) : 5  }
        self.assertEqual(expected, lg)


    def test_truncate_long(self):
        net = self.net("I -> {a} -> A -> {b 1.0} -> F")
        self.add(net,  "A -> {c 5.0} -> A")
        pi = findPlace(net,"I")
        imark = singleton_marking(net, [pi])
        sem = PLPNSemantics(imark)
        gen = WeightedTokenGameStateLogGenerator(sem,log_size=12,
                                                 max_trace_length=5,
                                                 warnings=False)
        lg = gen.generate()
        expected = { ( ss(["I"]), ss(["A"]), ss(["F"]) ) : 2,
                     ( ss(["I"]), ss(["A"]), ss(["A"]), ss(["F"]) ) : 2 ,
                     ( ss(["I"]), ss(["A"]), ss(["A"]), ss(["A"]), 
                                  ss(["F"]) ) : 2,
                     ( ss(["I"]), ss(["A"]), ss(["A"]), ss(["A"]), 
                                  ss(["A"]) ) : 6,
                     }
        self.assertEqual(expected, lg)



class BagTest(unittest.TestCase):
    def test_bag_union_empty(self):
        self.assertEqual({}, bag_union( {}, {} ) )

    def test_bag_union_one_empty(self):
        self.assertEqual({'a': 1}, bag_union( {'a': 1}, {} ) )

    def test_bag_union_with_intersect(self):
        self.assertEqual({'a': 3, 'b': 2}, 
                bag_union( {'a': 1}, {'a': 2, 'b': 2} )  )




class ExportTest(unittest.TestCase):
    def test_export_simple_log(self):
        log = LightStateLog( { ( ss(["I"]), ss(["F"]) ) : 4,
                               ( ss(["I"]), ss(["A","B"]), ss(["F"]) ) : 5  } )
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            export_simple_log_to_csv(log,tf.name)
            # print('-----')
            # with open(tf.name, 'r') as fin:
            #    print(fin.read())
        # note contents aren't checked automatically



