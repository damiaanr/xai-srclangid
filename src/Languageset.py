from dataset.DatasetManager import *
from .functions import *
from .Text import Text
import pickle
import copy
import spacy


class Languageset:
    """
    The Languageset class holds a single category(/class) of samples.
    Each category is identified by the language of the class, and, if
    translated, the source language of the translation. Categories can
    also be distinguished by additional characteristics. A set of
    samples can additionally be annotated by, e.g., PoS tags. All
    samples are saved in cache to prevent load times in the future.
    """
    SAMPLES_SOURCE = "Vinted"  # should support multiple languages
    CACHE_FOLDER = '../cache/'
    LOAD_FROM_DATAMANAGER_IF_NOT_STORED_IN_CACHE = True

    def __init__(self, lang: str, translated: bool, num_samples: int,
                 lang_source: str = None, load_from_cache: bool = True,
                 distinguisher: str = None):
        """
        Init method. Immediately loads all samples.

        In:
          @lang:            ISO639-3 code of the language of which the
                            samples in this set need to consist; if
                            @translated is True, this parameter should
                            contain the language into which the samples
                            were translated from @lang_source
          @translated:      if False, samples consist of original texts
                            where @lang is the source language; if
                            True, samples consist of translated texts
                            (and @lang_source should be set)
          @num_samples:     number of samples to be loaded (an excep-
                            tion will be thrown if too less samples are
                            available)
          @lang_source:     if @translated is True, this parameter
                            could contain the ISO639-3 code of the
                            original language that was translated into
                            @lang (otherwise, samples might originate
                            from different source languages)
          @load_from_cache: bool; if True, load the samples from a
                            stored pickle (if possible) instead of from
                            the DatasetManager (which is very slow)
          @distinguisher:   an optional additional string that distin-
                            guishes the category/class of the samples
                            constained within this class instance from
                            other samples in the overall dataset
        """

        self.lang = lang
        self.translated = translated
        self.lang_source = lang_source

        # pre-set cache file path and name prefix
        self.cache_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), self.CACHE_FOLDER)

        self.identifier = self.lang  # also used within Experiment()

        if self.translated:
            if self.lang_source is None:
                raise Exception("source language should be described!")
            self.identifier += "_" + self.lang_source

        if distinguisher is not None:
            self.identifier += "_" + self.distinguisher

        self.cache_prefix = self.cache_path + 'cat_' + self.identifier + '__'

        # load samples
        if load_from_cache:
            try:
                self.load_from_cache()
            except Exception as e:
                print(e)

                if self.LOAD_FROM_DATAMANAGER_IF_NOT_STORED_IN_CACHE:
                    self.load_from_datasetmanager(num_samples)
                    self.save_to_cache()
                else:
                    raise Exception("could not load from cache")

            if len(self.samples) < num_samples:
                raise Exception("cache did not contain enough samples")
            elif len(self.samples) != num_samples:
                self.samples = self.samples[:num_samples]
        else:
            self.load_from_datasetmanager(num_samples)
            self.save_to_cache()

    def load_from_datasetmanager(self, num_samples: int) -> None:
        """
        Loads samples from the DatasetManager()-framework, which is an
        independent program used for scraping and translating samples.

        Warning: since I wrote the DatasetManager not with efficiency
        in mind (but rather flexibility), load times can be VERY high.

        In:
          @num_samples: number of samples to extract from the dataset;
                        to prevent overseeing statistical mistakes,
                        method will throw an Exception if too less
                        samples could be fetched

        Out:
          - void
        """

        dm = DatasetManager(folder='dataset/output')
        samples = dm.get_subset({'lang_ISO639_3': self.lang,
                                 'translated': self.translated,
                                 'source': self.SAMPLES_SOURCE})

        if len(samples) < num_samples:
            raise Exception("could not fetch enough samples")
        elif len(samples) != num_samples:
            samples = samples[:num_samples]

        self.samples = []

        for sample in samples:
            self.samples.append(Text(sample['text'],
                                lang_set=self,
                                lang=self.lang))

    def save_to_cache(self) -> None:
        """
        Save the whole list of samples to the cache. Note: this method
        could be called in different 'phases' of constructing the list
        of samples (i.e., also after annotating with PoS-tags, etc.).
        Samples are stored within a pickle file. SpaCy Doc() objects
        are stored external to the Text() objects.

        In:
          - void
        Out:
          - void
        """

        cache_file = self.cache_prefix + str(time.time()) + '.p'

        samples = copy.deepcopy(self.samples)  # these will be modified

        for i, sample in enumerate(samples):
            if i == 0:
                if sample.doc is None:
                    doc_bin = None
                else:
                    doc_bin = spacy.tokens.DocBin()  # more efficient

            if sample.doc is not None:
                doc_bin.add(sample.doc)
                sample.doc = None  # will be serialized independently

            sample.lang_set = None  # could become extremely large

        if doc_bin is not None:
            doc_bin = doc_bin.to_bytes()

        data = doc_bin, samples

        pickle.dump(data, open(cache_file, 'wb'))

    def load_from_cache(self, cache_file: str = None) -> None:
        """
        Loads samples from a pickle file into the object. If no
        specific cache_file was specified, the latest modified pickle
        with the SAME category identifier (as defined in __init__()
        will be loaded).

        In:
          @cache_file: optional filename (including extension, ex-
                       cluding path) of pickle to be loaded

        Out:
          - void
        """

        if cache_file is None:
            # annotated cache files should always be the latest
            latest_files = glob.glob(self.cache_prefix + '*.p')

            if latest_files:
                cache_file = max(latest_files, key=os.path.getctime)
            else:
                raise Exception("no cache file found")
        else:
            cache_file = self.CACHE_FOLDER + cache_file

        # if set was tagged using SpaCy, the Doc()'s were serialized
        # independently from the Text() objects and need to be loaded
        doc_bin, self.samples = pickle.load(open(cache_file, "rb"))

        if doc_bin is not None:
            doc_bin = spacy.tokens.DocBin().from_bytes(doc_bin)
            spacy_model = pos_tagger_supported[self.lang][1]
            self.spacy_nlp = spacy.load(spacy_model)
            docs = list(doc_bin.get_docs(self.spacy_nlp.vocab))

        for i, sample in enumerate(self.samples):
            sample.lang_set = self  # were also erased for efficiency

            if doc_bin is not None:
                sample.doc = docs[i]
                assert sample.doc.text == sample.text

            doc_bin.add(sample.doc)

        if doc_bin is not None:
            del self.spacy_nlp  # not needed

    def tag(self) -> None:
        """
        If supported for the language of the current set, this method
        splits the text of all contained samples into sentences and
        tags every word within every sentence with annotations, such as
        Part-of-Speech (PoS)-tags, and stores them internally.

        Currently, the following (external) taggers are utilised:

        [*] SpaCy: for swe, rum, pol, lit, kor, ita, deu, fin, eng,
                       dut, hrv, chi

        In:
          - void

        Out:
          - void
        """
        if self.lang not in pos_tagger_supported.keys():
            raise Exception("PoS-tagging not supported for this language")

        tagger, model = pos_tagger_supported[self.lang]

        if tagger == "SpaCy":
            self.spacy_nlp = spacy.load(model)

            for sample in self.samples:
                sample.doc = self.spacy_nlp(sample.text)

                sample_pos = []

                for sent in sample.doc.sents:
                    sent_pos = []

                    for token in sent:
                        sent_pos.append(token.pos_)

                    sample_pos.append(sent_pos)

                sample.pos = sample_pos

            del self.spacy_nlp  # otherwise cache contains whole model

        self.cache_prefix += 'tagged_'
        self.save_to_cache()
