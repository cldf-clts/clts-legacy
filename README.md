Cross-Linguistic Transcription System
=====================================

**+++IMPORTANT DISCLAIMER+++**

Software and data underlying this repository are currently under heavy maintenance and will probably still change a lot before we will be able to publish a first official version. We would therefore kindly request all potential users to **NOT** re-use this software for their own applications in this stage and instead wait until we have a first officially published **citeable** version.

This is an attempt to create a system that allows to translate and compare different phonetic transcription systems. 

For starters, try this quick example:

```python
>>> from pyclts import TranscriptionSystem as TS
>>> bipa = TS() # broad IPA
>>> ajsp = TS('asjp') # asjp transcription system
>>> snd1 = bipa['ts']
>>> snd2 = asjp['c']
>>> snd1.name
'voiceless alveolar affricate consonant'
>>> snd2.name
'voiceless alveolar affricate consonant'
```

You can see that internally, we represent the sounds `ts` and `c`, depending on the alphabet from which they are taken.

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

You can also use our transcription data to convert from one transcription system to a given dataset (note that backwards-conversion may not be possible, as transcription data is often limited):

```
>>> from pyclts.ts import translate, TranscriptionSystem
>>> from pyclts.td import TranscriptionData
>>> bipa = TranscriptionSystem('bipa')
>>> sca = TranscriptionData('sca')
>>> translate('f a: t ə r', bipa, sca)
    'B A T E R'
```

But the translation can even be done in a much simpler way, by loading the transcription data directly:

```
>>> form pyclts.td import TranscriptionData
>>> sca = TranscriptionData('sca')
>>> sca('v a t ə r')
    ['B', 'A', 'T', 'E', 'R']
```


## Basic Structure of the Package

The ```clts``` package offers two basic types of data generated and managed in Python code:

* transcription systems (```pyclts.ts.TranscriptionSystem```), a system that can *generate* sounds
* transcription data (```pyclts.data.TranscriptionData```): a dataset with a *fixed number of sounds*

Transcription data is linked to our transcription system by the grapheme for the B(road) IPA transcription system, which serves as our default, and the name, which follows the IPA conventions with some modifications which were needed to make sure that we can represent sounds that we regularly find in cross-linguistic datasets.


