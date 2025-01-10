
import logging
from logging import debug
import math
from pmkoalas.models.petrinet import PetriNetDOTFormatter, Arc, Transition
# from pmkoalas.models.dotutil import export_DOT_to_image
## Includes local cut and paste fork elements
## Also has RoleStateNet specific elements 
from pm.pmmodels.dotutil import export_DOT_to_image
from pm.pmmodels.rsnet import RoleStateNet


logger = logging.getLogger(__name__)
debug, info = logger.debug, logger.info

class ScaledFormatter(PetriNetDOTFormatter):
    # These sizes should probably be relative instead of absolute

    def __init__(self,pn,sslog:dict,font='SimSun'):
        rfont = 'SimSun' if (font is None) else font
        super().__init__(pn,rfont)
        self._nodemap = {}
        # self._default_height = 0.2
        self._default_font_size=12
        actfreq = {}
        actsum = 0
        for caseId in sslog:
            for ss in sslog[caseId]:
                for act in ss.activities:
                    if act in actfreq:
                        actfreq[act] += 1
                    else:
                        actfreq[act] = 1
                    actsum += 1
        self._actfreq = actfreq
        self._actsum = actsum
        self._sf = 40
        self._arcscale = 10
        self._plscale = 2


    def transform_transition(self,tran,ti):
        tl = '' # tran.name if tran.name and tran.name != 'tau' else '&tau;'
        SPACE = ' '
        if SPACE in tl:
            tl = tl.replace(SPACE,"\n")
        fstr = f'n{str(ti)} [shape="box",margin="0, 0.1",'
        fstr += f'label="{tl} {tran.weight}", style="filled",'
        # height = self._defaultHeight + tran.weight/10.0
        # fstr += f'height="{height}", width="{height}"'
        fstr += '];\n'
        return fstr

    def transform_place(self,place,pi):
        height = self._default_height
        fs = self._default_font_size
        SPACE = ' '
        placeName = place.name
        if SPACE in place.name:
            placeName = place.name.replace(SPACE,"\n")
        if place.name in self._actfreq:
            sf = self._plscale * \
                   math.sqrt(self._sf * self._actfreq[place.name] /self._actsum)
            height = self._default_height + sf
            fs = round(self._default_font_size + 8*sf)
        fstr = f'n{str(pi)} [shape="circle",label="{placeName}",'
        fstr += f'height="{height}", fontsize="{fs}"];\n'
        return fstr

    def transform_arc(self,arc):
        #debug(f'transform_arc({arc})')
        from_node = self._nodemap[arc.from_node]
        to_node = self._nodemap[arc.to_node]
        weight = 1
        if arc.from_node in self._pn.transitions:
            weight = arc.from_node.weight
        elif arc.to_node in self._pn.transitions:
            weight = arc.to_node.weight
        asize = self._arcscale * math.sqrt(self._sf * weight / self._actsum )
        return f'n{from_node}->n{to_node}[penwidth="{asize}"]\n'


INITIAL_NAME = 'I'
FINAL_NAME = 'F'

def picky_arc(arc:Arc) -> bool:
    # print(f'picky_arc({arc})')
    return  (isinstance(arc.to_node,Transition) and arc.to_node.picky ) or \
            (isinstance(arc.from_node,Transition) and arc.from_node.picky ) 


class RoleStateNetFormatter(ScaledFormatter):
    # These sizes should probably be relative instead of absolute

    def __init__(self,pn:RoleStateNet,sslog:dict,font='SimSun',
                 termination_weights=True,
                 initial_name = INITIAL_NAME, final_name=FINAL_NAME):
        super().__init__(pn,sslog,font)
        self._termination_weights = termination_weights
        self._initial_name = initial_name
        self._final_name = final_name
        self._fontsize = 14

    def prelude(self) -> str:
        dotstr = 'digraph G{\n'
        dotstr += f'ranksep=".3"; fontsize="14"; remincross=true; margin="0.0,0.0"; fontname="{self._font}";rankdir="LR";charset=utf8;\n'
        dotstr += 'edge [arrowsize="0.5"];\n'
        dotstr += f'node [height="{self._default_height}",width="{self._default_height}",fontname="{self._font}"'
        dotstr += f',fontsize="{self._fontsize}"];\n'
        dotstr += 'ratio=0.4;\n'
        return dotstr

    def transform_picky_arcs(self,picky_arcs,ni) -> str:
        if len(picky_arcs) == 0:
            return ""
        fstr =  f'n{str(ni)} [shape="none",margin="0",'
        fstr += f'label=<<table>\n'
        fstr += '<th><td>Roles</td><td>Termination Weight</td></th>'
        tran_incoming = {}
        for arc in picky_arcs:
            if isinstance(arc.to_node,Transition):
                tran = arc.to_node
                if tran in tran_incoming:
                    tran_incoming[tran].append(arc.from_node)
                else:
                    tran_incoming[tran] = [arc.from_node]
        for tran in tran_incoming:
            fstr += '<tr><td align="left">'
            for place in tran_incoming[tran]:
                fstr += f'{place.name}; '
            fstr += f'</td><td align="right">{tran.weight}</td></tr>\n'
        fstr += '</table>>];\n'
        return fstr

    def transform_net(self) -> str:
        debug('RoleStateNetFormatter.transform_net()')
        dotstr = self.prelude()
        ni = 1
        #debug('   places')
        initialPlace = None
        for pl in self._pn.places:
            if pl.name == INITIAL_NAME:
                initialPlace = pl
            if pl.name == self._final_name:
                continue
            ni += 1
            self._nodemap[pl] = ni
            dotstr += self.transform_place(pl,ni)
        #debug('   transitions')
        for tr in self._pn.transitions:
            if tr.picky:
                continue
            ni += 1
            self._nodemap[tr] = ni
            dotstr += self.transform_transition(tr,ni)
        # debug(f'{self._nodemap}')
        picky_arcs = []
        for ar in self._pn.arcs:
            if picky_arc(ar):
                picky_arcs.append(ar)
                continue
            dotstr += self.transform_arc(ar)
        if self._termination_weights:
            ni += 1
            dotstr += self.transform_picky_arcs(picky_arcs,ni)
            finalWeightNode = ni
            initNi = self._nodemap[initialPlace]
            dotstr += f'n{finalWeightNode}->n{initNi} [style=invis];\n'
        dotstr += '}\n'
        return dotstr



def exportToScaledDOT(net,sslog: set,font) -> str:
    return ScaledFormatter(net,sslog,font).transform_net()


def exportNetToScaledImage(vard,oname,pn,sslog,font):
    dotStr = exportToScaledDOT(pn,sslog,font)
    export_DOT_to_image(vard,oname,dotStr) 

def exportRoleStateNetDOT(net,sslog,font) -> str:
    return RoleStateNetFormatter(net,sslog,font,
                                 termination_weights=False).transform_net()

def exportRoleStateNetToImage(vard,oname,pn,sslog,font):
    dotStr = exportRoleStateNetDOT(pn,sslog,font)
    export_DOT_to_image(vard,oname,dotStr) 


