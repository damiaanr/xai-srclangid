from dataset.DatasetManager import *
from functions import *
import spacy

n = 7500  # number of samples

dm = DatasetManager(folder='dataset/output')

# original texts
en = dm.get_subset({'lang_ISO639_3': 'eng',
                    'translated': False,
                    'source': 'Vinted'})[:n]
pl = dm.get_subset({'lang_ISO639_3': 'pol',
                    'translated': False,
                    'source': 'Vinted'})[:n]

# translated texts
en_t = dm.get_subset({'lang_ISO639_3': 'eng',
                      'lang_ISO639_3_original': 'pol',
                      'translated': True,
                      'source': 'Vinted'})[:n]
pl_t = dm.get_subset({'lang_ISO639_3': 'pol',
                      'lang_ISO639_3_original': 'eng',
                      'translated': True,
                      'source': 'Vinted'})[:n]

occurrences_en = parse_ads(en, spacy.load("en_core_web_trf"))
occurrences_pl = parse_ads(pl, spacy.load("pl_core_news_lg"))
occurrences_en_t = parse_ads(en_t, spacy.load("en_core_web_trf"))
occurrences_pl_t = parse_ads(pl_t, spacy.load("pl_core_news_lg"))

probs_en = probs(occurrences_en)
probs_pl = probs(occurrences_pl)
probs_en_t = probs(occurrences_en_t)
probs_pl_t = probs(occurrences_pl_t)

e_en, avg_en = entropy_per_pos(probs_en)
e_pl, avg_pl = entropy_per_pos(probs_pl)
e_en_t, avg_en_t = entropy_per_pos(probs_en_t)
e_pl_t, avg_pl_t = entropy_per_pos(probs_pl_t)

# print the results of the experiment
print_labels = ["Eng (Avg. " + str(round(avg_en, 2)) + ")",
                "Pol (Avg. " + str(round(avg_pl, 2)) + ")",
                "Pol -> Eng (μ=" + str(round(avg_en_t, 2)) + ")",
                "Eng -> Pol (μ=" + str(round(avg_pl_t, 2)) + ")"]
print_format = "{:>9}" + "{:>19}" * 2 + "{:>23}" * 2
print(print_format.format("", *print_labels))

for k in e_en.keys():
    print(print_format.format(k,
                              round(e_en[k], 2) if k in e_en else 'n/a',
                              round(e_pl[k], 2) if k in e_en else 'n/a',
                              round(e_en_t[k], 2) if k in e_en_t else 'n/a',
                              round(e_pl_t[k], 2) if k in e_pl_t else 'n/a',))
