from html.parser import HTMLParser


class AdParser(HTMLParser):
    """
    This class inherits the builtin HTML Parser and extracts the raw
    texts of advertisements on Marktplaats.nl.
    """
    def __init__(self):
        """
        Init (see class description above). In/out void.
        """
        super().__init__()
        self.capture = False
        self.captured_text = ""
        self.nested_divs = 0

    def yield_text(self) -> str:
        """
        Returns the stored texts and resets the AdParser so that the
        instance can be used again for different HTML documents.

        In:
          - void

        Out:
          @text: Raw contents of advertisement (stripped HTML)
        """
        if self.captured_text == "":
            return False

        yielded_text = self.captured_text
        self.captured_text = ""
        return yielded_text

    def handle_starttag(self, tag, attrs):
        """
        Starts capturing the innerHTML of elements after encountering
        the main <div>-tag of an advertisement; converts <br> to space.

        @ This method overwrites handle_starttag() of super class
        """
        if tag == 'div' and self.capture:
            self.nested_divs += 1
        elif (tag == 'div'
                and attrs
                and attrs[0][0] == 'class'
                and attrs[0][1] == 'Description-description'):
            self.capture = True
        elif tag == 'br' and self.capture:
            self.captured_text += " "

    def handle_endtag(self, tag):
        """
        Allows for nested <div>s within the main <div>. Also see
        handle_starttag().

        @ This method overwrites handle_endtag() of super class
        """
        if tag == 'div' and self.capture:
            if self.nested_divs > 0:
                self.nested_divs -= 1
            else:
                self.capture = False

    def handle_data(self, data):
        """
        Simply stores innerHTML of encountered elements in class.

        @ This method overwrites handle_endtag() of super class

        """
        if self.capture:
            self.captured_text += data
