import datetime

from parse_csv import PumpParser
from parse_xml import AppleHealthParser

class Dataset:
    PUMP_DS_DIR = 'pump'
    APPLE_DS_FILE = 'apple_health_export/export.xml'
    SAVE_FILE = 'dataset.npy'
    def __init__(self):
        self.pump_parser = PumpParser(self.PUMP_DS_DIR)
        self.apple_parser = AppleHealthParser(self.APPLE_DS_FILE)
        self._colate()

    def _colate(self):
        pump_data = self.pump_parser.get_all_data()
        watch_data = self.apple_parser.get_all_data()

        # Append, deduplicate all keys.
        all_keys = list(set(list(pump_data.keys()) + list(watch_data.keys())))
        self.times = np.array(all_keys)
        print(self.times)

        self.time_to_idx = {}
        for idx, time in enumerate(self.times):
            self.time_to_idx[time] = idx


        def iob_contribution(curr_dt, bolus_dt, units):
            min_diff = (curr_dt - bolus_dt).total_seconds() / 60
            # linear increase up to 15 minutes
            if min_diff < 15:
                return (min_diff / 15.0) * units
            elif min_diff < 300: # 5 hour effect
                return (285 - min_diff) / 285.0 * units
            else:
                return 0


        self.data = {}
        for key in all_keys:
            elem = pump_data[key] if key in pump_data.keys() else {}
            elem['rhr'] = watch_data[key]['rhr'] if key in watch_data.keys() else None
            elem['hrv'] = watch_data[key]['hrv'] if key in watch_data.keys() else None
            self.data[key] = elem

        # TODO: add sliding insulin window.
        # Calculate IoB:
        for key in sorted(all_keys, key=lambda x: datetime.datetime.strptime(x, '%m-%Y')):
            print(key)



    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self.data[key]

    def save_to_disk(self):


if __name__ == '__main__':

    
