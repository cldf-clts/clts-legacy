from pyclts import *
import json
from collections import defaultdict

bipa = TranscriptionSystem()

table = []

for k, v in bipa.features['consonant'].items():
    row = ['consonant', bipa._feature_values[k], k, v]
    table += [row]
    
    

for k, v in bipa.features['vowel'].items():
    row = ['vowel', bipa._feature_values[k], k, v]
    table += [row]
    
    
    
    

for s in bipa.sounds:
    if not bipa[s].type == 'marker':
        for f in bipa[s]._features():
            if not bipa[s].type in [ 'tone', 'marker']:
                table += [[bipa[s].type, bipa._feature_values[f], getattr(bipa[s], bipa._feature_values[f]), bipa.features[bipa[s].type].get(f, '')]]
            elif bipa[s].type == 'tone':
                table += [[bipa[s].type, bipa._feature_values[f],
                    getattr(bipa[s], bipa._feature_values[f]), '']]
        

table = sorted(set([tuple(x) for x in table if not None in x]))

table = [['sound_class', 'feature', 'value', 'diacritic']] + table

# write to tsv but prepare to writ to json as well
output = {"vowel": defaultdict(list), "consonant": defaultdict(list), "tone":
        defaultdict(list)}
with open('features.tsv', 'w') as f:
    for line in table:
        f.write('\t'.join(line)+'\n')
        if line[0] in ['vowel', 'consonant', 'tone']:
            output[line[0]][line[1]] += [line[2]]
with open('features.json', 'w') as f:
    f.write(json.dumps(output, indent=2))

