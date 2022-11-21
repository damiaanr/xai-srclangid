# Experiment: word order entropy
The files in this branch contain a very quickly and ugly written experiment concerning word order mistakes in certain specific language pairs.

## Description of experiment
Slavic languages are highly inflective (*i.e.*, they tend to express grammatical markers by morphology instead of syntax). Therefore, Slavic languages are generally characteristic of a more free word order, compared to languages that are less inflective (such as Dutch).

It is therefore expected that the value of a successive PoS tag in Polish is less 'certain' than a succeeding PoS tag in Dutch. Entropy is a good measure to convey such uncertainty. An entropy of `1` means that all PoS tags would be equally likely to succeed a preceeding PoS tag, while an entropy of `0` would indicate that there is only *one* possible PoS tag that could succeed a preceeding PoS tag.

In this experiment, original Dutch samples are compared with original Polish samples and Dutch samples which were translated from Polish.

## Dataset ##

The experiment loads the dataset from the `datasets/scraper-translater` dynamically.