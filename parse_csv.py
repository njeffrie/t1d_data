import os
import utils
from datetime import datetime

class PumpParser:
    def __init__(self, pump_dir):
        self.pump_dir = pump_dir
        self.csvfiles = [f for f in os.listdir(pump_dir) if f.endswith('.csv')]

    def read_bg_data(self, fname):
        readings = {}
        with open(fname, 'r') as f:
            # logs start with 6 lines of file header plus one line for column names.
            for line in f.readlines()[7:]:
                # cgm readings start with pump name.
                elems = line.split(',')
                if elems[0] == 't:slim X2':
                    pump, ser_num, desc, dtime, val = elems[:5]
                    readings[utils.round(datetime.fromisoformat(dtime))]=float(val)
        return readings

    def read_bolus_data(self, fname):
        readings = {}
        with open(fname, 'r') as f:
            # logs start with 6 lines of file header plus one line for column names.
            for line in f.readlines()[7:]:
                # cgm readings start with pump name.
                elems = line.split(',')
                if elems[0] == 'Bolus':
                    _, btype, method, bg, _, dtime, size, food_bolus, corr_bolus, desc, _, _, _, _, _, _, carbs, _, cf, cr  = elems[:20]
                    key = utils.round(datetime.fromisoformat(dtime))
                    entry = {}
                    entry['bolus'] = float(size)
                    entry['bg'] = float(bg)
                    entry['carbs'] = float(carbs)
                    entry['food_bolus'] = float(food_bolus)
                    entry['corr_bolus'] = float(corr_bolus)
                    readings[key] = entry
        return readings

    def get_all_bolus_data(self):
        bolus_values = {}
        for file in self.csvfiles:
            bolus_values.update(self.read_bolus_data(os.path.join(self.pump_dir, file)))

        return bolus_values

    def get_all_bg_data(self):
        bg_values = {}
        for file in self.csvfiles:
            bg_values.update(self.read_bg_data(os.path.join(self.pump_dir, file)))

        return bg_values

    def get_all_data(self):
        bg_data = self.get_all_bg_data()
        bolus_data = self.get_all_bolus_data()

        # First convert both to lists, append, then deduplicate.
        all_keys = list(set(list(bg_data.keys()) + list(bolus_data.keys())))

        all_data = {}
        for key in all_keys:
            elem = bolus_data[key] if key in bolus_data.keys() else {}
            elem['bg'] = bg_data[key] if key in bg_data.keys() else None
            all_data[key] = elem
        return all_data


if __name__ == '__main__':
    parser = PumpParser('pump')
    values = parser.get_all_data()
    print(len(list(values.keys())))
    for i in range(100):
        print(values[list(values.keys())[i]])
