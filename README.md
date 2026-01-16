# statesnap-miner and role-state-miner

The State Snapshot Miner and Role-State Miners construct Petri net models from role trace logs. This has been applied to data from the [CGED-Q](https://shss.hkust.edu.hk/lee-campbell-group/projects/china-government-employee-database-qing-cged-q/), a digital version of Qing civil service records. A paper on this research was [presented at ICPM2023](https://adamburkeware.net/2023/09/10/state-snap.html). Research is ongoing and future publications are planned.

## Running

Requires Python 3.11 or later.

### Installing

Clone the repo and create a virtual environment of your choice.

Install dependencies with 

`pip install -r requirements.txt`

Visualisation depends on [Graphviz](https://graphviz.org/) being installed and on the PATH, specifically the `dot` executable.

### Running the example
The example script, [snapeg.py](snapeg.py), uses a toy CSV log from the unit tests, and outputs a model diagram.

```
$ python snapeg.py
Output model to test_ssnap1_pn.png.
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

[conv.py](cgedq/conv.py) converts CSV or Stata extracts into CSV files in state snapshot log form. Multiple files are produced according to different slices of the data. Role conflation of less frequent roles also happens here. Check help for extra options.

`python -m cgedq.conv <datafile>`

Some example extracts of the [CGED-Q public data release 1850-1864](https://shss.hkust.edu.hk/lee-campbell-group/2022/01/04/cged-q-jinshenlu-1850-1864-public-release-now-available/) are included as CSV files. This example will create state snapshot logs from Jinshi officials in the 1850-1864 period.

`python -m cgedq.conv cged-q-jinshi_1850-1864.csv --tmlfile tml_1850-1864.csv --rebuild`


### Mine

[mine.py](cgedq/mine.py) takes snapshot CSV files, performs further filtering, and runs the state snapshot miner on them, producing PNG output. Output can be varied to eg PNML (for PLPN) or PDF by changing the script. 

`python -m cgedq.mine`

This produces several output models covering different subsets and durations. 

[Top candidate (状元) first three years - English](images/cged-q-zyjtnalleng_n0000_ss003y_pn.png)

[Top candidate (状元) first three years - Chinese](images/cged-q-zyjtnall_n0000_ss003y_pn.png)

### Appointment Database

To help explore the data with standard SQL tools, a SQLLite database called `appoint.db` is built in the home directory when `conv.py` runs. 

### Public Extracts Included

As the full set of CGED-Q data is not in public release, it is not included in this project. Do note that there are [public releases of extracts](https://doi.org/10.14711/dataset/E9GKRS) covering 1850-1864 and 1900-1911.

Records for 1850-1864 are in the `data` directory. These extracts include only a subset of the attributes available in the CGED-Q, and include some basic data normalisation that suited this project, such as standardising hanzi character variants and including only officials with surnames (which excludes most Manchu and Mongolians). The exact code used for the extract is in `process_public_extract()` function in [conv.py](https://github.com/adamburkegh/statesnap-miner/blob/3ed73066b57c4b2399d1076951a6867bbb268aa6/cgedq/conv.py#L600).


 * `cged-q-allclean_1850-1864.csv` - All records
 * `cged-q-jinshi_1850-1864.csv` - Jinshi officials
 * `cged-q-t1jtall_1850-1864.csv` - Exam Tier 1 placed officials
 * `cged-q-t2jtall_1850-1864.csv` - Exam Tier 2 placed officials
 * `roletrans.csv` - Small Chinese-English dictionary for role names
 * `tml_1850-1864.csv` - Timinglu exam records with CGED-Q `person_id`, primarily for exam tier

If using the data beyond preliminary investigatory work, please do reach out to the experts at the Lee-Campbell group, and of course cite their work. 

## CGED-Q Conceptual Model

Analysis of this rich data set included the preparation of a [conceptual model in ORM notation](<images/CGED-Q ORM 202506.pdf>).

### References
Burke, A.T., Leemans, S.J.J., Wynn, M.T., and Campbell, C.D. (2023). State Snapshot Process Discovery on Career Paths of Qing Dynasty Civil Servants. ICPM2023.

Burke, A.T., Leemans, S.J.J., Hou, Y., Wynn, M.T., and Campbell, C.D. (forthcoming). State-Based Career Path Discovery and Comparison
For Qing Civil Servants 1830-1904

Chen, B., Campbell, C., Ren, Y., & Lee, J. (2020). Big Data for the Study of Qing Officialdom: The China Government Employee Database-Qing (CGED-Q). Journal of Chinese History, 4(2), 431–460. https://doi.org/10.1017/jch.2020.15

Campbell, C. D., Chen, B., Ren, Y., & Lee, J. (2022). China Government Employee Database-Qing (CGED-Q) Jinshenlu Public Release [Data set]. DataSpace@HKUST. https://doi.org/10.14711/dataset/E9GKRS

