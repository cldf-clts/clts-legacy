# Collection of Exemplary Scripts with CLTS

## `phoible.py`

This code illustrates how a subset of phoible consonants can be checked and how important the generative aspect of CLTS is to allow to describe larger numbers of sounds. The code accesses the most recent data from phoible and then tries to parse all phoible sounds with the function ```CLTS().get_sound```. This time, we only select consonants, and we only count how many consonants are explained by taking those where phoible has the exactly identical string to represent the sound. We then apply to checks:

1. we test whether the form is generated or not (and display this by markign generated forms with an asterisk)
2. we test how well the name-strings we give to the sounds (they are all displayed in the last column) conform to the criterion of uniqueness (they should only denote one sound not more).

It turns out, that our current version of CLTS has identical symbols for 327 phoible consonants. You will further see that we capture all most frequent ones. Furthermore, it is surprising that the majority of these consonants is actually generated, thus showing how important it is to have a generative built-in procedure for sounds from IPA symbols. Third, given that our check does not show any cases where the name-identifiers are not unique, this shows that we are also on the right track and that our current CLTS can express 327 distinct sounds with the naming principle, drawn from phoible.


