import xml.etree.ElementTree as ET
import utils
from datetime import datetime

tree = ET.parse('apple_health_export/export.xml')
root = tree.getroot()

class AppleHealthParser:
    HRV_TYPE = 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN'
    RHR_TYPE = 'HKQuantityTypeIdentifierRestingHeartRate'
    def __init__(self, fname):
        self.element_tree = ET.parse(fname)
        self.root = self.element_tree.getroot()

    def get_hrv(self) -> dict:
        hrv_entries = {}
        for elem in self.root:
            if elem.tag == 'Record' and elem.attrib['type'] == self.HRV_TYPE:
                start_dt = utils.round(datetime.fromisoformat(elem.attrib['startDate']))
                hrv_entries[start_dt] = float(elem.attrib['value'])
        return hrv_entries

    def get_rhr(self) -> dict:
        rhr_entries = {}
        for elem in self.root:
            if elem.tag == 'Record' and elem.attrib['type'] == self.RHR_TYPE:
                start_dt = utils.round(datetime.fromisoformat(elem.attrib['startDate']))
                rhr_entries[start_dt] = float(elem.attrib['value'])
        return rhr_entries

    def get_all_data(self) -> dict:
        hrv_data = self.get_hrv()
        rhr_data = self.get_rhr()

        # First convert both to lists, append, then deduplicate.
        all_keys = list(set(list(hrv_data.keys()) + list(rhr_data.keys())))

        all_data = {}
        for key in all_keys:
            elem = {}
            elem['rhr'] = rhr_data[key] if key in rhr_data.keys() else None
            elem['hrv'] = hrv_data[key] if key in hrv_data.keys() else None
            all_data[key] = elem
        return all_data



if __name__ == '__main__':
    parser = AppleHealthParser('apple_health_export/export.xml')
    hrv_data = parser.get_all_data()
    print(len(hrv_data.keys()))
