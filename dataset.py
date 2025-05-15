import datetime

import numpy as np
import pandas as pd
from datasets import Dataset as HFDataset

from parse_csv import PumpParser
from parse_xml import AppleHealthParser

class Dataset:
    def __init__(self, pump_ds_dir, apple_ds_file):
        self.pump_parser = PumpParser(pump_ds_dir)
        self.apple_parser = AppleHealthParser(apple_ds_file)
        self._colate()

    def _colate(self):
        pump_data = self.pump_parser.get_all_data()
        watch_data = self.apple_parser.get_all_data()

        # Append, deduplicate all keys and sort them
        all_keys = sorted(list(set(list(pump_data.keys()) + list(watch_data.keys()))))
        self.times = np.array(all_keys)

        self.time_to_idx = {}
        for idx, time in enumerate(self.times):
            self.time_to_idx[time] = idx

        # TODO: This is a naive calculation. Replace with a more accurate IoB curve.
        def iob_contribution(curr_dt, bolus_dt, units):
            min_diff = (curr_dt - bolus_dt).total_seconds() / 60
            # linear increase up to 15 minutes
            if min_diff < 15:
                return (min_diff / 15.0) * units
            elif min_diff < 300: # 5 hour effect
                return (285 - min_diff) / 285.0 * units
            else:
                return 0

        # Initialize data dictionary with all timestamps
        self.data = {}
        for key in all_keys:
            elem = pump_data[key] if key in pump_data.keys() else {}
            elem['hr'] = watch_data[key]['hr'] if key in watch_data.keys() else None
            elem['timestamp'] = key
            elem['bg'] = elem.get('bg', None)
            elem['bolus'] = elem.get('bolus', 0.0)
            elem['carbs'] = elem.get('carbs', 0.0)
            elem['food_bolus'] = elem.get('food_bolus', 0.0)
            elem['corr_bolus'] = elem.get('corr_bolus', 0.0)
            self.data[key] = elem

        # Calculate IoB for each timestamp
        sorted_times = sorted(all_keys)
        for i, curr_time in enumerate(sorted_times):
            curr_dt = datetime.datetime.fromisoformat(curr_time).replace(tzinfo=None)
            total_iob = 0.0

            # Look back 5 hours (300 minutes) for insulin contributions
            for prev_time in sorted_times[max(0, i-60):i]:  # Assuming 5-min intervals, look back 60 entries
                prev_dt = datetime.datetime.fromisoformat(prev_time).replace(tzinfo=None)
                if (curr_dt - prev_dt).total_seconds() <= 300 * 60:  # Within 5 hours
                    if 'bolus' in self.data[prev_time] and self.data[prev_time]['bolus'] > 0:
                        total_iob += iob_contribution(curr_dt, prev_dt, self.data[prev_time]['bolus'])

            self.data[curr_time]['iob'] = total_iob

        # Convert to pandas DataFrame for interpolation
        df = pd.DataFrame.from_dict(self.data, orient='index')

        # Interpolate missing values
        numeric_columns = ['bg', 'hr', 'iob']
        df[numeric_columns] = df[numeric_columns].interpolate(method='linear', limit=6)  # interpolate up to 30 min gaps

        # Convert back to dictionary format
        self.data = df.to_dict('index')

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self.data[key]

    def save_to_disk(self, save_file):
        # Convert data to HuggingFace dataset format
        records = []
        for timestamp in sorted(self.data.keys()):
            record = self.data[timestamp]
            records.append({
                'timestamp': timestamp,
                'bg': record['bg'],
                'hr': record['hr'],
                'iob': record['iob'],
                'bolus': record['bolus'],
                'carbs': record['carbs'],
                'food_bolus': record['food_bolus'],
                'corr_bolus': record['corr_bolus']
            })

        # Create HuggingFace dataset
        hf_dataset = HFDataset.from_list(records)

        # Save to disk
        hf_dataset.save_to_disk(save_file)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process diabetes dataset.')
    parser.add_argument('--pump_ds_dir', type=str, default='pump', help='Directory containing pump data CSV files.')
    parser.add_argument('--apple_ds_file', type=str, default='apple_health_export/export.xml', help='Path to Apple Health export XML file.')
    parser.add_argument('--save_file', type=str, default='dataset', help='Path to save the dataset.')
    args = parser.parse_args()

    dataset = Dataset(args.pump_ds_dir, args.apple_ds_file)
    dataset.save_to_disk(args.save_file)