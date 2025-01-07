'''
Structures and semantics for a Role-State nets. Role-State nets are weighted
nets with place capacities of one and two types of transitions.
'''

from typing import Dict, Set, Iterable
from pmkoalas.models.petrinet import Place, Transition, Arc, LabelledPetriNet
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




