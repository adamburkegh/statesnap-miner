'''
Structures and semantics for a Role-State nets. Role-State nets are weighted
nets with place capacities of one and two types of transitions.
'''

from typing import Dict, Set, Iterable
import xml.etree.ElementTree as ET
from pmkoalas.models.petrinet import Place, Transition, Arc, LabelledPetriNet
import pm
from pm.pmmodels.plpn import Marking, singleton_marking, PetriNetSemantics


# Is class hierarchy the best way to represent?
class RSTransition(Transition):
    def __init__(self,name,pickyt=False,tid=None):
        if tid == None:
            Transition.__init__(self,name,tid=name)
        else:
            Transition.__init__(self,name,tid=tid)
        self._picky = pickyt

    @property
    def picky(self):
        return self._picky

    def __eq__(self,other):
        return Transition.__eq__(self,other) \
                and self._picky == other._picky

    def __hash__(self) -> int:
        return hash((self._name,self._tid,self._weight,self._silent,
                     self._picky))


class RoleStateNet(LabelledPetriNet):
    def __init__(self, places:Iterable[Place], transitions:Iterable[Transition],
                 arcs:Iterable[Arc],
                 name:str='Role-State net'):
        for tran in transitions:
            if not hasattr(tran,'picky'):
                tran.picky = False
        LabelledPetriNet.__init__(self,places,transitions,arcs,name) 

def to_rsnet(net:LabelledPetriNet) -> RoleStateNet:
    for tran in net._transitions:
        if not hasattr(tran,'picky'):
            tran.picky = False
    return net

class RoleStateNetSemantics(PetriNetSemantics):
    """
    Firing rules for RSNets including capacity.
    """
    def __init__(self, marking: Marking) -> None:
        super().__init__(marking)

    def active_enabled(self,trans):
        for inp in self._incoming[trans]:
            if inp not in self._mark.mark \
                    or self._mark.mark[inp] == 0:
                return False
        for outp in self._outgoing[trans]:
            if outp in self._mark.mark \
                    and outp not in self._incoming[trans]:
                return False
        return True

    def picky_enabled(self,trans):
        if set(self._mark.mark.keys()) != set(self._incoming[trans]):
            return False
        return self.active_enabled(trans)


    def enabled(self) -> Set[Transition]:
        """
        returns the set of transitions that are enabled at this marking.
        """
        ret = set()
        for trans in self._net.transitions:
            renabled = True
            if trans.picky:
                renabled = self.picky_enabled(trans)
            else:
                renabled = self.active_enabled(trans)
            if renabled:
                ret.add(trans)
        return ret


def convert_net_to_xml(net:LabelledPetriNet ) -> ET.Element: 
    """
    Converts a given Petri net to an XML structure that conforms with the pnml
    schema.

    See: http://www.pnml.org/version-2009/grammar/pnmlcoremodel.rng
    """
    # Copy-paste fork of koalas version, stripping out cruft and irrelevancies
    # At time of writing, koalas version needs rework to
    #   - strip out subclass logic for DPNs
    #   - remove markings from net data structure
    #   - fix UUID behaviour
    root = ET.Element('pnml')
    net_node = ET.SubElement(root,'net', 
            attrib={'type': PNML_URL,
                    'id':net.name} )
    net_namer = ET.SubElement(net_node, "name")
    ET.SubElement(net_namer, "text").text = net.name
    page = ET.SubElement(net_node,'page', id="page1")
    for place in net.places:
        placeNode = ET.SubElement(page,'place', 
            attrib={'id': "place-"+str(place.pid) } )
        if place.name:
            name_node = ET.SubElement(placeNode,'name')
            text_node = ET.SubElement(name_node,'text')
            text_node.text = place.name
        if isinstance(place.pid, int):
            localNode = f'p{place.pid}'
        else:
            localNode = place.pid
        prom_node = ET.SubElement(
                placeNode, 'toolspecific',
                attrib={
                    'tool' : "ProM",
                    'version' : "6.4",
                    'localNodeID' : localNode
                }
            )
    for tran in net.transitions:
        tranNode = ET.SubElement(page,'transition', 
                        attrib={'id':"transition-"+str(tran.tid) } )
        if tran.name:
            name_node = ET.SubElement(tranNode,'name')
            text_node = ET.SubElement(name_node,'text')
        ts_node = ET.SubElement(tranNode,'toolspecific',
                        attrib={ 'tool':'StochasticPetriNet',
                                 'version':'0.2', 
                                 'invisible': str(tran.silent),
                                 'priority': '1',
                                 'weight' : str(tran.weight),
                                 'distributionType': 'IMMEDIATE'} )
        trs_node = ET.SubElement(tranNode,'toolspecific',
                        attrib={ 'tool':'RoleStateNet',
                                 'version':pm.version, 
                                 'transitionType': \
                                    ( 'PICKY' if tran.picky else 'ACTIVE') } )

    arcid = 1
    for arc in net.arcs:
        if isinstance(arc.from_node, Place):
            arcNode = ET.SubElement(page,'arc',
                attrib={'source': "place-"+str(arc.from_node.nodeId), 
                        'target': "transition-"+str(arc.to_node.nodeId),
                        'id': "arc-"+str(arcid) } )
        else:
            arcNode = ET.SubElement(page,'arc',
                attrib={'source': "transition-"+str(arc.from_node.nodeId), 
                        'target': "place-"+str(arc.to_node.nodeId),
                        'id': "arc"+str(arcid) } )
        arcid += 1


def export_rsnet_to_pnml(rsnet:RoleStateNet, fname:str):
    # Under-tested
    # Copy-paste fork of koalas version, stripping out cruft and irrelevancies
    xml =  convert_rsnet_to_xml(net)
    ET.indent( xml ) 
    ET.ElementTree(xml).write(fname,xml_declaration=True, encoding="utf-8")


