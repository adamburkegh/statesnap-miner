# 
# Load translation file
#

import csv
from enum import IntEnum
import types

ENCODING='utf-8'


class TransSource(IntEnum):
    HUCKER = 1
    CHEN = 2
    WIKTIONARY = 3
    OTHER = 4
    ADAMBURKE = 5

    @staticmethod
    def from_str(label):
        if label == 'Hucker':
            return TransSource.HUCKER
        if label == 'Chen':
            return TransSource.CHEN
        if label == 'WT':
            return TransSource.WIKTIONARY
        if label == 'AB':
            return TransSource.ADAMBURKE
        return TransSource.OTHER



def transobj(row):
    newt = types.SimpleNamespace()
    newt.pos = row['Position']
    newt.translation = row['Translation']
    newt.pinyin = row['Pinyin']
    newt.source = TransSource.from_str(row['Source'])
    return newt



def loadtransfile(fname='data/roletrans.csv'):
    trans = {}
    with open(fname, encoding=ENCODING, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pos = row['Position'] 
            if not pos in trans:
                newt = transobj(row)
                trans[pos] = newt
            else:
                old = trans[pos]
                newsource = TransSource.from_str(row['Source'])
                if newsource < old.source:
                    trans[pos] = transobj(row)
    return trans

