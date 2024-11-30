import unittest

from pm.metrics.relevance import *

ss = frozenset


class TraceFrequency:
    def __init__(self,elements:dict = {}):
        self._elements = elements
        self._trace_total = sum( elements.values() )

    def freq(self,trace):
        if trace in self._elements:
            return self._elements[trace]
        return 0

    def trace_total(self):
        return self._trace_total


class TraceFrequencyTest(unittest.TestCase):

    def test_zero(self):
        mtf = TraceFrequency( { 'a': 2, 'b': 3 } )
        self.assertEqual( 2, mtf.freq('a') )
        self.assertEqual( 0, mtf.freq('No such') )
        self.assertEqual( 5, mtf.trace_total() )


class EntropicRelevanceTest(unittest.TestCase):

    def test_model_cost_error(self):
        mtf = TraceFrequency( { 'a': 2 } )
        self.assertRaises( ValueError, model_cost, mtf, ( 'no such' ) )

    def test_model_cost_strings(self):
        mtf = TraceFrequency( { 'a': 1, 'ba': 7 } )
        self.assertEqual( 3, model_cost( mtf, 'a' ) )


