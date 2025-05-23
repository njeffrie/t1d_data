"""Parser for pump data CSV files."""

import os
import datetime
from typing import Dict

from . import utils


class PumpParser:
    """Parser for pump data CSV files.

    This class handles parsing of blood glucose and bolus data from pump CSV files.
    """

    def __init__(self, pump_dir: str) -> None:
        """Initialize the parser with the pump data directory.

        Args:
            pump_dir: Path to the directory containing pump CSV files.
        """
        self.pump_dir = pump_dir
        self.csvfiles = [f for f in os.listdir(pump_dir) if f.endswith('.csv')]

    def read_bg_data(self, fname: str) -> Dict[str, float]:
        """Read blood glucose data from a CSV file.

        Args:
            fname: Path to the CSV file.

        Returns:
            Dictionary mapping timestamps to blood glucose values.
        """
        readings = {}
        with open(fname, 'r') as f:
            # logs start with 6 lines of file header plus one line for column names.
            for line in f.readlines()[7:]:
                # cgm readings start with pump name.
                elems = line.split(',')
                if elems[0] == 't:slim X2':
                    pump, ser_num, desc, dtime, val = elems[:5]
                    dt = datetime.datetime.fromisoformat(dtime).replace(tzinfo=None)
                    readings[utils.round(dt)] = float(val)
        return readings

    def read_bolus_data(self, fname: str) -> Dict[str, Dict]:
        """Read bolus data from a CSV file.

        Args:
            fname: Path to the CSV file.

        Returns:
            Dictionary mapping timestamps to bolus data dictionaries.
        """
        readings = {}
        with open(fname, 'r') as f:
            # logs start with 6 lines of file header plus one line for column names.
            for line in f.readlines()[7:]:
                # cgm readings start with pump name.
                elems = line.split(',')
                if elems[0] == 'Bolus':
                    _, btype, method, bg, _, dtime, size, food_bolus, corr_bolus, desc, _, _, _, _, _, _, carbs, _, cf, cr = elems[:20]
                    dt = datetime.datetime.fromisoformat(dtime).replace(tzinfo=None)
                    key = utils.round(dt)
                    entry = {
                        'bolus': float(size),
                        'bg': float(bg),
                        'carbs': float(carbs),
                        'food_bolus': float(food_bolus),
                        'corr_bolus': float(corr_bolus)
                    }
                    readings[key] = entry
        return readings

    def get_all_bolus_data(self) -> Dict[str, Dict]:
        """Get all bolus data from all CSV files.

        Returns:
            Dictionary mapping timestamps to bolus data dictionaries.
        """
        bolus_values = {}
        for file in self.csvfiles:
            bolus_values.update(self.read_bolus_data(os.path.join(self.pump_dir, file)))
        return bolus_values

    def get_all_bg_data(self) -> Dict[str, float]:
        """Get all blood glucose data from all CSV files.

        Returns:
            Dictionary mapping timestamps to blood glucose values.
        """
        bg_values = {}
        for file in self.csvfiles:
            bg_values.update(self.read_bg_data(os.path.join(self.pump_dir, file)))
        return bg_values

    def get_all_data(self) -> Dict[str, Dict]:
        """Get all pump data.

        Returns:
            Dictionary mapping timestamps to dictionaries containing both blood glucose
            and bolus data.
        """
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


def main() -> None:
    """Main function to demonstrate parser usage."""
    parser = PumpParser('pump')
    values = parser.get_all_data()
    print(f"Total entries: {len(values.keys())}")
    for i in range(100):
        print(values[list(values.keys())[i]])


if __name__ == '__main__':
    main() 