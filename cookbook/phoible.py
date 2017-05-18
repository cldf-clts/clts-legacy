from pyclts.clts import CLTS, data_path, csv_as_list

phoible = csv_as_list(data_path('phoible', 'Parameters.csv'), delimiter=",")
clts = CLTS()

count = 1
for line in phoible[1:]:
    snd = clts.get_sound(line[-4])
    sid = line[4]
    if snd.type == 'consonant' and snd.name:
        if snd.source == str(snd) and not snd.alias:
            print('{0:5}\t{1:5}\t{2:5}\t{3:5}\t{4:2f}\t{5}'.format(
                count, line[-4], str(snd), snd.source, float(line[3]), snd.name))
            count += 1

