
from typing import Tuple
import unittest

from pmkoalas.models.pnfrag import *

def findPlace(net,label):
    """
    Return first node with this label
    """
    for place in net._places:
        if label == place.name:
            return place

def findPlaces(net,*labels) -> Tuple:
    """
    Return first node with this label
    """
    return tuple([findPlace(net,label) for label in labels])

def findTransitionById(net,nodeId):
    """
    Return first node with this label
    """
    for tran in net._transitions:
        if nodeId == tran.nodeId:
            return tran

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


