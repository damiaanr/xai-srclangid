from nltk import ngrams
from evaluation.bases.wals.src.LanguageDB import *
from .functions import *
from wordorderentropy.functions import probs as wordorder_entropy_probs
from wordorderentropy.functions import entropy_per_pos as entropy_per_gram


class Text:
    """
    This class holds a single sample of text of a certain language and
    contains methods to convert the textual content into features.
    These features can in turn be used for a numerical representation
    of the sample (e.g., a vector containing character n-gram
    occurrence frequencies). Instances of this class are typically held
    and manipulated by an instance of the Languageset() class.

    Feature extraction methods can be of two types:

    [*] Methods that return a list: the occurrence frequency of the
        the individual items in the list are considered the features
        of the sample. Typically, only the top-n most occurring list
        items across a whole language set (represented by a Languageset
        () object that contains multiple Text() objects) are used.
    [*] Methods that return a dict: every item in the dict is consider-
        ed to be a feature; across the whole language set (read above),
        all occurring keys in the dict are taken into account for all
        individual samples (even if a sample does not contain the
        feature in the returned dict).

    Read the description of Experiment and Languageset for more info.
    """

    # following dependencies manual from Stanford (Sep '08)
    DEPS_OBJECT = ['obj', 'dobj', 'iobj', 'pobj']
    DEPS_SUBJECT = ['subj', 'nsubj', 'csubj']

    def __init__(self, text: str, lang_set, lang: str = None):
        """
        Init method.

        In:
          @text:     doc. content as string ('the sample to be parsed')
          @lang_set: pointer to instance of Languageset() that contains
                     this Text() instance
          @lang:     ISO639-3 representation of language of the sample
        """
        self.text = text
        self.lang_set = lang_set

        if lang is not None and lang in iso_639_3_langs:
            self.lang = lang
        else:
            self.lang = None

        self.pos = None  # placeholder to mark text as not PoS-tagged
        self.doc = None  # contains richer tags (not only PoS)

    def get_charngrams(self, n: int = 3) -> list:
        """
        Returns n-length sequences of individual characters (including
        all special characters such as spaces, symbols, emoji's, etc.)

        Warning: The lists that this method produces contain highly
                 varied elements across the dataset. It is therefore
                 recommended to limit the occurrence frequencies used
                 by the svm by the top-n most frequently occuring!

        In:
          @n: integer representing sequence length

        Out:
          @out: list of lists (for every n) of strings of n characters
        """
        out = ["".join(k) for k in list(ngrams(self.text, n=n))]

        return out

    def get_posngrams(self, n: int = 2) -> list:
        """
        Returns n-length sequences of Part-of-Speech (PoS) tags.

        In:
          @n: integer representing length of PoS grams

        Out:
          @out: list of lists (for every n) of lists (for every
                sentence) of n-dimensional tuples with PoS-tags
        """
        if self.pos is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.pos:
            out += list(ngrams(sent, n=n))

        return out

    def get_predicateorder(self) -> list:
        """
        Returns a list of strings containing the chars 'S', 'V', and
        'O' of which their order correspond to the subject-verb-object
        ordering within the sample.

        In:
          - void

        Out:
          @out: list of strings representing patterns encountered in
                the sample (e.g., 'SVO' or 'VOS)
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            if sent.root.pos_ != 'VERB':
                continue

            order = [sent.root.i]  # PoS indices/locations in sample
            types = ['V']  # this is the root/start

            for child in sent.root.children:
                if child.dep_ in self.DEPS_OBJECT:
                    order.append(child.i)
                    types.append('O')
                elif child.dep_ in self.DEPS_SUBJECT:
                    order.append(child.i)
                    types.append('S')

            # sort the characters based on the location within sample
            ordered = sorted(types, key=lambda x: order[types.index(x)])

            out.append("".join(ordered))

        return out

    def get_verbaspect(self) -> list:
        """
        This method returns the verbal aspects encountered in the
        sample (if any). These are either imperfective or perfective.

        In:
          - void

        Out:
          @out: list containing either 'Imperfective' or 'Perfective'
                of reach verb in the sample that was annotated with
                its aspect
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            # make it correspond with get_predicateorder
            if sent.root.pos_ != 'VERB':
                continue

            root_morph = sent.root.morph.to_dict()

            if 'Aspect' in root_morph:
                out.append(root_morph['Aspect'])

        return out

    def get_negations(self) -> list:
        """
        This method counts the occurrence of negative adverb modifiers
        (e.g., in Polish, 'nie').

        In:
          - void

        Out:
          @out: list consiting only of boolean True elements (one for
                every encountered modifier)
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            for token in sent:
                if token.dep_ == 'advmod:neg':
                    out.append(True)

        return out

    def get_cases(self) -> list:
        """
        This method returns the encountered grammatical cases in the
        sample (regardless of the type of speech of word).

        In:
          - void

        Out:
          @out: list of grammatical cases; one entry for each word in
                the sample that was amnnotated with a grammatical case
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            for token in sent:
                token_morph = token.morph.to_dict()

                if 'Case' in token_morph:
                    out.append(token_morph['Case'])

        return out

    def get_adjnounorder(self) -> list:
        """
        This method returns the adjective-noun order patterns that were
        encountered in the sample.

        In:
          - void

        Out:
          @out: list of either 'AN' or 'NA' elements corresponding to
                every combination of nouns and adjectives and their
                ordering within the sentence
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            for token in sent:
                if token.pos_ != 'NOUN':
                    continue

                for child in token.children:
                    if child.pos_ == 'ADJ':
                        if child.i < token.i:
                            out.append('AN')
                            continue
                        else:
                            out.append('NA')
                            continue

        return out

    def get_morphngram(self, n: int = 2) -> list:
        """
        Returns n-length sequences of morphological markings in FEATS
        representation (specified by Universal Dependencies). All words
        included.

        Warning: The lists that this method produces contain highly
                 varied elements across the dataset. It is therefore
                 recommended to limit the occurrence frequencies used
                 by the svm by the top-n most frequently occuring!

        In:
          @n: length of the n-gram; default is bigram

        Out:
          @out: the sample's morphological analyses (per word) split
                into a list with n-gram tuples
        """
        if self.doc is None:
            # below call will throw an exception if lang not supported
            self.lang_set.tag()

        out = []

        for sent in self.doc.sents:
            running_sent = []

            for token in sent:
                running_sent.append(str(token.morph))

            out += list(ngrams(running_sent, n=n))

        return out

    def get_posentropy(self, n: int = 2) -> dict:
        """
        Calculates the entropy (a measure of 'surprise') for PoS-
        n-grams given their (n-1)-gram. The entropy is based on a
        frequentist interpretation of the occurring grams in the text.
        This metric can be used to measure 'word order freedom'.

        In:
          @n: integer indicating length of PoS-grams for which the
              entropy is calculated (i.e., for bigrams/2-grams, entropy
              is calculated per single PoS tag, i.e., every succeeding)

        Out:
          @entropy_per_gram: dict with entropies of next PoS (values)
                             given a PoS-ngram (keys)
        """
        occurrences = {}
        pos_ngrams = self.get_posngrams(n)

        if not pos_ngrams:
            return {}  # empty sample

        for sent in pos_ngrams:
            for i in range(1, len(sent)):  # sent[i] is an n-gram
                if sent[i-1] not in occurrences:
                    occurrences[sent[i-1]] = {}
                if sent[i] not in occurrences[sent[i-1]]:
                    occurrences[sent[i-1]][sent[i]] = 0

                occurrences[sent[i-1]][sent[i]] += 1

        # Note: below functions were originally written for bi-grams
        probs_per_gram = wordorder_entropy_probs(occurrences)
        entropy_per_gram_, average_entropy = entropy_per_gram(probs_per_gram)

        return entropy_per_gram_
