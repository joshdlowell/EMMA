import json
import datetime
import pandas as pd
import requests


def get_current_weather(location: str):
    """Get current temperature at a location.
    using https://simplemaps.com/data/us-cities data to get grid coordinates

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".

    Returns:
        a dict of weather data for the current timeframe and a dict of weather data for the next timeframe
        and a string of the forecast location, all in a dict
    """
    # Dicts with default values for returning later
    now, later = {"no data": "unable to retrieve the weather"}, {"no data": "unable to retrieve the weather"}
    # Convert location into grid coordinates
    grid_dict = get_grid_coordinates(location)
    if not grid_dict:
        return {"now": now, "later": later, "location": location}
    # Request the weather for the location
    weather = requests.get(f"https://api.weather.gov/points/{grid_dict['lat']},{grid_dict['long']}", json=True)
    if 200 != weather.status_code:  # If there was an API error, return defaults
        return {"now": now, "later": later, "location": location}

    # Use the forecast location from the returned weather
    weather = weather.json()
    # Pull the location specific forecasts for different windows of time
    twelve_hr_weather = requests.get(weather['properties']['forecast'], json=True).json()
    # Get today and tonight (or next period) conditions
    now_dict, later_dict = None, None
    for weather_dict in twelve_hr_weather['properties']['periods']:
        if weather_dict['number'] == 1:  # Current period is number 1
            now_dict = weather_dict
        if weather_dict['number'] == 2:  # Next period is number 2
            later_dict = weather_dict
        if now_dict and later_dict:  # Stop processing if required data has been collected
            break

    now = {
        'timeframe': now_dict.get('name', "unknown"),
        'temperature': now_dict.get('temperature', "unknown"),
        'temperatureUnit': now_dict.get('temperatureUnit', "unknown"),
        'detailedForecast': now_dict.get('detailedForecast', "unknown"),
    }
    later = {
        'timeframe': later_dict.get('name', 'unknown'),
        'detailedForecast': later_dict.get('detailedForecast', 'unknown'),
    }
    return {"now": now, "later": later, "location": location}


def get_weather_date(location: str, date: str = 0, day_of_week: str = None):
    """Get temperature at a location and date.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        date: The date to get the temperature for, in the format "Year-Month-Day".
        day_of_week: The day of the week (e.g., "Monday", "Tuesday") to get the weather for.

    Returns:
        the temperature, the location, the date and the unit in a dict
    """
    # Dicts with default values for returning later
    forecast = {"no data": "unable to retrieve the weather"}
    # Get date if day of the week was given
    if day_of_week:
        reference_date = datetime.date.today()
        # Convert day of week to integer (0 = Monday, 6 = Sunday)
        day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day_of_week.capitalize())
        # Calculate the difference in days between reference date and target day
        days_difference = day_index - reference_date.weekday()
        # Adjust if the target day is in the past
        if days_difference < 0:
            days_difference += 7
        date = (reference_date + datetime.timedelta(days=days_difference)).strftime('%Y-%m-%d')
    # Convert location into grid coordinates
    grid_dict = get_grid_coordinates(location)
    # Request the weather for the location
    if not grid_dict:
        return {"forecast": forecast, "location": location}
    weather = requests.get(f"https://api.weather.gov/points/{grid_dict['lat']},{grid_dict['long']}", json=True)
    if 200 != weather.status_code:  # If there was an API error, return defaults
        return {"forecast": forecast, "location": location}

    # Use the forecast location from the returned weather
    weather = weather.json()
    # Pull the location specific forecasts for different windows of time
    twelve_hr_weather = requests.get(weather['properties']['forecast'], json=True).json()

    # Get day and evening conditions
    forecast_dict = {}
    temp_unit = 'unknown'
    for weather_dict in twelve_hr_weather['properties']['periods']:
        print(weather_dict['startTime'].split('T')[0].strip())
        if date == weather_dict['startTime'].split('T')[0].strip():
            forecast_dict[weather_dict['name']] = weather_dict['detailedForecast']
            temp_unit = weather_dict.get('temperatureUnit', "unknown"),
    return {"forecast": forecast_dict, 'temperatureUnit': temp_unit,"location": location}


def get_grid_coordinates(location):
    location_list = location.split(",")  # Should yield [city, state, country]
    df = pd.read_csv("Tasks/ref_data/uscities.csv")
    # df = pd.read_csv("ref_data/uscities.csv")

    filtered_df = df[
        ['city', 'state_name', 'lat', 'lng']].loc[(df['city'].str.contains(location_list[0], case=False)) &
                                                  (df['state_name'].str.contains(location_list[1].strip(), case=False))]
    if filtered_df.empty:
        filtered_df = df[
            ['city', 'state_id', 'lat', 'lng']].loc[(df['city'].str.contains(location_list[0], case=False)) &
            (df['state_id'].str.contains(location_list[1].strip(), case=False))]
    if filtered_df.empty:
        return None

    return {'lat': filtered_df.at[filtered_df.index[0], 'lat'], 'long': filtered_df.at[filtered_df.index[0], 'lng']}


if __name__ == "__main__":
    # print(get_current_weather("Baltimore, Maryland, USA",39.2756,-76.6015))
    print(get_weather_date("Baltimore, Maryland, USA",'2024-11-30'))


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get a summary of the current weather at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the weather for, in the format "City, State, Country".',
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_date",
            "description": "Get weather at a location and date. The function requires the arguments location and \
            either the date or the day_of_week. The value for these arguments must be obtained directly from user \
            input, not by AI guessing. If the user has not provided the required information, the function cannot \
            be used, but instead clarifying questions to user are required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the weather for, in the format "City, State, Country".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the weather for, in the format "Year-Month-Day".',
                    },
                    "day_of_week": {
                        "type": "string",
                        "description": 'The day of the week (e.g., "Monday", "Tuesday") to get the weather for',
                    },
                },
                "required": ["location"],
            },
        },
    },
]
