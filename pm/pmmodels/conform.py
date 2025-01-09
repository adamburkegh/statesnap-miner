
from copy import deepcopy
from logging import debug
from typing import Iterable

from pmkoalas.models.petrinet import Place, LabelledPetriNet
from pm.pmmodels.plpn import Marking, PetriNetSemantics

def freeze_semantics(semantics:PetriNetSemantics):
    return freeze_mark(semantics.marking())

def freeze_mark(marking:Marking):
    return tuple(marking.mark.items())


def reachable_markings(semantics:PetriNetSemantics) -> Iterable:
    '''
    Return a dictionary of markings reachable from start_marking. This
    function creates the collection of reachable markings using basic search and
    provides no termination guarantee. The caller is responsible to pass 
    nets, markings and semantics that do not create infinite reachable markings,
    eg, workflow nets.
    '''
    debug('reachable_markings()')
    if len(semantics.marking().mark) == 0:
        return set()
    result = set( [freeze_semantics(semantics)] )
    start = deepcopy(semantics)
    for tran in semantics.enabled():
        nm = semantics.remark(tran)
        newmark = freeze_mark(nm)
        if newmark not in result:
            next_markings = reachable_markings(semantics)
            result |= next_markings
        semantics = start
    return result

