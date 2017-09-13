Cross-Linguistic Transcription System
=====================================

This is an attempt to create a system that allows to translate and compare different phonetic transcription systems. 

For starters, try this quick example:

```python
>>> from pyclts.clts import CLTS
>>> bipa = CLTS() # broad IPA
>>> snd1 = bipa['ts']
>>> snd2 = asjp['c']
>>> snd1.name
'voiceless alveolar affricate consonant'
>>> snd2.name
'voiceless alveolar affricate consonant'
```

You can see that internally, we represent the sounds `ts` and `c`, depending on the alphabet from which they are taking.

Another example is to parse a sound that is not yet in our database. We will try to create this sound automatically and infer its features from the set of diacritics and the base sound:

```python
>>> sound = bipa['dʷʱ']
>>> sound.name
'labialized breathy-voiced alveolar affricate consonant'
>>> sound.generated
True
>>> sound.alias
True
>>> print(sound)
d̤ʷ
>>> print(sound.uname)
LATIN SMALL LETTER D / COMBINING DIAERESIS BELOW / MODIFIER LETTER SMALL W
print(sound.codepoints)
U+0064 U+0324 U+02b7
```

You can see, since we represent breathy-voice phonation differently, we flag this sound as an alias. Also since it is not yet in our database explicitly coded, we flag it as a "generated" sound. In a similar way, you can generate sounds from their names:

```python
>>> sound = bipa['aspirated voiced aspirated bilabial plosive consonant']
>>> print(sound)
ʰbʰ
>>> sound.generated
True
>>> sound.name
'pre-aspirated aspirated voiced bilabial plosive consonant'
```

Note that this sound probably does not exist in any language, but we generate it from the feature components. Note also that the ```name``` that is automatically given for the sound automatically orders how the features are put together to form the sound identifier. In principle, our features bundles are unordered, but we try to decide for some explicit order of features to enhance comparison.


