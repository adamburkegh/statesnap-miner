# statesnap-miner

The State Snapshot Miner for constructing Petri net models from activity trace logs. This has been applied to data from the [CGED-Q](https://shss.hkust.edu.hk/lee-campbell-group/projects/china-government-employee-database-qing-cged-q/), a digital version of Qing civil service records.

## Running

### Installing

Clone the repo and create a virtual environment of your choice.

Install dependencies with 

`pip install -r requirements.txt`

Visualisation depends on [Graphviz](https://graphviz.org/) being installed and on the PATH.

### Running the example
The example script, [snapeg.py](snapeg.py), uses a toy CSV log from the unit tests, and outputs a model diagram.

```
$ python snapeg.py
Output model to test_ssnap1.png.
```


### Testing
`python -m unittest`

## Qing data from the CGED-Q

Scripts for working with CGED-Q data are in the `cgedq` package. There are two steps.

[conv.py](cgedq/conv.py) converts CSV or Stata extracts into CSV files in state snapshot log form. Multiple files are produced according to different slices of the data. A 

[mine.py](cgedq/mine.py) takes snapshot CSV files, performs further filtering, runs the state snapshot miner on them, producing PNG output. Output can be varied to eg PNML or PDF by changing the script. 

As the full set of CGED-Q data is not in public release, it is not included in this project. Do note that an extract covering  1900-1911 is publicly available.
