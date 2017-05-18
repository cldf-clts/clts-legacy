Cross-Linguistic Transcription System
=====================================

This is an attempt to create a system that allows to translate and compare different phonetic transcription systems. 

For starters, try this quick example:

```python
>>> from pyclts.clts import CLTS
>>> clts = CLTS()
>>> snd1 = clts.get_sound('ts')
>>> snd2 = asjp.get_sound('c')
>>> snd1.name
'voiceless alveolar affricate consonant'
>>> snd2.name
'voiceless alveolar affricate consonant'
```

You can see that internally, we represent the sounds `ts` and `c`, depending on the alphabet from which they are taking.
