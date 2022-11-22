# this file only takes care of arguments input from the command-line
# please refer to the readme or individual code files for more info
# (or run --help)

import argparse
from DatasetManager import *
from translate.Translator import *
from scraper.Scraper import *


# This function prevents invalid input and initiates Translator()
class validate_translate_options(argparse.Action):
    """
    This class is solely used to prevent invalid argument input and to
    initiate Translator(). It inherits Action() (see its docs).
    """
    def __call__(self, parser, args, values, option_string=None):
        """
        @ This method overwrites __call__()-magic of super class
        """
        global t, lang_from, lang_to, profile

        lang_from, lang_to, profile = values

        try:
            t = Translator(profile)
        except Exception:
            raise ValueError('Profile should be one out: '
                             + ', '.join(Translator.PROFILES.keys()))

        valid_languages = t.engine.get_valid_languages()

        if lang_from not in valid_languages or lang_to not in valid_languages:
            raise ValueError('Languages should be among the following: '
                             + ', '.join(valid_languages))

        setattr(args, self.dest, values)


args = argparse.ArgumentParser()


# Either one action needs to be selected: SCRAPE, TRANSLATE, or MERGE
args_main_action = args.add_mutually_exclusive_group(required=True)

args_main_action.add_argument('-scrape',
                              help='Scrape fresh data from the internet',
                              choices=Scraper.PROFILES.keys(),
                              nargs=1,
                              metavar=('PROFILE'))
args_main_action.add_argument('-translate',
                              help='Translate existing data in the dataset',
                              action=validate_translate_options,
                              nargs=3,
                              metavar=('FROM', 'TO', 'PROFILE'))
args_main_action.add_argument('-merge',
                              help='Merges files in the dataset into one',
                              action='store_true')
args_main_action.add_argument('-stats',
                              help='Lists dataset statistics',
                              action='store_true')

# Additional options (applies to all actions)
args.add_argument('-folder',
                  type=str,
                  help='Folder in which dataset is stored',
                  default='output')


# Additional options (applies to SCRAPE and TRANSLATE action)
args.add_argument('-n',
                  type=int,
                  help='Number of items to parse',
                  default=100)

# Additional options (applies only to SCRAPE action)
args.add_argument('-rounds',
                  type=int,
                  help='Number of rounds in which N items are scraped',
                  default=3)
args.add_argument('-roundsleep',
                  type=int,
                  help='Time (in seconds) to sleep after each round',
                  default=30)

args.add_argument('-newid',
                  help='if set, new recent id (e.g., ad id) will be taken'
                  'as starting point for scraping',
                  action='store_true')

args.add_argument('-lang',
                  help='some scraper profiles require a language to be set',
                  default=None)


# Additional options (applies only to TRANSLATE action)
args.add_argument('-type',
                  type=str,
                  help='only translate texts of type (e.g., Marketplace)')

opts = args.parse_args()


# Executing actions
dm = DatasetManager(folder=opts.folder)

if opts.scrape is not None:
    s = Scraper(opts.scrape[0], newid=opts.newid, lang=opts.lang)
    i = 0

    while i < opts.rounds:
        if i > 0:
            # print('Now sleeping for %d seconds' % opts.roundsleep)
            time.sleep(opts.roundsleep)
        response = s.run(opts.n)
        print('')
        if response is False:
            print('Blocked or run out of fresh IDs - all rounds terminated')
            break
        i += 1

    s.save()
elif opts.translate is not None:  # translation option was valid
    data = dm.get_untranslated(lang_from, lang_to,
                               limit=opts.n, type_text=opts.type)
    t.translate(data, lang_from, lang_to)
    t.save()
elif opts.merge:
    dm.merge()
elif opts.stats:
    dm.stats()
