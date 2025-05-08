"""Parser for Apple Health export XML data."""

import datetime
from typing import Dict

import tqdm
import xml.etree.ElementTree as ET

import utils


class AppleHealthParser:
    """Parser for Apple Health export XML data.

    This class handles parsing of heart rate variability (HRV) and resting heart rate (RHR)
    data from Apple Health export XML files.
    """

    HRV_TYPE = 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN'
    RHR_TYPE = 'HKQuantityTypeIdentifierRestingHeartRate'

    def __init__(self, fname: str) -> None:
        """Initialize the parser with the XML file.

        Args:
            fname: Path to the Apple Health export XML file.
        """
        self.element_tree = ET.parse(fname)
        self.root = self.element_tree.getroot()
        self._parse_data()

    def _parse_data(self) -> None:
        """Parse all health data in a single pass through the XML.

        This method populates self.hrv_entries and self.rhr_entries with data from the XML.
        """
        self.hrv_entries: Dict[str, float] = {}
        self.rhr_entries: Dict[str, float] = {}

        for elem in tqdm.tqdm(self.root):
            if elem.tag != 'Record':
                continue

            record_type = elem.attrib.get('type')
            if record_type not in [self.HRV_TYPE, self.RHR_TYPE]:
                continue

            start_dt = utils.round(datetime.datetime.fromisoformat(elem.attrib['startDate']))
            value = float(elem.attrib['value'])

            if record_type == self.HRV_TYPE:
                self.hrv_entries[start_dt] = value
            elif record_type == self.RHR_TYPE:
                self.rhr_entries[start_dt] = value

    def get_all_data(self) -> Dict[str, Dict[str, float]]:
        """Get all health data combined.

        Returns:
            A dictionary mapping timestamps to dictionaries containing HRV and RHR values.
            Example:
            {
                '2024-01-01T00:00:00': {
                    'rhr': 60.0,
                    'hrv': 50.0
                }
            }
        """
        all_keys = list(set(list(self.hrv_entries.keys()) + list(self.rhr_entries.keys())))

        all_data = {}
        for key in all_keys:
            elem = {
                'rhr': self.rhr_entries.get(key),
                'hrv': self.hrv_entries.get(key)
            }
            all_data[key] = elem
        return all_data


def main() -> None:
    """Main function to demonstrate parser usage."""
    parser = AppleHealthParser('apple_health_export/export.xml')
    hrv_data = parser.get_all_data()
    print(len(hrv_data.keys()))


if __name__ == '__main__':
    main()
