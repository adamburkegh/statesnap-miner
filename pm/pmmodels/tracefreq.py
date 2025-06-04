

class TraceFrequency:
    def __init__(self,elements:dict = {}):
        self._elements = elements
        self._trace_total = sum( elements.values() )
        self._roles = set( [r for t in self._elements for r in t] )

    def freq(self,trace):
        if trace in self._elements:
            return self._elements[trace]
        return 0

    def trace_total(self):
        return self._trace_total

    def role_total(self):
        return len(self._roles)

    def __str__(self):
        traces = ""
        for t in self._elements:
            traces += f'    {t}  :{self._elements[t]}\n'
        return f'TraceFrequency:\n    {len(self._roles)} roles: {self._roles}\n    {self._trace_total} traces\n{traces}'

    '''
    Treat return value as read-only.
    '''
    def traces(self):
        return self._elements.keys()


    '''
    Treat return value as read-only.
    '''
    def elements(self):
        return self._elements


class RoleTraceFrequency(TraceFrequency):
    def __init__(self, elements:dict = {}):
        self._elements = elements
        self._trace_total = sum( elements.values() )
        self._roles = \
                set( [r for t in self._elements for rs in t for r in rs] )


    def __str__(self):
        traces = ""
        for t in self._elements:
            ts = [set(x) for x in t]
            traces += f'    {str(ts):40s}: {self._elements[t]:8d}\n'
        return f'TraceFrequency:\n    {len(self._roles)} roles: {self._roles}\n    {self._trace_total} traces\n{traces}'


class EntryFrequency:
    def __init__(self, tf: TraceFrequency ):
        self._entries = {}
        elements = tf.elements()
        for trace in elements:
            for entry in trace:
                if entry in self._entries:
                    self._entries[entry] += elements[trace]
                else:
                    self._entries[entry] = elements[trace]
        self._entry_total = sum( self._entries.values() )

    def entry_total(self):
        return self._entry_total

    def entry_freq(self,entry):
        return self._entries[entry]

    ''' Treat as read-only '''
    def entries(self):
        return self._entries

