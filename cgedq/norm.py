import pandas as pd

from cgedq import roledict


def split_position(pos,known_roles):
    if pos in known_roles:
        return [pos]
    known_roles.sort(key=lambda ls: -len(ls) )
    result = []
    for role in known_roles:
        if pos.find(role) >= 0:
            result.append(role)
            pos = pos.replace(role,'',1)
    if pos != "":
        result.append(pos)
    return result

def normalize_positions(positions,knownroles,jobfield='synjob'):
    posres =  [ split_position(p,knownroles)
                              for p in positions[jobfield] ]
    flat = [ item for sublist in posres for item in sublist ]
    return pd.DataFrame(set(flat),columns=[jobfield])


def normalize_positions_df(indf,knownroles,jobfield='synjob'):
    rescols = indf.columns
    resdict = dict( (col,[]) for col in rescols ) 
    for index, row in indf.iterrows():
        for pos in split_position(row[jobfield],knownroles):
            for rescol in rescols:
                if rescol == jobfield:
                    resdict[rescol].append(pos)
                else:
                    resdict[rescol].append(row[rescol])
    return pd.DataFrame(resdict)


def normalize_positions_dict(sourceroles,knownroles=roledict.knownroles):
    res = {}
    for cpos in sourceroles:
        sroles = split_position(cpos,knownroles)
        for role in sroles:
            if role in res:
                res[role] = res[role]+1
            else:
                res[role] = 1
    return res


