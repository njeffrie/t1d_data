"""Parser for pump data JSON files."""

import os
import datetime
import json
from typing import Dict, List, Tuple

from . import utils


class PumpParser:
    """Parser for pump data JSON files.

    This class handles parsing of blood glucose and bolus data from Tidepool JSON files.
    """

    def __init__(self, pump_dir: str) -> None:
        """Initialize the parser with the pump data directory.

        Args:
            pump_dir: Path to the directory containing pump JSON file.
        """
        self.pump_dir = pump_dir
        self.json_file = os.path.join(pump_dir, 'TidepoolExport.json')
        
        # Load and parse JSON data
        with open(self.json_file, 'r') as f:
            self.data = json.load(f)

    def _parse_timestamp(self, time_str: str) -> datetime.datetime:
        """Parse timestamp from Tidepool format to datetime.

        Args:
            time_str: Timestamp string in Tidepool format.

        Returns:
            Datetime object.
        """
        # Tidepool uses ISO 8601 format with timezone
        dt = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.replace(tzinfo=None)  # Remove timezone info for consistency

    def _get_basal_rates(self) -> List[Tuple[datetime.datetime, float]]:
        """Get basal rate changes from the JSON data, split into 5-minute segments.

        Returns:
            List of tuples containing (timestamp, rate) for each 5-minute segment.
        """
        basal_entries = [entry for entry in self.data 
                        if entry.get('type') == 'basal']
        
        rates = {}
        for entry in basal_entries:
            start_dt = self._parse_timestamp(entry['time'])
            # Get duration in minutes
            duration_minutes = round(float(entry.get('duration', 0)))
            # Convert hourly rate to 5 minute rate.
            rate = float(entry.get('rate', 0.0)) / 12.0
            
            for i in range(round(duration_minutes / 5.0)):
                key = utils.round(start_dt + datetime.timedelta(minutes=5 * i))
                # Add the segment
                rates[key] = rate
        print(sorted(rates.keys())[:10])
        return rates


    def read_bg_data(self) -> Dict[str, float]:
        """Read blood glucose data from the JSON file.

        Returns:
            Dictionary mapping timestamps to blood glucose values.
        """
        readings = {}
        
        # Filter for blood glucose entries
        bg_entries = [entry for entry in self.data 
                     if entry.get('type') == 'cbg' and 
                     entry.get('units') == 'mg/dL']
        
        for entry in bg_entries:
            dt = self._parse_timestamp(entry['time'])
            key = utils.round(dt)
            readings[key] = float(entry['value'])
            
        return readings

    def read_bolus_data(self) -> Dict[str, Dict]:
        """Read bolus data from the JSON file.

        Returns:
            Dictionary mapping timestamps to bolus data dictionaries.
        """
        readings = {}
        
        # Filter for bolus entries
        bolus_entries = [entry for entry in self.data 
                        if entry.get('type') == 'bolus']
        
        for entry in bolus_entries:
            dt = self._parse_timestamp(entry['time'])
            key = utils.round(dt)
            
            # Extract bolus information
            entry_data = {
                'bolus': float(entry.get('normal', 0.0)),
                'bg': float(entry.get('bgInput', 0.0)),
                'carbs': float(entry.get('carbInput', 0.0)),
                'food_bolus': float(entry.get('normal', 0.0)),  # Normal bolus is typically for food
                'corr_bolus': float(entry.get('correction', 0.0))
            }
            
            readings[key] = entry_data

        # Add basal rates
        basal_rates = self._get_basal_rates()

        for key, rate in basal_rates.items():
            if key in readings:
                readings[key]['bolus'] += rate
            else:
                readings[key] = {
                    'bolus': rate,
                    'bg': None,
                    'carbs': 0.0,
                    'food_bolus': 0.0,
                    'corr_bolus': 0.0
                }
            
        return readings

    def get_all_data(self) -> Dict[str, Dict]:
        """Get all pump data.

        Returns:
            Dictionary mapping timestamps to dictionaries containing both blood glucose
            and bolus data.
        """
        bg_data = self.read_bg_data()
        bolus_data = self.read_bolus_data()

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
    
    # Print some sample entries
    for i, key in enumerate(sorted(values.keys())[:150]):
        print(f"\nEntry {i+1}:")
        print(f"Time: {key}")
        print(f"Data: {values[key]}")


if __name__ == '__main__':
    main() 