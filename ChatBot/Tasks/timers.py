import datetime
import threading
import time


class Timers:
    def __init__(self, callback, streamlit_ctx, streamlit_add_ctx):
        self.timers = {}
        self.player_callback = callback
        self.streamlit_ctx = streamlit_ctx
        self.streamlit_add_ctx = streamlit_add_ctx

    def set_timer(self, name, duration):
        num, new_name = 2, name
        while new_name in self.timers.keys() and num < 10:
            new_name = name + " " + str(num)
            num += 1
        if num > 9:
            self.player_callback(f"There are already {num - 1} timers with the name {name}. "
                                 f"Please choose another name.")
        else:
            start_timer = threading.Thread(target=self.time_runner, args=(new_name, duration), daemon=True)
            self.timers[new_name] = {'duration': duration,
                                     'start': datetime.datetime.now(),
                                     'end': datetime.datetime.now() + datetime.timedelta(seconds=duration),
                                     'thread': start_timer,
                                     'cancelled': False}
            self.streamlit_add_ctx(start_timer, self.streamlit_ctx)
            start_timer.start()
        print("timer set")

    def get_timers(self):
        info_string = ""
        for key in self.timers.keys():
            info_string += f"{key} with "
            info_string += self.remaining_time(info_string, key)

        self.player_callback(f"There are {len(self.timers.keys())} active timers. {info_string}")

    def check_timer(self, name):
        # Check for numeric and text numbers
        num_list = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

        timer = self.timers.pop(name, None)

        if not timer:
            values = name.split()
            if len(values) > 1 and values[-1].strip().lower() in num_list:
                values[-1] = str(num_list.index(values[-1].strip().lower()))
                name = " ".join(values)
                timer = self.timers.pop(name, None)

        if timer:
            info_string = f"{name} timer has "
            info_string += self.remaining_time(info_string, name)
        elif len(self.timers) == 1:
            name = list(self.timers.keys())[0]
            info_string = f"You only have a timer named {name}, which has "
            info_string += self.remaining_time(info_string, name)
        else:
            info_string = f"There is no timer named {name}"

        self.player_callback(info_string)

    def cancel_timer(self, name):
        if name in self.timers.keys():
            self.timers[name]['cancelled'] = True
            self.player_callback(f"{name} timer cancelled")

    def time_runner(self, name, duration):
        time.sleep(duration)
        if not self.timers[name]['cancelled']:
            self.player_callback(f"{name} timer is finished")
        self.timers.pop(name, None)
        print(f"{name} timer complete")

    def remaining_time(self, info_string, name):
        time_remaining = self.timers[name]['end'] - datetime.datetime.now()
        if time_remaining.total_seconds() < 0:
            info_string += "no time remaining, "
        else:
            days = time_remaining.days
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if days > 0:
                info_string += f"{days} days, "
            if hours > 0:
                info_string += f"{hours} hours, "
            if minutes > 0:
                info_string += f"{minutes} minutes, "
            if seconds > 0:
                info_string += f"{seconds} seconds, "
            info_string += "remaining. "
        return info_string



TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "set_timer",
                "description": "create a timer that alerts the user when completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": 'The name of the timer the user would like to create',
                        },
                        "duration": {
                            "type": "float",
                            "description": 'The duration of the timer the user would like to '
                                           'create in seconds represented as a float',
                        },
                    },
                    "required": ["name", "duration"],
                },
            },
        },
    {
        "type": "function",
        "function": {
            "name": "get_timers",
            "description": "gets the list of currently active timers and provides it to the user. This "
                           "function takes no arguments",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": None,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_timer",
            "description": "Determines the amount of time remaining on a timer and returns that value to the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": 'The name of the timer the user would like to check',
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_timer",
            "description": "Cancels a timer that the user has requested to cancel",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": 'The name of the timer the user would like to cancel',
                    },
                },
                "required": ["name"],
            },
        },
    },
    ]