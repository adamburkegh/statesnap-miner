
import unittest
from pmmodels.pnexport import exportPetriNetToPM4PY
from pmmodels.pnfrag import PetriNetFragmentParser
from cgedq.logutil import debug
import pm4py



class PNExportTest(unittest.TestCase):
    def test_export_to_pm4py(self):
        parser = PetriNetFragmentParser()
        net = parser.createNet("dotTest",
                            "I -> {tau 2.0} -> Sweep")
        parser.addToNet(net,"I -> {tau 2.0} -> Student")
        parser.addToNet(net,"I -> {a 3.0} -> Student")
        outnet = exportPetriNetToPM4PY(net)
        self.assertEqual( len(net.places), len(outnet.places) )
        self.assertEqual( len(net.transitions), len(outnet.transitions) )
        self.assertEqual( len(net.arcs), len(outnet.arcs) )
        debug(outnet)
        debug(net)
        # Manually check visualisation
        # pm4py.view_petri_net(outnet)

