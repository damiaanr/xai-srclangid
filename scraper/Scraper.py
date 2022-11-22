from .platforms.Sprzedajemy.Scraper import *
from .platforms.Marktplaats.Scraper import *
from .platforms.Vinted.Scraper import *
import yaml
import time


class Scraper:
    """
    This main Scraper class handles instances of specific scraper clas-
    ses dynamically and keeps track of IO for the dataset files.
    """

    # All compatible scrapers should be hard-listed here
    PROFILES = {
        'Sprzedajemy': {'lang_ISO639_3': 'pol', 'type': 'Marketplace'},
        'Marktplaats': {'lang_ISO639_3': 'dut', 'type': 'Marketplace'},
        'Vinted': {'type': 'Marketplace'}
    }

    def __init__(self, profile: str, output_folder: str = 'output',
                 newid: bool = False, lang: str = None) -> None:
        """
        Init (see general class description above).

        In:
          @profile:       Platform to scrape (see global PROFILES)
          @output_folder: Folder in which new samples will be stored
          @newid:         See documentation for the platform-specific
                          classes to which this setting applies (note:
                          this might not be supported by all profiles)
          @lang:          If profile supports multiple languages (i.e.,
                          lacks key 'lang_ISO639_3' in above global),
                          language can be manually specified.

        Out:
          n/a
        """
        if profile not in self.PROFILES:
            raise Exception("Scraping profile does not exist")

        scraperclass = globals()[profile + "Scraper"]  # dynamic load

        if 'lang_ISO639_3' not in self.PROFILES[profile]:
            if not lang:
                raise Exception("Language must be specified for this profile")

            self.scraper = scraperclass(lang=lang)
            self.lang = lang
        else:
            self.scraper = scraperclass(get_new_last_id=newid)

        self.profile = profile
        self.data = []

        self.output_folder = output_folder

    def run(self, iterations: int) -> None:
        """
        Fetches samples from the platform-specific scrapers and
        organises these into representations suitable for the dataset.
        Samples are stored in the class instance and should be manually
        saved using save().

        In:
          @iterations: Integer denoting number of samples to be fetched

        Out:
          - void
        """
        i = 0

        while i < iterations:
            try:
                data_element = self.PROFILES[self.profile].copy()

                if 'lang_ISO639_3' not in data_element:
                    data_element['lang_ISO639_3'] = self.lang

                data_element['source'] = self.profile
                data_element['text'] = self.scraper.next_item()
                data_element['translated'] = False

                # since all scrapers sleep, the below line denotes a
                # safe identifier for which nothing needs to be stored
                identifier = int(str(time.time()).replace('.', ''))
                data_element['identifier'] = identifier

                self.data.append(data_element)

                print('\r'+'Parsed text %d/%d' % (i+1, iterations), end='')
            except Exception as error:
                print('\r\n'+'Round terminated (see error below)')
                if error.args[0] == "blocked" or error.args[0] == "runout":
                    return False

                print(error)
                break

            i += 1

    def save(self, file_name: str = None) -> None:
        """
        Writes all fetched samples to a separate file in the dataset
        folder. Destructs instance of specific scraper class so that
        the cache relevant to the relevant platform is saved.

        In:
          @file_name: filename (excluding extension); if None, the
                      current timestamp (with decimals) will be taken

        Out:
          - void
        """
        del self.scraper

        if file_name is None:
            file_name = str(time.time())

        with open(self.output_folder + '/' + file_name + '.yaml', 'w') as out:
            documents = yaml.dump(self.data, out)
