
import unittest

from pmkoalas.models.pnfrag import *

def findPlace(net,label):
    """
    Return first node with this label
    """
    for place in net._places:
        if label == place.name:
            return place


class PetriNetTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PetriNetFragmentParser()

    def net(self,netText,label=None):
        lb = "ssmetricstest"
        if label:
            lb = label
        return self.parser.create_net(lb,netText)

    def add(self,net,netText):
        return self.parser.add_to_net(net,netText)


