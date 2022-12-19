from sklearn import svm
from sklearn.inspection import permutation_importance
import pickle


def train_test_svm(dataset, linear: bool = False,
                   show_top_imp: int = 15, no_perm_imp: bool = True) -> None:
    """
    Trains a scikit-implementation of an SVM. Tests and prints accuracy
    scores. Aditionally prints an estimation of the 'most important'
    features that led to classifications in the test set. This function
    is just a 'helper function': it already prints everything and does
    not return anything.

    In:
      @dataset:      tuple of the following format: (samples_train,
                     labels_train, samples_test, labels_test,
                     index_labels, index_features); all these elements
                     are described at the Experiment().split_dataset()
                     method, which returns this exact tuple
      @linear:       if True, a standard linear SVM is trained; other-
                     wise, the radial basis functions are its kernel
      @show_top_imp: integer representing number of features to list
                     that are deemed the most contributing factors; for
                     linear SVMs the importance measures are the
                     squares of the coefficients, for rbf-SVMs these
                     are calculated using Permutation Feature Importance
                     (see Scikit documentation 4.2)
      @no_perm_imp:  if set to True, Permutation Feature Importance is
                     skipped (only applies to rbf-kernel SVMs); this
                     can be useful as PFI often takes a very long time

    Out:
      - void
    """
    train_samples, train_labels, test_samples, \
        test_labels, labels_index, feature_keys = dataset

    print('Dataset contained %d total features' % len(feature_keys))

    if linear:
        # model = svm.SVC(kernel='linear', probability=True)
        model = svm.SVC(kernel='linear')
    else:
        model = svm.SVC()  # default is a radial kernel

    model.fit(train_samples, train_labels)
    prediction = model.predict(test_samples)
    correct = (prediction == test_labels).sum()

    print('Accuracy of ' + ('non-' if not linear else '') + 'linear SVM: %.3f'
          % (correct/test_samples.shape[0]))

    zipper = None  # placeholder for 'importance measures'

    if linear:
        zipper = model.coef_[0]**2
    elif not no_perm_imp:
        weights = permutation_importance(model, test_samples, test_labels)
        zipper = weights.importances_mean

    if zipper is not None:
        weight_table = "{:>20}" + "   " + "{:>4}"
        print(weight_table.format('FEATURE', 'IMPORTANCE'))

        for i, fw in enumerate(sorted(zip(feature_keys, zipper),
                                      key=lambda x: x[1], reverse=True)):
            f, w = fw

            if i >= show_top_imp:
                break

            if len(f) < 20:
                feature_string = f
            else:
                feature_string = f[:17] + '...'

            print(weight_table.format(feature_string, round(w, 2)))


# The below dict stores information relating to the (morphological)
# tagger needed to annotate samples of certain languages (to provide
# future flexibility.
pos_tagger_supported = {
    'swe': ('SpaCy', 'sv_core_news_lg'),
    'rum': ('SpaCy', 'ro_core_news_lg'),
    'pol': ('SpaCy', 'pl_core_news_lg'),
    'lit': ('SpaCy', 'lt_core_news_lg'),
    'kor': ('SpaCy', 'ko_core_news_lg'),
    'ita': ('SpaCy', 'it_core_news_lg'),
    'deu': ('SpaCy', 'de_core_news_lg'),
    'fin': ('SpaCy', 'fi_core_news_lg'),
    'eng': ('SpaCy', 'en_core_web_lg'),
    'dut': ('SpaCy', 'nl_core_news_lg'),
    'hrv': ('SpaCy', 'hr_core_news_lg'),
    'chi': ('SpaCy', 'zh_core_web_lg'),
}


# The below list contains all valid 639-3 codes (could be handy).
iso_639_3_langs = [
    'aar',
    'abk',
    'ave',
    'afr',
    'aka',
    'amh',
    'arg',
    'ara',
    'asm',
    'ava',
    'aym',
    'aze',
    'bak',
    'bel',
    'bul',
    'bih',
    'bis',
    'bam',
    'ben',
    'tib',
    'bre',
    'bos',
    'cat',
    'che',
    'cha',
    'cos',
    'cre',
    'ces',
    'chu',
    'chv',
    'wel',
    'dan',
    'deu',
    'div',
    'dzo',
    'ewe',
    'gre',
    'eng',
    'epo',
    'spa',
    'est',
    'baq',
    'per',
    'ful',
    'fin',
    'fij',
    'fao',
    'fre',
    'fry',
    'gle',
    'gla',
    'glg',
    'grn',
    'guj',
    'glv',
    'hau',
    'heb',
    'hin',
    'hmo',
    'hrv',
    'hat',
    'hun',
    'arm',
    'her',
    'ina',
    'ind',
    'ile',
    'ibo',
    'iii',
    'ipk',
    'ido',
    'ice',
    'ita',
    'iku',
    'jpn',
    'jav',
    'geo',
    'kon',
    'kik',
    'kua',
    'kaz',
    'kal',
    'khm',
    'kan',
    'kor',
    'kau',
    'kas',
    'kur',
    'kom',
    'cor',
    'kir',
    'lat',
    'ltz',
    'lug',
    'lim',
    'lin',
    'lao',
    'lit',
    'lub',
    'lav',
    'mlg',
    'mah',
    'mao',
    'mac',
    'mal',
    'mon',
    'mar',
    'may',
    'mlt',
    'bur',
    'nau',
    'nob',
    'nde',
    'nep',
    'ndo',
    'dut',
    'nno',
    'nor',
    'nbl',
    'nav',
    'nya',
    'oci',
    'oji',
    'orm',
    'ori',
    'oss',
    'pan',
    'pli',
    'pol',
    'pus',
    'por',
    'que',
    'roh',
    'run',
    'rum',
    'rus',
    'kin',
    'san',
    'srd',
    'snd',
    'sme',
    'sag',
    'sin',
    'slk',
    'slv',
    'smo',
    'sna',
    'som',
    'alb',
    'srp',
    'ssw',
    'sot',
    'sun',
    'swe',
    'swa',
    'tam',
    'tel',
    'tgk',
    'tha',
    'tir',
    'tuk',
    'tgl',
    'tsn',
    'ton',
    'tur',
    'tso',
    'tat',
    'twi',
    'tah',
    'uig',
    'ukr',
    'urd',
    'uzb',
    'ven',
    'vie',
    'vol',
    'wln',
    'wol',
    'xho',
    'yid',
    'yor',
    'zha',
    'chi',
    'zul',
]
