# statesnap-miner

The State Snapshot Miner for constructing Petri net models from activity trace logs. This has been applied to data from the [CGED-Q](https://shss.hkust.edu.hk/lee-campbell-group/projects/china-government-employee-database-qing-cged-q/), a digital version of Qing civil service records. A paper on this research is forthcoming.

## Running

Requires Python 3.11 or later.

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

Implementations of the miner and code to work with state snapshot logs are in the `ssnap` module, and can be used as a library.

### Testing
`python -m unittest`

## Qing data from the CGED-Q

Scripts for working with CGED-Q data are in the `cgedq` package. There are two steps.

1. Convert - [conv.py](cgedq/conv.py) - create state snapshot logs for different types of officials as CSV files in the `var/` directory
2. Mine - [mine.py](cgedq/mine.py) - run the state snapshot miner 

These two scripts form a (simple) data pipeline and there is much in them specific to the input data and target extracts. It is best to think of them as project-specific worked examples. They definitely aren't a supported API.

### Convert

[conv.py](cgedq/conv.py) converts CSV or Stata extracts into CSV files in state snapshot log form. Multiple files are produced according to different slices of the data. Check help for extra options.

`python -m cgedq.conv <datafile>`

Some example extracts of the [CGED-Q public data release 1850-1864](https://shss.hkust.edu.hk/lee-campbell-group/2022/01/04/cged-q-jinshenlu-1850-1864-public-release-now-available/) are included as CSV files. This example will create state snapshot logs from Jinshi officials in the 1850-1864 period.

`python -m cgedq.conv cged-q-jinshi_1850-1864.csv --tmlfile tml_1850-1864.csv --rebuild`


### Mine

[mine.py](cgedq/mine.py) takes snapshot CSV files, performs further filtering, runs the state snapshot miner on them, producing PNG output. Output can be varied to eg PNML or PDF by changing the script. 

`python -m cgedq.mine`



As the full set of CGED-Q data is not in public release, it is not included in this project. Do note that an extract covering  1900-1911 is publicly available.

### Public Extracts Included


These include only a subset of the attributes available in the CGED-Q, and include some basic data normalisation that suited this project, such as standardising hanzi character variants. 
