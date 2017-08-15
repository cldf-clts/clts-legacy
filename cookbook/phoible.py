from pyclts.clts import CLTS, data_path, csv_as_list
from collections import defaultdict

phoible = csv_as_list(data_path('phoible', 'Parameters.csv'), delimiter=",")
clts = CLTS()

count = 1
gens = 0

names = defaultdict(list)
for line in phoible[1:]:
    snd = clts.get_sound(line[-4].replace(' ', ''))
    sid = line[4]
    if snd.type == 'consonant' and snd.name:
        if (snd.source != str(snd) and not snd.alias) or snd.unknown:
            if snd.generated:
                gen = '*'
            else:
                gen = ' '
            print(gen + '{0:5}\t{1:5}\t{2:5}\t{3:5}\t{4:2f}\t{5}\n'.format(
                count, line[-4], str(snd), snd.source, float(line[3]), snd.name))
            count += 1
            if snd.generated:
                gens += 1
            names[snd.name] += [snd.source]
    elif snd.type == 'consonant':
        if not snd.name:
            print(snd, snd.source)
print(gens)
#for name, sounds in names.items():
#    if len(sounds) > 1:
#        print(name, ', '.join(sounds))
#    elif name != sounds[0]:
#        print(name, ', '.join(sounds))
