
import math
from pmkoalas.models.petrinet import PetriNetDOTFormatter
# from pmkoalas.models.dotutil import export_DOT_to_image
## local cut and paste fork
from pm.pmmodels.dotutil import export_DOT_to_image


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
        from_node = self._nodemap[arc.from_node]
        to_node = self._nodemap[arc.to_node]
        weight = 1
        if arc.from_node in self._pn.transitions:
            weight = arc.from_node.weight
        elif arc.to_node in self._pn.transitions:
            weight = arc.to_node.weight
        asize = self._arcscale * math.sqrt(self._sf * weight / self._actsum )
        return f'n{from_node}->n{to_node}[penwidth="{asize}"]\n'


def exportToScaledDOT(net,sslog: set,font) -> str:
    return ScaledFormatter(net,sslog,font).transform_net()


def exportNetToScaledImage(vard,oname,pn,sslog,font):
    dotStr = exportToScaledDOT(pn,sslog,font)
    export_DOT_to_image(vard,oname,dotStr) 



