
from copy import deepcopy
import logging
from typing import Iterable

from pmkoalas.models.petrinet import Place, LabelledPetriNet
from pm.pmmodels.plpn import Marking, PetriNetSemantics

logger = logging.getLogger(__name__)
debug, info = logger.debug, logger.info


def place_tuple_key(pt):
    place, val = pt
    return  (place.name,place.pid,val)

def sort_place_tuple_seq(ptl):
    result = []
    for entry in sorted(ptl,key=place_tuple_key):
        # result.append(  place_tuple_key(entry) )
        result.append( entry )
    return tuple(result)

def freeze_semantics(semantics:PetriNetSemantics):
    return freeze_mark(semantics.marking())

def freeze_mark(marking:Marking):
    # return tuple(sorted(marking.mark.items()))
    return sort_place_tuple_seq(marking.mark.items())

def reachable_markings(semantics:PetriNetSemantics,visited:set=set(),level=0) \
        -> Iterable:
    '''
    Return a dictionary of markings reachable from start_marking. This
    function creates the collection of reachable markings using basic search and
    provides no termination guarantee. The caller is responsible to pass 
    nets, markings and semantics that do not create infinite reachable markings,
    eg, workflow nets.
    '''
    debug(f'reachable_markings() {level}')
    if len(semantics.mark.mark) == 0:
        return set()
    result = set( [freeze_semantics(semantics)] )
    startMark = deepcopy(semantics.mark.mark)
    debug(f'{level} startMark {startMark}')
    enabled = semantics.enabled()
    debug(f'{level} enabled {semantics.enabled()}')
    for tran in enabled:
        # debug(f'    semantics.mark {semantics.mark}')
        # debug(f'    {level}    marking {semantics.mark.mark}')
        # debug(f'    {level}    enabled {enabled}')
        nm = semantics.remark(tran)
        newmark = freeze_mark(nm)
        if newmark not in result and newmark not in visited:
            next_markings = reachable_markings(semantics, result | visited,
                                               level+1)
            result |= next_markings
        # debug(f'    {level}     next_markings {next_markings}')
        semantics.mark = Marking(semantics.mark.net,startMark)
    return result


