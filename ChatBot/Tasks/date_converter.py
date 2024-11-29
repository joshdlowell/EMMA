import datetime

def weekday_to_date(weekday):
    """Converts a day of the week (e.g., "Monday") to a date,
    optionally using a reference date.

    Args:
        weekday (str): The day of the week (e.g., "Monday", "Tuesday").

    Returns:
        datetime.date: The date corresponding to the given day of the week.
    """

    reference_date = datetime.date.today()

    # Convert day of week to integer (0 = Monday, 6 = Sunday)
    day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(weekday.capitalize())

    # Calculate the difference in days between reference date and target day
    days_difference = day_index - reference_date.weekday()

    # Adjust if the target day is in the past
    if days_difference < 0:
        days_difference += 7

    reference_date = reference_date + datetime.timedelta(days=days_difference)
    return {'date': reference_date.strftime('%Y-%m-%d')}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "weekday_to_date",
            "description": "convert a day of the week (e.g., 'Monday', 'Tuesday') into a date in the format 'year-month-day'",
            "parameters": {
                "type": "object",
                "properties": {
                    "weekday": {
                        "type": "string",
                        "description": 'The day of the week (e.g., "Monday", "Tuesday") to convert to a date',
                    },
                },
                "required": ["weekday"],
            },
        },
    },
]