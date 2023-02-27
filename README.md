# Experiment: SVM on scraped Vinted texts
This branch contains an initial attempt to identify the source language of machine-translated Vinted advertisement texts using hand-crafted features designed to capture the specific characteristics of individual languages. In the future, these features should be learned by a model (and related to certain language-specific elements) instead of manually designed.

*Note: the `requirements.txt`-file also contains the (sometimes large) SpaCy models fit to individual languages.*

## Dataset ##
The dataset contains 7,500 `Marketplace` samples for each language, scraped from various locales of Vinted (*e.g.*, [Vinted.nl](https://vinted.nl/) or [Vinted.lt](https://vinted.lt/)). The dataset is challenging as many samples contain only single sentences that are moreover often ungrammatical in nature (*e.g.*, 'nice dress never worn'). The languages included in this experiment are `lit`, `deu`, `ces`, `dut`, `eng`, `pol`, and `slk`. All samples were translated into `eng` and `pol` using `GoogleUnofficial`. The experiment loads the dataset from the `datasets/scraper-translater` dynamically.

## Discriminating between original and translated Polish texts ##
The first experiment (`experiment1.py`) trains a linear SVM on 12,000 samples of which 6,000 are original texts in `pol` from [Vinted.pl](https://vinted.pl/), and 6,000 samples are Polish texts translated from `eng`. The test set contains 3,000 samples (1,500 each). The SVM model was chosen to be linear because of the higher degree of explainability of linear models. Inspired by the specifics of the Polish language (especially its high morphologicity), the following features were hand-crafted for this task:

- **`predicateorder`** The order of subject, predicate, and object in a sentence (*e.g.*, SVO, OVS, etc.). Each occurring pattern in the dataset forms a class and the frequencies of each pattern in a single sample are counted—the counts form the features on which the SVM is trained. As word order in Polish is generally considered to be more free while in English it is more strict, it is expected that original Polish samples generally contain a higher variety of predicate—subject—object orders.
- **`verbaspect`** The verbal aspects (either perfective or imperfective) are counted for each verb that occurs in an individual sample. In Slavic languages, the verbal aspect was developed very explicitly. As a consequence, most Slavic L2 learners struggle with choosing the correct aspect. Therefore, it is expected that machine translation also suffers from verbal-aspect errors. The occurrence frequencies of both aspects form the features for the SVM.
- **`negations`** Like French, the Polish language incorporates a double negation. It is hypothesized that machine translators make mistakes when formulating this type of negations when translating from a language that does not have a double negation. This feature simply counts all occurrences of negative adverb modifiers (in Polish, this should only be the word **nie**).
- **`cases`** Polish is a highly inflected language and morphologically marks words using seven cases (naamvallen). Again, following the experiences of L2 learners, it is expected that machine translation engines make mistakes when choosing the correct case. The features fed to the SVM consist of the occurrence counts for each case marking in an individual sample.
- **`adjnounorder`** While in English, an adjective should generally always be placed before a noun, in Polish, the adjective can be placed after the noun as well. It may therefore be the case that machine translations between these languages contain unnatural adjective—noun word orderings. The features corresponding to this topic simply consist of counts for either adjective—noun or noun—adjective constructions in each individual sample.
- **`posentropy`** See `experiments/wordorder-entropy` (branch).

When concatenating all of the above features into a single representation vector for each individual sample, the accuracy of the classifier was reported to be `0.712` with a linear SVM (and `0.726` with a radial basis). Note that the random chance baseline is `0.5`. The top 15 most important features (squared coefficients) were the features listed below:

| FEATURE             | WEIGHT^2 |
|---------------------|----------|
| predicateorder: OVS | 3.88     |
| predicateorder: SOV | 1.14     |
| verbaspect: Imp     | 1.02     |
| posentropy: SCONJ   | 0.54     |
| predicateorder: OV  | 0.41     |
| posentropy: CCONJ   | 0.4      |
| predicateorder: VSO | 0.39     |
| posentropy: ADJ     | 0.31     |
| posentropy: NOUN    | 0.3      |
| predicateorder: VS  | 0.3      |
| adjnounorder: NA    | 0.28     |
| posentropy: DET     | 0.23     |
| posentropy: PROPN   | 0.22     |
| predicateorder: SVO | 0.18     |
| posentropy: PART    | 0.17     |

Interestingly, for the non-linear SVM, the top five was as follows: *cases: Nom, adjnounorder: AN, adjnounorder: NA, posentropy: NOUN, verbaspect: Imp*. Predicate-order features didn't even feature in the top 15.

When training the linear classifier with only one out of the six above-listed feature sets, the following accuracy scores were achieved:

| feature set      | accuracy | difference with baseline | classes |
|------------------|----------|--------------------------|---------|
| `predicateorder` | 0.553    | +0.053 (+0.086 unrstrc.) | 10 (127)|
| `verbaspect`     | 0.597    | +0.097 (+0.097 unrstrc.) | 2 (3)   |
| `negations`      | 0.519    | +0.019                   | 1       |
| `cases`          | 0.556    | +0.056                   | 7       |
| `adjnounorder`   | 0.636    | +0.136                   | 2       |
| `posentropy`     | 0.645    | +0.145 (+0.235 unrstrc.) | 14 (18)  |
| **all of above** | 0.712    | +0.212 (+0.274 unrstrc.) | 36 (158)|

When considering 'classical' features for the classification tasks (i.e., character *n*-grams, PoS *n*-grams and morph-*n*-grams; see `experiment1.py` for the details) the accuracy was `0.939` for a linear SVM.

*Note: a few restrictions were in place during the experiment (e.g., SYM, PUNCT, and SPACE PoS-tags were excluded from the `posentropy`-category. See `experiment1.py` for the specifics. Without these restrictions, the accuracy was `0.774` for a linear SVM (`0.781` for a non-linear rbf SVM). See the table above for the individual total difference (from random chance baseline) in accuracy scores.*

*Another note: after clearing the cache and re-fetching all samples and recalculating their features, the resulting accuracy scores differed slightly. The scores reported above stem from earlier calculations.* 

## Multi-lingual source language identification ##
*This experiment is currently in process*
