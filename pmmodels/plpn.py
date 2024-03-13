'''
Semantics for a Place Labelled Petri Net
'''

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Set
from pmkoalas.models.petrinet import *



@dataclass(frozen=True)
class Marking:
    net: LabelledPetriNet
    mark: Dict[Place,int]

def singleton_marking(net, mark: list[Place]):
    fullmark = { p: 1 for p in mark }
    return Marking(net,fullmark)
        


class PetriNetSemantics:
    """
    Calculate enabling and firing semantics for a marked net.
    """

    def __init__(self, marking: Marking) -> None:
        self._net = marking.net
        self._mark = marking
        # for each transition compute the incoming and outgoing places
        self._incoming:Dict[Transition,Set[Place]] = dict()
        self._outgoing:Dict[Transition,Set[Place]] = dict()
        self._update_arc_context()

    def _update_arc_context(self):
        # Inefficient: checks every transition every time
        for trans in self._net.transitions:
            arcs = self._net.arcs
            incoming = [ arc for arc in arcs if  arc.to_node == trans ]
            outgoing = [ arc for arc in arcs if arc.from_node == trans ]
            self._incoming[trans] = [ arc.from_node for arc in incoming ]
            self._outgoing[trans] = [ arc.to_node for arc in outgoing ]

    def enabled(self) -> Set[Transition]:
        """
        returns the set of transitions that are enabled at this marking.
        """
        ret = set()
        for trans in self._net.transitions:
            enabled = True
            for place in self._incoming[trans]:
                enabled = enabled and place in self._mark.mark \
                        and self._mark.mark[place] > 0
            if (enabled):
                ret.add(trans)
        return ret

    def remark(self, firing:Transition) -> Marking:
        """
        Returns a new marking, that is one step from this marking by firing
        the given transition.
        """
        if firing not in self.enabled():
            raise ValueError("Given transition cannot fire from this marking.")
        next_mark = deepcopy(self._mark.mark)
        for incoming in self._incoming[firing]:
            next_mark[incoming] = next_mark[incoming] - 1
            if next_mark[incoming] == 0:
                del next_mark[incoming] 
        for outgoing in self._outgoing[firing]:
            if outgoing in next_mark:
                next_mark[outgoing] = next_mark[outgoing] + 1
            else:
                next_mark[outgoing] = 1
        self._mark = Marking(self._net, next_mark)
        self._update_arc_context()
        return self._mark

    def marking(self):
        return self._mark






class PLPNSemantics(PetriNetSemantics):
    """
    Firing rules for PLPN including capacity.
    """
    def __init__(self, marking: Marking) -> None:
        super().__init__(marking)


    def enabled(self) -> Set[Transition]:
        """
        returns the set of transitions that are enabled at this marking.
        """
        ret = set()
        for trans in self._net.transitions:
            enabled = True
            for inp in self._incoming[trans]:
                enabled = enabled \
                        and inp in self._mark.mark \
                        and self._mark.mark[inp] > 0
            if not enabled:
                next
            for outp in self._outgoing[trans]:
                enabled = enabled \
                        and (not outp in self._mark.mark \
                             or outp in self._incoming[trans])
            if (enabled):
                ret.add(trans)
        return ret




