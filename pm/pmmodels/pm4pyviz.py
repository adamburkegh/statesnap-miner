#
# Convert a PNML file or pm4py Petri net to a DOT graph file
# 
#
#


import pm4py
import sys

def toUnicodeCodepoints(sin):
    out = ""
    for ch in sin:
        out += str(ord(ch))
    return out

# Petri net
def tranDOT(tran,ti):
    fstr = '{} [shape="box",margin="0, 0.1",label="{}",style="filled"];\n'
    tl = tran.label if tran.label else '&tau;'
    return fstr.format('n' + str(ti),tl)

def placeDOT(place,pi):
    fstr = '{} [shape="circle",label=""];\n'
    return fstr.format('n' + str(pi))

def arcDOT(arc,nodemap):
    return "n{}->n{}\n".format(nodemap[arc.source],nodemap[arc.target])


# BPMN
def flowDOT(flow,nodemap):
    return "n{}->n{}\n".format(
                nodemap[flow.get_source()],nodemap[flow.get_target()])

def nodeDOT(node,nodeid):
    fstr = '{} [shape="box",margin="0, 0.1",label="{}",style="filled,rounded"];\n'
    nl = node.get_name() 
    return fstr.format('n' + str(nodeid),nl)
          
opshape = '{} [shape="diamond",width="0.4",height="0.4",margin="0, 0",label="{}"];\n'

def xor(node,nodeid):
    nl = node.get_name() 
    return opshape.format('n' + str(nodeid),'X')
          
def parallel(node,nodeid):
    nl = node.get_name() 
    return opshape.format('n' + str(nodeid),'+')
          

''' 
Must provide a compatible font with extended character sets 
like Russian or Chinese
''' 
def netToDOT(net,font):
    dotstr = ""
    dotstr += 'digraph G{\n'
    dotstr += 'ranksep=".3"; fontsize="14"; remincross=true; margin="0.0,0.0"; fontname="SimSun";rankdir="LR";charset=utf8;\n'
    dotstr += 'edge [arrowsize="0.5"];\n'
    dotstr += 'node [height=".2",width=".2",fontname="' + font 
    dotstr +=                                    '",fontsize="14"];\n'
    dotstr += 'ratio=0.4;\n'
    nodemap = {}
    ni = 1
    for pl in net.places:
        ni += 1
        nodemap[pl] = ni
        dotstr += placeDOT(pl,ni)
    for tr in net.transitions:
        ni += 1
        nodemap[tr] = ni
        dotstr += tranDOT(tr,ni)
    for ar in net.arcs:
        dotstr += arcDOT(ar,nodemap)
    dotstr += '}\n'
    return dotstr

def bpmnToDOT(bpmn,font):
    dotstr = ""
    dotstr += 'digraph G{\n'
    dotstr += 'ranksep=".3"; fontsize="14"; remincross=true; margin="0.0,0.0"; fontname="SimSun";rankdir="LR";charset=utf8;\n'
    dotstr += 'edge [arrowsize="0.5"];\n'
    dotstr += 'node [height=".2",width=".2",fontname="' + font 
    dotstr +=                                    '",fontsize="14"];\n'
    dotstr += 'ratio=0.4;\n'
    nodemap = {}
    ni = 1
    for node in bpmn.get_nodes():
        ni += 1
        nodemap[node] = ni
        nodeName = node.get_name() 
        if nodeName.find('xor') == 0:
            dotstr += xor(node,ni)
        elif nodeName.find('parallel') == 0:
            dotstr += parallel(node,ni)
        else:
            dotstr += nodeDOT(node,ni)
    for flow in bpmn.get_flows():
        dotstr += flowDOT(flow,nodemap)
    dotstr += '} \n'
    # print(dotstr)
    return dotstr


def viz(pnetfile,font='Arial'):
    net, init, fin = pm4py.read_pnml(pnetfile) 
    print(netToDOT(net,font))


if __name__ == '__main__':
    viz(sys.argv[1])

