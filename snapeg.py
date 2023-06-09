import ssnap.ssnap as snapminer
from pmmodels.pnformatter import exportNetToScaledImage


sslog = snapminer.sslogFromCSV('tests/ssnap/test_ssnap_log1.csv',
                                'personid','job','year',
                                types={'personid': int, 'year':int },
                                keepSuccDupes=False)
pn = snapminer.mine(sslog,label="ssmtest")
iname = 'test_ssnap1'
exportNetToScaledImage('.',iname,pn,sslog, 'Times-Roman')
print(f'Output model to {iname}.png.')


