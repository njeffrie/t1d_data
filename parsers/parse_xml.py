"""Parser for Apple Health export XML data."""

import datetime
from typing import Dict, List, Tuple

import tqdm
import xml.etree.ElementTree as ET

from . import utils


class AppleHealthParser:
    """Parser for Apple Health export XML data.

    This class handles parsing of heart rate (HR) data and workout activities from Apple Health export XML files.
    """

    HR_TYPE = 'HKQuantityTypeIdentifierHeartRate'
    WORKOUT_TYPE = 'HKWorkoutTypeIdentifier'
    
    # Workout types we're interested in
    RUNNING = 'HKWorkoutActivityTypeRunning'
    WALKING = 'HKWorkoutActivityTypeWalking'
    NORDIC_SKIING = 'HKWorkoutActivityTypeNordicSkiing'

    def __init__(self, fname: str) -> None:
        """Initialize the parser with the XML file.

        Args:
            fname: Path to the Apple Health export XML file.
        """
        self.element_tree = ET.parse(fname)
        self.root = self.element_tree.getroot()
        self._parse_data()

    def _parse_workouts(self) -> List[Tuple[datetime.datetime, datetime.datetime, str]]:
        """Parse workout records from the XML.

        Returns:
            List of tuples containing (start_time, end_time, workout_type) for each workout.
        """
        workouts = []
        
        for elem in tqdm.tqdm(self.root):
            if elem.tag != 'Workout':
                continue
                
            workout_type = elem.attrib.get('workoutActivityType')
            if workout_type not in [self.RUNNING, self.WALKING, self.NORDIC_SKIING]:
                continue
                
            start_dt = datetime.datetime.fromisoformat(elem.attrib['startDate']).replace(tzinfo=None)
            end_dt = datetime.datetime.fromisoformat(elem.attrib['endDate']).replace(tzinfo=None)
            
            workouts.append((start_dt, end_dt, workout_type))
            
        return workouts

    def _parse_data(self) -> None:
        """Parse all heart rate data and workout activities.

        This method populates self.hr_entries with data from the XML and tracks workout periods.
        """
        self.hr_entries: Dict[str, Dict] = {}
        
        # First parse all workouts
        workouts = self._parse_workouts()
        
        # Then parse heart rate data and check for overlapping workouts
        for elem in tqdm.tqdm(self.root):
            if elem.tag != 'Record':
                continue

            record_type = elem.attrib.get('type')
            if record_type != self.HR_TYPE:
                continue

            # Convert to timezone-naive datetime
            start_dt = datetime.datetime.fromisoformat(elem.attrib['startDate']).replace(tzinfo=None)
            start_dt = utils.round(start_dt)
            value = float(elem.attrib['value'])

            # Initialize entry with default values
            if start_dt not in self.hr_entries:
                self.hr_entries[start_dt] = {
                    'hr': value,
                    'running': False,
                    'walking': False,
                    'nordic_skiing': False
                }
            else:
                self.hr_entries[start_dt]['hr'] = value

            # Check if this timestamp falls within any workout periods
            for workout_start, workout_end, workout_type in workouts:
                if workout_start <= start_dt <= workout_end:
                    if workout_type == self.RUNNING:
                        self.hr_entries[start_dt]['running'] = True
                    elif workout_type == self.WALKING:
                        self.hr_entries[start_dt]['walking'] = True
                    elif workout_type == self.NORDIC_SKIING:
                        self.hr_entries[start_dt]['nordic_skiing'] = True

    def get_all_data(self) -> Dict[str, Dict]:
        """Get all heart rate and activity data.

        Returns:
            A dictionary mapping timestamps to dictionaries containing HR and activity values.
            Example:
            {
                '2024-01-01T00:00:00': {
                    'hr': 72.0,
                    'running': False,
                    'walking': True,
                    'nordic_skiing': False
                }
            }
        """
        return self.hr_entries


def main() -> None:
    """Main function to demonstrate parser usage."""
    parser = AppleHealthParser('apple_health_export/export.xml')
    data = parser.get_all_data()
    print(f"Total entries: {len(data.keys())}")
    
    # Print some statistics about activities
    running_count = sum(1 for entry in data.values() if entry['running'])
    walking_count = sum(1 for entry in data.values() if entry['walking'])
    skiing_count = sum(1 for entry in data.values() if entry['nordic_skiing'])
    
    print(f"Running periods: {running_count}")
    print(f"Walking periods: {walking_count}")
    print(f"Nordic skiing periods: {skiing_count}")


if __name__ == '__main__':
    main() 