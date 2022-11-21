import csv
from typing import Tuple as T


class LanguageDB:
    """
    LanguageDB() is a service-class that provides an interface for
    the WALS database (consisting of .csv-files).
    """
    DATA_PATH = "bases/wals/data/"

    def __init__(self):
        """
        Init (see class description above).

        In:
          - void

        Out:
          n/a
        """
        self.populate_db_defaults()
        self.characteristics_populated = False

    def populate_db_defaults(self) -> None:
        """
        Parses general language data and stores on class-level in two
        different dicts: languages_wals (all data); ..._iso639_3 (only
        WALS ID (for inference)).

        In:
          - void

        Out:
          - void
        """
        with open(self.DATA_PATH + 'languages.csv') as languages_file:
            languages = csv.DictReader(languages_file)

            self.languages_wals = {}
            self.languages_iso639_3 = {}

            # small DB; so this redundancy-for-convenience is not bad
            for entry in languages:
                self.languages_wals[entry['ID']] = entry
                self.languages_iso639_3[entry['ISO639P3code']] = \
                    {'ID': entry['ID']}

    def populate_characteristics(self, explicit: bool = False,
                                 wals_codes: list = None) -> None:
        """
        Parses language-specific characteristics and adds parameters
        and values that apply to languages_wals dict (note: NOT the
        ..._iso639_3 dict). Sets a class-level boolean to True if for
        ALL languages characteristics were parsed.

        In:
          @explicit:   if True, parameter name is stored instead of key
                       important for Language.get_characteristic() etc.
          @wals_codes: list of WALS codes of languages to process; if
                       empty, all languages will be parsed.

        Out:
          - void
        """
        if explicit:  # pre-load meta CSVs
            charc_keys, charc_values = LanguageDB.get_characteristics_fields()

        #  doing this in p..._db_defaults() would make Ø-dicts ambiguous
        if wals_codes:
            for wals_code in wals_codes:
                self.languages_wals[wals_code]['Characteristics'] = {}
        else:
            for wals_code in self.languages_wals:
                self.languages_wals[wals_code]['Characteristics'] = {}

        with open(DATA_PATH + 'values.csv', encoding='utf8') as values_file:
            values = csv.reader(values_file)
            next(values)

            for entry in values:
                if wals_codes and entry[1] not in wals_codes:
                    continue

                if explicit:
                    entry[2] = charc_keys[entry[2]]
                    entry[4] = charc_values[entry[4]]

                self.languages_wals[entry[1]]['Characteristics'][entry[2]] = \
                    entry[4]

        if not wals_codes:
            self.characteristics_populated = True

    def verify_wals_code(self, wals_code: str) -> bool:
        """
        In:
          @wals_code: language code within WALS

        Out:
          @bool: True if language code is valid (exists in WALS DB)
        """
        return True if wals_code in self.languages_wals else False

    def verify_iso639_3_code(self, iso639_3_code: str) -> bool:
        """
        In:
          @iso639_3_code: standardised ISO639-3 language code

        Out:
          @bool: True if language code is valid (exists in WALS DB)
        """
        return True if iso639_3_code in self.languages_iso639_3 else False

    def get_wals_code_by_iso639_3(self, iso639_3_code: str) -> bool:
        """
        In:
          @iso639_3_code: standardised ISO639-3 language code

        Out:
          @wals_code: language code within WALS
        """
        return self.languages_iso639_3[iso639_3_code]['ID']

    def get_characteristics_fields() -> T[dict, dict]:
        """
        Provides a mapping between codes and explicit names for keys
        and values of parameters of language characteristics. Only
        used when language-specific traits are explicitly stored.
        Note: this method is very inefficient if repeatedly called.
        This is a static method.

        In:
          - void

        Out:
          @charc_keys: dict, parameter codes as keys, names as values
          @charc_values: dict, value codes as keys, desc. as values
        """
        charc_keys = {}
        charc_values = {}

        with open(DATA_PATH + 'parameters.csv', encoding='utf8') as keys_file:
            keys = csv.reader(keys_file)

            for key in keys:
                charc_keys[key[0]] = key[1]

        with open(DATA_PATH + 'codes.csv', encoding='utf8') as values_file:
            values = csv.reader(values_file)

            for value in values:
                charc_values[value[0]] = value[2]

        return charc_keys, charc_values
