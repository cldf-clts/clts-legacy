# How to contribute to CLTS

If you contribute, we assume that you forked the data from CLTS first via GitHub and add, for example, a new transcription dataset.
Make sure to add the relevant references for the dataset and fill out the `datasets.tsv`, so we have all relevant information on the datasets. You then need to add your dataset to the `sources` folder and run 

```shell
$ clts td
```

This will load and check your contribution. In order to make sure the data gets changed and the statistics get re-calculated, you now need to run:

```shell
$ clts dump
```

Once this has been done, you can create a pull request and have us review the data.
