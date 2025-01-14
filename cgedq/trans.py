# 
# Load translation file
#

import csv
from enum import IntEnum
import types

ENCODING='utf-8'


class TransSource(IntEnum):
    """
    Sources:
    HUCKER      Hucker, Charles - A Dictionary of Official Titles in 
                Imperial China
    CHEN        Chen Bijia - Origins and Career Patterns of the Qing Government 
                Officials (1850-1912): Evidence from the China Government 
                Employee Dataset-Qing (CGED-Q). OR: private correspondence 
                advice from Chen Bijia when she was working in the Lee-Campbell
                Group at HKUST.
    HOU         Hou Yueran, private correspondence from Masters student in
                Lee-Campbell Group at HKUST.
    Wiktionary  Open dictionary
    Wikipedia   The amazing encyclopedia that anyone can edit.
    AB          Adam Burke, originator of this software project.

    """

    HUCKER = 1      
    CHEN = 2
    HOU = 3
    WIKTIONARY = 4
    WIKIPEDIA = 5
    OTHER = 6
    ADAMBURKE = 7

    @staticmethod
    def from_str(label):
        if label == 'Hucker':
            return TransSource.HUCKER
        if label == 'Chen':
            return TransSource.CHEN
        if label == 'Hou':
            return TransSource.HOU
        if label == 'WT':
            return TransSource.WIKTIONARY
        if label == 'WP':
            return TransSource.WIKIPEDIA
        if label == 'AB':
            return TransSource.ADAMBURKE
        return TransSource.OTHER



def roletransobj(row):
    newt = types.SimpleNamespace()
    newt.pos = row['Position']
    newt.translation = row['Translation']
    newt.pinyin = row['Pinyin']
    newt.source = TransSource.from_str(row['Source'])
    return newt


def loadroletransfile(fname='data/roletrans.csv'):
    trans = {}
    with open(fname, encoding=ENCODING, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pos = row['Position'] 
            if not pos in trans:
                newt = roletransobj(row)
                trans[pos] = newt
            else:
                old = trans[pos]
                newsource = TransSource.from_str(row['Source'])
                if newsource < old.source:
                    trans[pos] = roletransobj(row)
    return trans


def placetransobj(row):
    newt = types.SimpleNamespace()
    newt.place = row['Place']
    newt.pinyin = row['Pinyin']
    newt.source = TransSource.from_str(row['Source'])
    return newt

def loadplacetransfile(fname='data/placetrans.csv'):
    trans = {}
    with open(fname, encoding=ENCODING, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pos = row['Place'] 
            if not pos in trans:
                newt = placetransobj(row)
                trans[pos] = newt
            else:
                old = trans[pos]
                newsource = TransSource.from_str(row['Source'])
                if newsource < old.source:
                    trans[pos] = placetransobj(row)
    return trans




