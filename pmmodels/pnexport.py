
from pmmodels.petrinet import LabelledPetriNet
from pm4py.objects.petri_net.obj import PetriNet
# 2.7.0 only
# from pm4py.objects.petri_net.stochastic.obj import StochasticPetrinet
from pm4py.objects.petri_net.utils.petri_utils import *


''' 
Export to a pm4py Petri net object. 

pm4py support for stochastic PNs has been
variable. As at June 2023, the old module has been deprecated and a new
module has recently been added in around 2.7.0. Other elements in this
project were developed against pm4py 2.5.0. 

It would be reasonable to enhance this method to export pm4py.objects.petri_net.stochastic.obj.StochasticPetrinet objects in the future.

'''
def exportPetriNetToPM4PY(lpn:LabelledPetriNet) -> PetriNet:
    net = PetriNet(name=lpn.label)
    places = { place: add_place(net, place.name) for place in lpn.places }
    trans = { tran: add_transition(net,name=str(tran.tid),label=tran.name) \
                    for tran in lpn.transitions }
    for arc in lpn.arcs:
        fromNode, toNode = None, None
        if arc.fromNode in places:
            fromNode = places[arc.fromNode]
            toNode   = trans[arc.toNode]
        else:
            fromNode = trans[arc.fromNode]
            toNode   = places[arc.toNode]
        add_arc_from_to(fromNode,toNode,net)
    return net

