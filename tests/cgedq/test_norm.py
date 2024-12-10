# -*- coding: utf-8 -*-

import unittest
import pandas as pd
from cgedq.norm import *
from cgedq.logutil import *

DEBUG=False

class NormTest(unittest.TestCase):
    def test_split_position(self):
        self.assertEqual(['teacher'],
                          split_position("teacher",[]))
        self.assertEqual(['teacher'],
                          split_position("teacher",['builder']))
        self.assertEqual(['teacher','violinist'],
                          split_position("teacherviolinist",['teacher']))
        self.assertEqual(['teacher','builder','violinist'],
                          split_position("teacherviolinistbuilder",
                                         ['teacher','builder']))
        self.assertEqual(['priest','pri','violist'],
                          split_position("priestpriviolist",
                                         ['priest','pri']))
        self.assertEqual(['priest','pri','violist'],
                          split_position("priestpriviolist",
                                         ['pri','priest']))
        self.assertEqual(['violist','priest','ly'],
                          split_position("priestlyviolist",
                                         ['priest','violist']))

    def test_split_cc(self):
        self.assertEqual(['戶部務','賞戴花翎'],
                          split_position('賞戴花翎戶部務',
                                         ['戶部務','正主考']))

    def test_split_overlap_riw(self):
        self.assertEqual(['翰林院侍讀學士','咸安宮總裁教習'],
                      split_position('翰林院侍讀學士咸安宮總裁教習',
                                    ['翰林院侍讀學士','咸安宮總裁教習']) )
        self.assertEqual(['翰林院侍讀學士','咸安宮總裁教習'],
                      split_position('翰林院侍讀學士咸安宮總裁教習',
                                    ['翰林院侍讀學士','翰林院侍讀',
                                     '咸安宮總裁教習']) )
        self.assertEqual(['翰林院侍讀學士','咸安宮總裁教習'],
                      split_position('翰林院侍讀學士咸安宮總裁教習',
                                    ['翰林院侍讀','翰林院侍讀學士',
                                     '咸安宮總裁教習']) )


    def test_normalize_position_empty(self):
        df = pd.DataFrame({'synjob' : ['Job 1', 'Job 2', 'Job 3']})
        normalize_positions(df,knownroles=[]) 


    def test_normalize_position_1(self):
        df = pd.DataFrame({'synjob' : ['Job 1Job 4', 'Job 2', 'Job 3']})
        res = normalize_positions(df,knownroles=['Job 4']) 
        debug(res)

    def test_normalize_position_cc(self):
        df = pd.DataFrame({'synjob' : 
                ['頭品頂戴工部務', '頭品頂戴賞戴花翎吏部務', '軍機戶部務',
                  '賞戴花翎協辦大學士禮部務教習庶吉士']
                })
        knownroles= ['工部務','禮部務','戶部務']
        res = normalize_positions(df,
                        knownroles=knownroles)
        if (not DEBUG):
            return
        with open('tnpc.csv','w',encoding='utf-8',newline='') as of:
            res.to_csv(of)
            of.write('\n')

    def test_normalize_position_df(self):
        df = pd.DataFrame({'synjob' : ['Job1Job2', 'Job2', 'Job3'],
                           'person_id': [1,2,3]})
        df.reset_index()
        normalize_positions_df(df,knownroles=['Job1','Job2']) 


    def test_normalize_position_dict(self):
        compjobs = ['Job 1Job 4', 'Job 2', 'Job 3']
        sj = normalize_positions_dict(compjobs,['Job 4'] )
        self.assertEqual(['Job 1','Job 2', 'Job 3', 'Job 4'], 
                         sorted(sj) )


if __name__ == '__main__':
    unittest.main()

