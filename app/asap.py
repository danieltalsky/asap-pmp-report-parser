import re


class InvalidASAPFile(Exception):
    """
    An ASAP file string doesn't have a valid header
    """

    pass


class ASAPSection:
    """
    Represents the fields in an ASAP section

    After parsing the section string, the fields array will have the section header in the 0
    position and the other fields will be indexed with the field number.
    """

    ALLOWED_ASAP_SECTIONS = [
        "TH",
        "IS",
        "PHA",
        "PAT",
        "DSP",
        "PRE",
        "CDI",
        "AIR",
        "TP",
        "TT",
    ]

    DELIMITER_ASAP_FIELD_SEP = "*"

    section_header: str
    fields: list[str]

    def __init__(self, section_string: str):
        self.fields = self.parse(section_string)
        self.section_header = self.fields[0]

    def parse(self, section_string: str) -> list[str]:
        """
        Accepts a field-delimited ASAP section string and returns an ordered list of field strings

        Ex:
        ```
        PRE*1801093810*FC0350152*******
        ```

        @param section_string: a field-delimited string representing a single section
        @return: an ordered list of individual string fields in a section
        """
        return section_string.split(self.DELIMITER_ASAP_FIELD_SEP)

    def get_field_code(self, field_number: int) -> str:
        """
        Creates the field code string from the header and positional integer

        TH + 0 + 2 = TH02
        @param field_number:
        """
        return self.section_header + str(field_number).zfill(2)

    def asdict(self):
        output_dict = {}
        for field_number, field_value in enumerate(self.fields):
            if field_number > 0:
                output_dict[self.get_field_code(field_number)] = field_value
        return output_dict

    def __str__(self):
        output = ""
        for field_number, field_value in enumerate(self.fields):
            if field_number > 0:
                output += f"{self.get_field_code(field_number)}: {field_value}\n"
        return output


class ASAPDispense:
    """
    A group of ASAPSections representing a single dispensed medication and all of its associated information
    """

    DISPENSE_SECTION_HEADERS = [
        "PAT",
        "DSP",
        "PRE",
        "CDI",
        "AIR",
    ]

    sections: list[ASAPSection]

    def __init__(self):
        self.sections = []

    def already_contains(self, new_section: ASAPSection):
        for section in self.sections:
            if new_section.section_header == section.section_header:
                return True
        return False


class ASAP:
    """
    Represents an ASAP report

    Contains an array of ASAPSection objects and an array of ASAPDispense objects
    """

    ASAP_VERIFICATION_HEADER = "TH*"

    REQUIRED_ASAP_SECTIONS = ["TH", "IS", "PHA", "PAT", "DSP", "PRE", "TP", "TT"]

    DELIMITER_ASAP_SECTION = "~"

    # Pulls the field codes like TH03 or AIR12 into two capture groups (TH)(03) or (AIR)(12)
    FIELD_CODE_PATTERN = re.compile(r"([A-Z]{2,3})([0-9]{1,2})")

    sections: list[ASAPSection]
    dispenses: list[ASAPDispense]

    def __init__(self, asap_contents: str):
        self.verify_file_header(asap_contents)
        self.sections = self.parse(asap_contents)
        self.dispenses = self.collect_dispenses()

    def verify_file_header(self, asap_contents: str):
        """
        Verifies the file starts with the first ASAP section header string and a field delimiter: TH*

        Raises an exception if the header isn't found since the file won't be parseable

        @param asap_contents:
        """
        if not asap_contents.startswith(self.ASAP_VERIFICATION_HEADER):
            raise InvalidASAPFile()

    @property
    def unsatisfied_required_sections(self) -> list[str]:
        """
        Lists required section headers that don't exist in the ASAP document

        @return: list of section headers that don't appear
        """
        remaining_required_sections = self.REQUIRED_ASAP_SECTIONS.copy()
        for section in self.sections:
            if section.section_header in remaining_required_sections:
                remaining_required_sections.remove(section.section_header)
        return remaining_required_sections

    def parse(self, asap_contents: str):
        """
        Transforms an ASAP report file string into an array of section strings.

        @param asap_contents:
        @return:
        """
        sections = []

        # This is a quick hack to remove the TH09 field delimiter indicator
        # to allow a quick split.  It just removes the double ~~ created by TH09
        #
        # Note that until this is fixed, the parser will not accept a custom delimiters
        asap_contents.replace(
            self.DELIMITER_ASAP_SECTION * 2, self.DELIMITER_ASAP_SECTION
        )

        asap_section_strings = asap_contents.split(self.DELIMITER_ASAP_SECTION)
        for section_string in asap_section_strings:
            if "*" in section_string:
                asap_section = ASAPSection(section_string)
                sections.append(asap_section)
        return sections

    def collect_dispenses(self) -> list[ASAPDispense]:
        """
        Iterates through the sections array, creating ASAPDispense groups of sections representing a single dispense.

        @return:
        """
        dispenses = []
        open_dispense_record = ASAPDispense()
        for section in self.sections:
            if section.section_header in ASAPDispense.DISPENSE_SECTION_HEADERS:
                # A dispense record can't contain two of the same section so a duplicate means it's a new dispense
                if open_dispense_record.already_contains(section):
                    dispenses.append(open_dispense_record)
                    open_dispense_record = ASAPDispense()
                else:
                    open_dispense_record.sections.append(section)
        return dispenses

    def get_field(self, field_code: str) -> str:
        """
        Gets a field by field code (TH02) in the sections array.

        If there are multiple matches, it naively gets the first match.

        @param field_code: 2-3 digits and a zero padded 2 digit integer
        @return: the field contents string
        """
        field_code_matches = re.search(self.FIELD_CODE_PATTERN, field_code)
        field_header, field_number_string = field_code_matches.groups()
        field_number = int(field_number_string)
        for section in self.sections:
            if (
                section.section_header == field_header
                and len(section.fields) >= field_number
            ):
                return section.fields[field_number]

    def analyze(self):
        """
        Print statistics about an ingested ASAP report
        """
        version = self.get_field("TH01")
        print(f"Detected ASAP report version: {version}")

        print(f"Total valid sections detected: {str(len(self.sections))}")

        unsatisfied_required_sections = self.unsatisfied_required_sections
        if not len(unsatisfied_required_sections) > 0:
            print("All required sections present.")
        else:
            print(f"Required sections not present: {unsatisfied_required_sections}")

        print(f"Total dispenses: {str(len(self.dispenses))}")
