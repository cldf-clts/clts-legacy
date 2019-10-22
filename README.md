# This repository is superseeded by https://github.com/cldf-clts/clts and https://github.com/cldf-clts/pyclts



### Cross-Linguistic Transcription Systems


This is an attempt to create a system that allows to translate and compare different phonetic transcription systems. 

For starters, try this quick example:

```python
>>> from __future__ import unicode_literals
>>> from pyclts import TranscriptionSystem as TS
>>> bipa = TS('bipa') # broad IPA
>>> asjp = TS('asjpcode') # asjp transcription system
>>> snd1 = bipa['ts']
>>> snd2 = asjp['c']
>>> snd1.name
'voiceless alveolar sibilant affricate consonant'
>>> snd2.name
'voiceless alveolar sibilant affricate consonant'
>>> bipa.translate('ts a ŋ ə', asjp)
'c E N 3'
>>> asjp.translate('C a y', bipa)
'tʃ ɐ j'
```

You can see that internally, we represent the sounds `ts` and `c`, depending on the alphabet from which they are taken.

Another example is to parse a sound that is not yet in our database. We will try to create this sound automatically and infer its features from the set of diacritics and the base sound:

```python
>>> sound = bipa['dʱʷ']
>>> sound.name
'labialized breathy voiced alveolar stop consonant'
>>> sound.generated
True
>>> sound.alias
True
>>> print(sound)
dʷʱ
>>> print(sound.uname)
LATIN SMALL LETTER D / MODIFIER LETTER SMALL W / MODIFIER LETTER SMALL H WITH HOOK
>>> print(sound.codepoints)
U+0064 U+02b7 U+02b1
```

You can see, since we represent breathy-voice phonation differently, we flag this sound as an alias. Also since it is not yet in our database explicitly coded, we flag it as a "generated" sound. In a similar way, you can generate sounds from their names:

```python
>>> sound = bipa['pre-aspirated voiced aspirated bilabial stop consonant']
>>> print(sound)
ʰbʰ
>>> sound.generated
True
>>> sound.name
'pre-aspirated aspirated voiced bilabial plosive consonant'
```

Note that this sound probably does not exist in any language, but we generate it from the feature components. Note also that the ```name``` that is automatically given for the sound automatically orders how the features are put together to form the sound identifier. In principle, our features bundles are unordered, but we try to decide for some explicit order of features to enhance comparison.

You can also use our transcription data to convert from one transcription system to a given dataset (note that backwards-conversion may not be possible, as transcription data is often limited):

```python
>>> from pyclts import TranscriptionSystem, SoundClasses 
>>> bipa = TranscriptionSystem('bipa')
>>> sca = SoundClasses('sca')
>>> bipa.translate('f a: t ə r', sca)
    'B A T E R'
```

But the translation can even be done in a much simpler way, by loading the transcription data directly:

```python
>>> sca = SoundClasses('sca')
>>> sca('v a t ə r')
    ['B', 'A', 'T', 'E', 'R']
```


#### Basic Structure of the Package

The ```pyclts``` package offers three basic types of data generated and managed in Python code:

* transcription systems (```pyclts.transcriptionsystems.TranscriptionSystem```), a system that can *generate* sounds
* transcription data (```pyclts.transcriptiondata.TranscriptionData```): a dataset with a *fixed number of sounds*
* sound classes (```pyclts.soundclasses.SoundClasses```): a dataset with a direct mapping from sounds to a concrete character (the sound class)


Transcription data is linked to our transcription system by the grapheme for the B(road) IPA transcription system, which serves as our default, and the name, which follows the IPA conventions with some modifications which were needed to make sure that we can represent sounds that we regularly find in cross-linguistic datasets.

#### Parsing Procedure 

feature | handled by | note | example
--- | --- | --- | ---
normalized | ```ts._norm()```, ```ts[sound].normalized``` | this refers to one-to-one character replacement with obviously wrong unicode lookalikes | ```λ``` (wrong) vs. ```ʎ``` (correct)
alias | transcription system data (```+``` indicates alias), ```ts['sound'].alias``` | this refers to "free" IPA variants that are widely used and are therefore officially accepted for "broad ipa" or any other TS, but one variant is usually chosen as the preferred one | ```ts``` (normal) vs. ```ʦ``` (alias)
source | ```ts['sound'].source``` | the unnormalized form as it is given to the TS | ```bipa['λ'].source == 'λ'```
grapheme | ```ts[lingpy/'sound'].grapheme``` | the normalized form which has not been resolved by an alias | ```bipa['ʦ'].grapheme == 'ʦ'
string/unicode | ```ts['sound'].__unicode__()``` | the normalized form in which a potential alias is replaced by its "accepted" counterpart | ```str(bipa['ʦ']) == 'ts'```
name | ```bipa['sound'].name``` | the canonical representation of the feature system that defines a sound, with the sound class (consonant, cluster, vowel, diphthong) in the end, and the feature bundle following the order given in the ```pyclts.models``` description of the corresponding sound class. This representation serves as the basis for translation among different TS. | ```bipa['ts'].name == 'voiceless alveolar sibilant-affricate consonant'```
generated | ```ts['sound'].generated``` | If a sound is not yet know to a given TS, the algorithm tries to generate it by de-composing it into its *base part* and adding features to the left and to the right, based on the *diacritics*. If a sound has been generated, this is traced with help of the attribute. Normally, generated sounds need to be double-checked by the experts, as their grapheme representation may be erroneous. Thus, while the sound ```kʷʰ``` can be regularly defined in a TS (like BIPA), a user might query ```kʰʷ```, in which case the sound would be generated internally, the grapheme would be stored in its normalized form (which is identical with the base), but the ```str()```-representation would contain the correct order, and the character would be automatically qualified as an alias of an existing one.  | ```str(TS['kʰʷ']) == 'kʷʰ' and TS['kʰʷ'].grapheme == 'kʰʷ' and TS[''kʰʷ'].alias and TS['kʰʷ'].generated``` 
base | ```ts['sound'].base``` | if a sound is being generated, the parsing algorithm first tries to identify the potential "base" of the sound, i.e., a sound that is already known and explicitly defined in a given transcription system. Based on this base sound, the grapheme is then constructed by following the diacritics to the left and to the right. If the so-constructed feature bundle already exists in the transcription system, the constructed sound is treated as an alias, if it does not exist, the sound is only marked as being generated. | ```str(TS['d̤ʷ']) == 'dʷʱ'```
