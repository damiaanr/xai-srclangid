from src.Experiment import *
from src.functions import train_test_svm

#######################################################################
#                             EXPERIMENT A
#######################################################################

# First we experiment with manually designed features
e = Experiment(num_samples=7500)

e.add_language(lang='pol', translated=False)
e.add_language(lang='pol', translated=True, lang_source='eng')

e.add_features(feature='posentropy',
               options={'n': 2},
               ignore=['SPACE', 'SYM', 'X', 'PUNCT'])
e.add_features(feature='predicateorder',
               focus=['SVO', 'SV', 'SOV', 'OV', 'VOS', 'VO',
                      'VSO', 'VS', 'OVS', 'OV', 'OSV', 'SV'])
e.add_features(feature='verbaspect', focus=['Imp', 'Perf'])
e.add_features(feature='adjnounorder')
e.add_features(feature='cases')
e.add_features(feature='negations')

dataset = e.split_dataset()

# Linear
train_test_svm(dataset, linear=True)

# versus radial basis
train_test_svm(dataset, linear=False, no_perm_imp=False)


#######################################################################
#                             EXPERIMENT B
#######################################################################

# Now, we repeat the experiment with more general features
e2 = Experiment(num_samples=7500)

e2.add_language(lang='pol', translated=False)
e2.add_language(lang='pol', translated=True, lang_source='eng')

e2.add_features(feature='charngrams', options={'n': 3}, top_n=100)
e2.add_features(feature='posngrams', options={'n': 3})
e2.add_features(feature='charngrams', options={'n': 2}, top_n=250)
e2.add_features(feature='posngrams', options={'n': 2})
e2.add_features(feature='morphngram', top_n=250)
e2.add_features(feature='morphngram', options={'n': 3}, top_n=100)

dataset2 = e2.split_dataset()

train_test_svm(dataset2, linear=True)
train_test_svm(dataset2, linear=False)
