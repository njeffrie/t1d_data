"""Parser for nutrition data CSV files."""

import datetime
from typing import Dict, Optional

import pandas as pd
import tqdm

from . import utils


class FoodParser:
    """Parser for nutrition data CSV files.

    This class handles parsing of food intake data from nutrition summary CSV files.
    """

    def __init__(self, fname: str) -> None:
        """Initialize the parser with the CSV file.

        Args:
            fname: Path to the nutrition summary CSV file.
        """
        self.df = pd.read_csv(fname)
        self._parse_data()

    def _guess_time(self, current_idx: int, meal_type: str) -> Optional[str]:
        """Guess the time for a meal based on adjacent entries of the same meal type.

        Args:
            current_idx: Index of the current row in the dataframe.
            meal_type: Type of meal (Breakfast, Lunch, Dinner, Snacks).

        Returns:
            Guessed time string in format 'HH:MM AM/PM' or None if no good guess can be made.
        """
        # Look at previous entries
        for i in range(current_idx - 1, -1, -1):
            prev_row = self.df.iloc[i]
            if prev_row['Meal'] == meal_type and not pd.isna(prev_row['Time']):
                return prev_row['Time']

        # Look at next entries
        for i in range(current_idx + 1, len(self.df)):
            next_row = self.df.iloc[i]
            if next_row['Meal'] == meal_type and not pd.isna(next_row['Time']):
                return next_row['Time']

        # If no good guess can be made, return None
        return None

    def _parse_data(self) -> None:
        """Parse all nutrition data.

        This method populates self.food_entries with data from the CSV.
        """
        self.food_entries: Dict[str, Dict] = {}

        for idx, row in tqdm.tqdm(self.df.iterrows(), total=len(self.df)):
            # Parse date and time
            date_str = row['Date']
            time_str = row['Time']
            
            if pd.isna(time_str):
                # Try to guess time based on adjacent entries of the same meal type
                guessed_time = self._guess_time(idx, row['Meal'])
                if guessed_time:
                    time_str = guessed_time
                else:
                    # If no good guess can be made, use default times based on meal type
                    meal_defaults = {
                        'Breakfast': '08:00 AM',
                        'Lunch': '12:00 PM',
                        'Dinner': '06:00 PM',
                        'Snacks': '09:00 PM'
                    }
                    time_str = meal_defaults.get(row['Meal'], '12:00 PM')
            
            # Combine date and time
            dt_str = f"{date_str} {time_str}"
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %I:%M %p')
            key = utils.round(dt)
            
            # Create entry for this timestamp
            if key not in self.food_entries:
                self.food_entries[key] = {
                    'calories': 0.0,
                    'carbs': 0.0,
                    'protein': 0.0,
                    'fat': 0.0,
                    'fiber': 0.0,
                    'saturated_fat': 0.0,
                    'sodium': 0.0
                }
            
            # Add nutrition data
            entry = self.food_entries[key]
            entry['calories'] += float(row['Calories']) if not pd.isna(row['Calories']) else 0.0
            entry['carbs'] += float(row['Carbohydrates (g)']) if not pd.isna(row['Carbohydrates (g)']) else 0.0
            entry['protein'] += float(row['Protein (g)']) if not pd.isna(row['Protein (g)']) else 0.0
            entry['fat'] += float(row['Fat (g)']) if not pd.isna(row['Fat (g)']) else 0.0
            entry['fiber'] += float(row['Fiber']) if not pd.isna(row['Fiber']) else 0.0
            entry['saturated_fat'] += float(row['Saturated Fat']) if not pd.isna(row['Saturated Fat']) else 0.0
            entry['sodium'] += float(row['Sodium (mg)']) if not pd.isna(row['Sodium (mg)']) else 0.0

    def get_all_data(self) -> Dict[str, Dict]:
        """Get all nutrition data.

        Returns:
            A dictionary mapping timestamps to dictionaries containing nutrition values.
            Example:
            {
                '2024-01-01T00:00:00': {
                    'calories': 500.0,
                    'carbs': 50.0,
                    'protein': 20.0,
                    'fat': 15.0,
                    'fiber': 5.0,
                    'saturated_fat': 3.0,
                    'sodium': 500.0,
                    'meal_type': 'Lunch'
                }
            }
        """
        return self.food_entries


def main() -> None:
    """Main function to demonstrate parser usage."""
    parser = FoodParser('nutrition_summary.csv')
    food_data = parser.get_all_data()
    print(f"Total entries: {len(food_data.keys())}")


if __name__ == '__main__':
    main() 