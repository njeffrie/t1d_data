"""Parser for Apple Health export XML data."""

import datetime
from typing import Dict

import tqdm
import xml.etree.ElementTree as ET

import utils


class AppleHealthParser:
    """Parser for Apple Health export XML data.

    This class handles parsing of heart rate (HR) data from Apple Health export XML files.
    """

    HR_TYPE = 'HKQuantityTypeIdentifierHeartRate'

    def __init__(self, fname: str) -> None:
        """Initialize the parser with the XML file.

        Args:
            fname: Path to the Apple Health export XML file.
        """
        self.element_tree = ET.parse(fname)
        self.root = self.element_tree.getroot()
        self._parse_data()

    def _parse_data(self) -> None:
        """Parse all heart rate data in a single pass through the XML.

        This method populates self.hr_entries with data from the XML.
        """
        self.hr_entries: Dict[str, float] = {}

        for elem in tqdm.tqdm(self.root):
            if elem.tag != 'Record':
                continue

            record_type = elem.attrib.get('type')
            if record_type != self.HR_TYPE:
                continue

            start_dt = utils.round(datetime.datetime.fromisoformat(elem.attrib['startDate']))
            value = float(elem.attrib['value'])

            self.hr_entries[start_dt] = value

    def get_all_data(self) -> Dict[str, Dict[str, float]]:
        """Get all heart rate data.

        Returns:
            A dictionary mapping timestamps to dictionaries containing HR values.
            Example:
            {
                '2024-01-01T00:00:00': {
                    'hr': 72.0
                }
            }
        """
        all_data = {}
        for key in self.hr_entries.keys():
            elem = {
                'hr': self.hr_entries.get(key)
            }
            all_data[key] = elem
        return all_data


def main() -> None:
    """Main function to demonstrate parser usage."""
    parser = AppleHealthParser('apple_health_export/export.xml')
    hr_data = parser.get_all_data()
    print(len(hr_data.keys()))


if __name__ == '__main__':
    main()
