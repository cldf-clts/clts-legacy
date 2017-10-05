from pyclts.util import metadata_path
from clldutils.dsv import NamedTupleReader
from collections import defaultdict

def phoible():
    out = defaultdict(list)
    with NamedTupleReader(metadata_path('phoible.tsv'), delimiter='\t') as uni:
        for row in uni:
            if row.PHOIBLE_ID not in [x.get('id', '') for x in
                    out[row.CLTS_NAME]]:
                out[row.CLTS_NAME] += [{
                        "id": row.PHOIBLE_ID, 
                        "grapheme": row.PHOIBLE_GRAPHEME}]
                out[row.BIPA_GRAPHEME] += [out[row.CLTS_NAME]]
    return out


def pbase():
    out = defaultdict(list)
    with NamedTupleReader(metadata_path('pbase.tsv'), delimiter='\t') as uni:
        for row in uni:
            if row.PBASE_URL not in [x.get('id', '') for x in
                    out[row.CLTS_NAME]]:
                out[row.CLTS_NAME] += [{
                        "id": row.PBASE_URL, 
                        "grapheme": row.PBASE_GRAPHEME}]
                out[row.BIPA_GRAPHEME] += [out[row.CLTS_NAME]]
    return out

def lingpy():
    out = {}
    with NamedTupleReader(metadata_path('lingpy.tsv'), delimiter='\t') as uni:
        for row in uni:
            out[row.CLTS_NAME] = {
                    "sca": row.SCA_CLASS, 
                    "dolgo": row.DOLGOPOLSKY_CLASS, 
                    "asjp": row.ASJP_CLASS, 
                    "prosody": row.PROSODY_CLASS, 
                    "cv": row.CV_CLASS, 
                    "color": row.COLOR_CLASS
                    }
            out[row.BIPA_GRAPHEME] = out[row.CLTS_NAME]
    return out

