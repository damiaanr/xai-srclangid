# Damiaan's MSc AI thesis repository

This private repository holds the code of all (sub)projects relevant to my thesis. I will try to keep it as organised as possible, which might be a challenge as it will contain multiple, independent projects which would normally have their own repository.

All code is documented, type annotated (unless it concerns methods that overwrite already documented methods from existing classes) and PEP8-compliant. All code is written with the aim to rely on as less external libraries as possible.

## Projects 


To keep a clear overview, this repository contains several orphan branches, *i.e.* branches that function as stand-alone branches. Each holds a separate project, some of which are dynamically loaded (as a submodule) within other branches. Each branch contains a `requirements.txt` file and a separate `README.md` with a description.

Currently, the repository contains the following projects:

- `datasets/scraper-translator` Small framework that manages a dynamic dataset and allows for plug-and-play scrapers and translators.
- `evaluation` Small framework that offers multiple ways of evaluating the eventual model's behaviour.
- `experiments/wordorder-entropy` Quick experiment relating to word order mistakes when translating specific language pairs.
- `experiments/svm-vinted` Initial attempt at the source language identification task using manually designed language-specific features.