import json

import requests


def get_current_temperature(location: str, latitude: float, longitude: float, unit: str = "fahrenheit"):
    """Get current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, and the unit in a dict
        forecast - forecast for 12h periods over the next seven days
    forecastHourly - forecast for hourly periods over the next seven days
    forecastGridData - raw forecast data over the next seven days

    forecast['properties']['periods'] yields a list for each timeframe with the keys
     'number',
     'name',
     'startTime',
     'endTime',
     'isDaytime',
     'temperature',
     'temperatureUnit',
     'temperatureTrend',
     'probabilityOfPrecipitation',
     'dewpoint',
     'relativeHumidity',
     'windSpeed',
     'windDirection',
     'icon',
     'shortForecast',
     'detailedForecast'

    """
    # Dicts with default values for returning later
    now, later = {"no data": "unable to retrieve the weather"}, {"no data": "unable to retrieve the weather"}
    # Request the weather for the location
    weather = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}", json=True)
    if 200 != weather.status_code:
        return {
        "now": now,
        "later": later,
        "location": location,
    }

    # Use the forecast location from the returned weather
    weather = weather.json()
    location_data = weather['properties']['relativeLocation']['properties']
    forecast_location = f"{location_data['city']} , {location_data['state']}"

    # Pull the forecasts for different windows of time
    # hourly_weather = requests.get(weather['properties']['forecastHourly'], json=True).json()
    twelve_hr_weather = requests.get(weather['properties']['forecast'], json=True).json()

    # Get today and tonight (or next period)
    for weather_dict in twelve_hr_weather['properties']['periods']:
        if weather_dict['number'] == 1:
           now = {
               'timeframe': weather_dict['name'],
               'temperature': weather_dict['temperature'],
               'temperatureUnit': weather_dict['temperatureUnit'],
               'probabilityOfPrecipitation': weather_dict['probabilityOfPrecipitation'],
               'windSpeed': weather_dict['windSpeed'],
               'windDirection': weather_dict['windDirection'],
               'detailedForecast': weather_dict['detailedForecast'],
           }
        if weather_dict['number'] == 2:
            later = {
                'timeframe': weather_dict['name'],
                'temperature': weather_dict['temperature'],
                'temperatureUnit': weather_dict['temperatureUnit'],
                'probabilityOfPrecipitation': weather_dict['probabilityOfPrecipitation'],
                'windSpeed': weather_dict['windSpeed'],
                'windDirection': weather_dict['windDirection'],
                'detailedForecast': weather_dict['detailedForecast'],
            }


    return {
        "now": now,
        "later": later,
        "location": forecast_location,
    }


def get_temperature_date(location: str, latitude: float, longitude: float, date: str, unit: str = "fahrenheit"):
    """Get temperature at a location and date.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        date: The date to get the temperature for, in the format "Year-Month-Day".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, the date and the unit in a dict
    """
    return {
        "temperature": 25.9,
        "location": location,
        "date": date,
        "unit": unit,
    }

if __name__ == "__main__":
    print(get_current_temperature("Baltimore",39.2756,-76.6015))


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "latitude": {
                        "type": "float",
                        "description": 'The latitude of the location to get the '
                                       'temperature for, as a float rounded to 4 decimal places".',
                    },
                    "longitude": {
                        "type": "string",
                        "description": 'The longitude of the location to get the '
                                       'temperature for, as a float rounded to 4 decimal places".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "fahrenheit".',
                    },
                },
                "required": ["location", "latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_date",
            "description": "Get temperature at a location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "latitude": {
                        "type": "float",
                        "description": 'The latitude of the location to get the '
                                       'temperature for, as a float rounded to 4 decimal places".',
                    },
                    "longitude": {
                        "type": "string",
                        "description": 'The longitude of the location to get the '
                                       'temperature for, as a float rounded to 4 decimal places".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the temperature for, in the format "Year-Month-Day".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "fahrenheit".',
                    },
                },
                "required": ["location", "latitude", "longitude", "date"],
            },
        },
    },
]
