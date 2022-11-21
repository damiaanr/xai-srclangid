from dataset.DatasetManager import *
from functions import *
import spacy

dm = DatasetManager(folder='dataset/output')

nl = dm.get_subset({'lang_ISO639_3': 'dut', 'translated': False})
pl = dm.get_subset({'lang_ISO639_3': 'pol', 'translated': False})
nl_trans = dm.get_subset({'lang_ISO639_3': 'dut', 'translated': True})

occurrences_nl = parse_ads(nl, spacy.load("nl_core_news_lg"))
occurrences_pl = parse_ads(pl, spacy.load("pl_core_news_lg"))
occurrences_nl_trans = parse_ads(nl_trans, spacy.load("nl_core_news_lg"))

probs_nl = probs(occurrences_nl)
probs_pl = probs(occurrences_pl)
probs_nl_trans = probs(occurrences_nl_trans)

e_nl, avg_nl = entropy_per_pos(probs_nl)
e_pl, avg_pl = entropy_per_pos(probs_pl)
e_nl_trans, avg_nl_trans = entropy_per_pos(probs_nl_trans)

# a pretty way to print the results of the experiment
print_labels = ["Dutch", "Polish", "Polish => Dutch"]
print_format = "{:>20}" * 4
print(print_format.format("", *print_labels))

for k in e_nl.keys():
    print(print_format.format(k,
                            round(e_nl[k], 2),
                            round(e_pl[k], 2),
                            round(e_nl_trans[k], 2)))
