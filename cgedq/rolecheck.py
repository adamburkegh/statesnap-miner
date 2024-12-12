# -*- coding: utf-8 -*-

# Perform role split independent of full data load, based on an export of 
# consolidated roles. This is based on preference rules across guanzhi and 
# jigou fields, but is before normalization by splitting.

from cgedq.norm import normalize_positions_dict, split_position
from cgedq.roledict import knownroles, role_synonyms
from cgedq.trans import loadroletransfile

import argparse
import csv
import sys


ENCODING='utf-8'
sys.stdout.reconfigure(encoding=ENCODING)

COMMENT='#'



def rolecheck(sourceroles):
    return normalize_positions_dict(sourceroles)

def loadrolefile(fname):
    res = []
    with open(fname,mode='r',encoding=ENCODING,newline='') as f:
        for line in f:
            if line.find(COMMENT,0,1) != 0:
                res.append(line.rstrip())
    return res



def exportroles(fname,splitroles):
    with open(fname, 'w', encoding=ENCODING,newline='') as csvfile:
        fieldnames = ['role','is_known','has_synonym','synonym','count']
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for role in splitroles.keys():
            row = {'role':role,'count':splitroles[role]}
            row |= {'is_known': (role in knownroles) }
            has_synonym = (role in role_synonyms) 
            row |= {'has_synonym': has_synonym }
            row |= {'synonym': (role_synonyms[role] if has_synonym else '') }
            writer.writerow(row)

def calcsimplified(splitroles):
    res = [ role_synonyms[role] if role in role_synonyms else role
                                for role in splitroles ]
    return set(res)

def calctrans(roles,trans):
    return set([role for role in roles if role in trans])

'''
Take the string of a position output by the role normalisation process,
and identify which pre-norm roles it came from.
'''
def trace_position(position,sourceroles):
    res = []
    for cpos in sourceroles:
        sroles = split_position(cpos,knownroles)
        if position in sroles:
            res.append( ( cpos,sroles) )
    return res

def trace_main(position,sourceroles):
    print(f'Tracing position {position} across {len(sourceroles)} roles')
    sourcepos = trace_position(position,sourceroles)
    if not sourcepos:
        print(f'No such entry.')
    for (pos,roles) in sourcepos:
        print(f'    Original job entry: {pos}')
        print(f'    Split into:')
        for srole in roles:
            indict = "No entry"
            if srole in knownroles:
                indict = "Known role"
            print(f'        {srole}     {indict}')
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('rolefile',default='data/zyroles.csv',nargs='?')
    parser.add_argument('-d','--debug',default=False, action='store_true')
    parser.add_argument('-t','--trace')
    args = parser.parse_args()
    sroles = loadrolefile(args.rolefile)
    if args.trace:
        trace_main(args.trace,sroles)
        return
    splitroles = rolecheck(loadrolefile(args.rolefile))
    simproles = calcsimplified(splitroles)
    exportroles('var/rcout.csv',splitroles)
    print(f"Loaded {len(sroles)} roles.")
    print(f"Split and exported {len(splitroles)} roles.")
    print(f"Includes {len(simproles)} unique simplified roles.")
    tran = loadroletransfile('data/roletrans.csv')
    tranroles = calctrans(simproles,tran)
    print(f"Of simplified roles, {len(tranroles)} have translations.")
    if args.debug:
        for tr in tran:
            print(f'{tr} {tran[tr]}')


if __name__ == '__main__':
    main()

