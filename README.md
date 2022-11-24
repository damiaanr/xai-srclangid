# Experiment: word order entropy
The files in this branch contain a very quickly written experiment concerning word order mistakes in certain specific language pairs.

## Description of experiment
Slavic languages are highly inflective (*i.e.*, they tend to express grammatical markers by morphology instead of syntax). Therefore, Slavic languages are generally characteristic of a more free word order, compared to languages that are less inflective (such as English).

It is therefore expected that the value of a successive PoS tag in Polish is less 'certain' than a succeeding PoS tag in English. Entropy is a good measure to convey such uncertainty. An entropy of `1` means that all PoS tags would be equally likely to succeed a preceeding PoS tag, while an entropy of `0` would indicate that there is only *one* possible PoS tag that could succeed a preceeding PoS tag.

In this experiment, original English samples are compared with original Polish samples, and English samples which were translated from Polish and vice-versa.

## Dataset ##

The experiment loads the dataset from the `datasets/scraper-translater` dynamically.

## Results ##

For 7,500 `Marketplace` samples, scraped from [Vinted.nl](https://vinted.nl/) and [Vinted.co.uk](https://vinted.co.uk/) and translated using `GoogleUnofficial`, the results are shown in the table below. The results are discussed in my thesis project proposal.

|       | `eng` | `pol` | `pol` -> `eng` | `eng` -> `pol` |
|-------|-------|-------|----------------|----------------|
| INTJ  | 0.66  | 0.65  | 0.74           | 0.59           |
| VERB  | 0.81  | 0.81  | 0.76           | 0.8            |
| PROPN | 0.7   | 0.78  | 0.63           | 0.62           |
| PUNCT | 0.82  | 0.8   | 0.76           | 0.83           |
| NOUN  | 0.77  | 0.82  | 0.69           | 0.69           |
| ADJ   | 0.56  | 0.67  | 0.49           | 0.6            |
| ADV   | 0.68  | 0.66  | 0.64           | 0.62           |
| ADP   | 0.66  | 0.44  | 0.62           | 0.46           |
| SPACE | 0.17  | 0.27  | 0.38           | 0.3            |
| NUM   | 0.69  | 0.44  | 0.44           | 0.61           |
| DET   | 0.41  | 0.51  | 0.33           | 0.45           |
| PRON  | 0.72  | 0.77  | 0.59           | 0.82           |
| AUX   | 0.68  | 0.71  | 0.7            | 0.66           |
| CCONJ | 0.76  | 0.73  | 0.77           | 0.77           |
| PART  | 0.55  | 0.78  | 0.51           | 0.76           |
| X     | 0.56  | 0.68  | 0.5            | 0.59           |
| SYM   | 0.39  | 0.68  | 0.48           | 0.77           |
| SCONJ | 0.6   | 0.76  | 0.56           | 0.78           |