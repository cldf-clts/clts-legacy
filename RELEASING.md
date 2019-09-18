
Releasing pyclts
================


Preliminary operations
----------------------

The clts repository contains different data, some of which is automatically generated. Given the generative power of transcription systems, we store generated data in files in order to make sure that we can compare the "generative potential" across versions. For this reason, when updating the transcription systems in clts, you will have to run the clts commandline tool in order to make sure the data is re-created accordingly.



The first step here includes running

```shell
$ clts _make_package
```

This code will read in all datasets we have manually assembled in `clts/sources/` and check to which degree the sounds can be rendered in the BIPA transcription system. The data will then be written to `clts/src/pyclts/transcriptiondata/` in form of a flat file per transcription dataset, and to `clts/src/pyclts/soundclasses/lingpy.tsv` (since for the time being, only LingPy's sound classes are included in clts.
Note that for LingPy soundclasses to be accurately generated, `lingpy` needs
to be installed in the latest released version.

After having run these commands, the data should be compared and dumped to two files for convenient access and comparability across versions. In order to do so, run the command

```shell
$ clts dump
```

This will overwrite the two files `data/sounds.tsv` and `data/graphemes.tsv` which reside in the `data` folder of the clts repository. These files are **always** created automatically and should never be manually touched. Once this is done, you can make a pull request to have our core team check the differences in the generated sounds and the available number of different graphemes in the data.


Releasing
---------

- Do platform test via tox:
```
tox -r
```

- Make sure statement coverage is >= 99%
- Make sure flake8 passes:
```
flake8 src
```

- Update the version number, by removing the trailing `.dev0` in:
  - `setup.py`
  - `src/pyclts/__init__.py`

- Create the release commit:
```shell
git commit -a -m "release <VERSION>"
```

- Create a release tag:
```
git tag -a v<VERSION> -m"<VERSION> release"
```

- Release to PyPI (see https://github.com/di/markdown-description-example/issues/1#issuecomment-374474296):
```shell
python setup.py clean --all
rm dist/*
python setup.py sdist
twine upload dist/*
rm dist/*
python setup.py bdist_wheel
twine upload dist/*
```

- Push to github:
```
git push origin
git push --tags
```

- Increment version number and append `.dev0` to the version number for the new development cycle:
  - `src/pyclts/__init__.py`
  - `setup.py`

- Commit/push the version change:
```shell
git commit -a -m "bump version for development"
git push origin
```
