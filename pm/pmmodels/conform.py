
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
        result.append( entry )
    return tuple(result)

def freeze_semantics(semantics:PetriNetSemantics):
    return freeze_mark(semantics.marking())

def freeze_mark(marking:Marking):
    debug(f"freeze_mark( {marking.mark} )")
    return sort_place_tuple_seq(marking.mark.items())

def thaw_mark(marking:tuple):
    debug(f'thaw_mark( {marking} )')
    return { place : tokens for place, tokens in marking }


def reachable_markings(semantics:PetriNetSemantics) -> Iterable:
    '''
    Return a dictionary of markings reachable from start_marking. This
    function creates the collection of reachable markings using basic search and
    provides no termination guarantee. The caller is responsible to pass 
    nets, markings and semantics that do not create infinite reachable markings,
    eg, workflow nets.
    '''
    debug(f'reachable_markings() ')
    if len(semantics.mark.mark) == 0:
        return set()
    stack = []
    result = set()  
    startMark = deepcopy(semantics.mark.mark)
    debug(f'startMark {startMark}')
    enabled = semantics.enabled()
    fsm = freeze_mark(semantics.mark)
    # marking, level
    stack.append( (fsm, 0) )
    while stack != []:
        fmark, level = stack.pop()
        mark = thaw_mark (fmark)
        debug(f'looking at {mark}')
        semantics.mark = Marking(semantics.mark.net,mark)
        result |= set( [fmark] )
        level += 1
        enabled = semantics.enabled()
        debug(f'{level} enabled {enabled}')
        for tran in enabled:
            # debug(f'    semantics.mark {semantics.mark}')
            # debug(f'    {level}    marking {semantics.mark.mark}')
            # debug(f'    {level}    enabled {enabled}')
            nm = semantics.remark(tran)
            debug(f'    new mark {nm.mark}')
            newmark = freeze_mark(nm)
            if newmark not in result:
                debug(f"    not in result, pushing on stack ... {newmark}")
                stack.append( (newmark, level ) )
            # debug(f'    {level}     next_markings {next_markings}')
            semantics.mark = Marking(semantics.mark.net,mark)
    semantics.mark = Marking(semantics.mark.net,startMark)
    return result


