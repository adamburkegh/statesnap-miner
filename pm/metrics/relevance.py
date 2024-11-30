
import math

def model_cost(modelTF, trace) -> float: 
		return -1.0 * \
                math.log2( modelTF.freq(trace)/ modelTF.trace_total() )

