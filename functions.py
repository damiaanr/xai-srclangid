import spacy
import math
from typing import Tuple as T


def parse_ads(ads: list, nlp: spacy.lang):
    """
    Counts the occurrences of two PoS tags occuring sequentially on
    the sentence level.

    In:
      @ads: Subset of dataset; list of dataset sample elements
      @nlp: Spacy Language object returned by spacy.load()

    Out:
      @occurrences: Dict with PoS-tags as keys and a nested dict as
                    their values. The nested dict likewise contains
                    PoS tags as keys, but holds the frequencies of the
                    PoS-tag corresponding to the nested-dict's keys
                    occuring after the PoS tag corresponding to the
                    outer-dict's keys (essentialy 2gram PoS-tags).
    """
    occurrences = {}

    for ad in ads:
        doc = nlp(ad['text'])
        for sent in doc.sents:
            for i in range(1, len(sent)):
                if sent[i-1].pos_ not in occurrences:
                    occurrences[sent[i-1].pos_] = {}
                if sent[i].pos_ not in occurrences[sent[i-1].pos_]:
                    occurrences[sent[i-1].pos_][sent[i].pos_] = 0

                occurrences[sent[i-1].pos_][sent[i].pos_] += 1

    return occurrences


def probs(occurrences: dict) -> dict:
    """
    Converts occurrence frequencies of sequantial PoS tags into
    frequentist probabilities.

    In:
      @occurrences: Nested dict containing occurence values of two PoS
                    tags in sequence

    Out:
      @probs:       Nested dict containing frequentist probabilities
                    for two PoS tags occuring sequentially
    """
    probs = {}

    for ppos in occurrences:
        ppos_sum = sum(occurrences[ppos].values())
        probs[ppos] = {}

        for spos in occurrences[ppos]:
            prob = occurrences[ppos][spos] / ppos_sum
            probs[ppos][spos] = prob

    return probs


def entropy_per_pos(probs: dict) -> T[dict, float]:
    """
    Calculates the entropy for the range of PoS tags that can occur
    after a certain PoS tag.

    In:
      @probs: Dict containing dicts with frequentist probability values
              for two PoS tags occuring sequentially; format:
              [firsttag][secondtag] = probability-of-second-after-first

    Out:
      @entropies: Input with nested dicts converted to entropy values
      @float:     Average entropy over all PoS tags
    """
    if len(probs) == 0:
        raise Exception("Empty dict given!")

    entropies = {}

    for ppos in probs:
        ppos_entropy = 0
        if len(probs[ppos]) == 1:
            entropies[ppos] = 0
            continue

        for spos in probs[ppos]:
            log = math.log(probs[ppos][spos], len(probs[ppos]))
            ppos_spos_entropy = probs[ppos][spos] * log
            ppos_entropy += ppos_spos_entropy
        entropies[ppos] = -ppos_entropy

    average_entropy = sum(entropies.values()) / len(entropies)

    return entropies, average_entropy
