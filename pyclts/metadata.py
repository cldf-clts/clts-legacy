from pyclts.util import metadata_path
from clldutils.dsv import NamedTupleReader

def phoible():
    out = {}
    with NamedTupleReader(metadata_path('phoible.tsv'), delimiter='\t') as uni:
        for row in uni:
            out[row.CLTS_NAME] = {
                    "id": row.PHOIBLE_ID, 
                    "grapheme": row.PHOIBLE_GRAPHEME}
            out[row.BIPA_GRAPHEME] = out[row.CLTS_NAME]
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

