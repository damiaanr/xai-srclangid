# Datasets: scraper & translator

This small command-line program manages a dataset of text samples dynamically. Samples can be added by either scraping or translating. The tool has been written with the aim of providing an easy way for adding different scrapers and translators.

Note that this tool is highly inefficient for usage *in production*: it is meant as an initial starting point for a dataset which can be converted easily to more efficient data representations.

## Usage
Run `main.py -help` to invoke a detailed overview of all possible actions.

### Examples

1. Run `main.py -scrape Sprzedajemy -n 100 -rounds 5 -roundsleep 60` to add a total of 500 new samples to the dataset, scraped from [Sprzedajemy.pl](https://sprzedajemy.pl), in 5 rounds with a minute of cool-down time in between.
2. Run `main.py -translate pol dut GoogleUnofficial -n 40` to translate 40 Polish samples from the dataset into Dutch using an unofficial Google Translate API endpoint. Only original Polish texts which have not been translated into Dutch will be selected.
3. Run `main.py -stats` to overview the contents of the dataset (*i.e.*, the amount of samples per language, and the number of translations).
## Instruments
*Note: some of the instruments below contain hard-coded values for certain parameters, such as the time of sleeping (in second) between HTTP requests. This is a deliberate choice as their values were set on the basis of empirical evidence during experimental testing.*
### Scrapers
Currently, there are **two** scrapers working stably.

- `MarktplaatsScraper` scrapes `Marketplace` content from platform [Marktplaats.nl](https://marktplaats.nl) in `dut` (Dutch)
- `SprzedajemyScraper` scrapes `Marketplace` content from platform [Sprzedajemy.pl](https://sprzedajemy.pl) in `pol` (Polish)

### Translators
Currently, there is **one** translator working stably.

- `GoogleUnofficial` translates using an old Google API endpoint (lower in quality than the live version of Google Translate)

## Dataset
The dataset consists of all `.yaml` files in a defined folder (default: `output`). Each file contains a set of text samples, which are the individual elements in the dataset.
### Format
Each sample (element) in the dataset can hold the following attributes:
- **`identifier`** internal ID of the sample (translated samples are represented by the same identifier as the original sample)
- **`lang_ISO639_3`** language of text corresponding to the sample (if the sample translated, this attribute will havae the translated language as its value)
- `lang_ISO639_3_original` original language of the text sample (only if the element concerns a translated sample)
- `sentences` a split into separate sentences within the text corresponding to the sample (only applies when the element considers a translated sample using a translation engine which supports splitting into sentences)
- **`source`** source of the text sample (*i.e.*, name of the platform from which the sample was scraped)
- **`text`** the text corresponding to the sample
- **`translated`** Boolean value indicating whether the sample was translated or not
- `translation_vendor` engine using which the sample was translated (if applicable)
- **`type`** type of the textual content (currently only `Marketplace` is supported)

*Note: bold keys indicate mandatory values*