import datetime
import json

from ..utilities.resource_path import resource_path
from ..utilities.config import config



path = resource_path('settings/state.json')



class StateManager:
    def __init__(self) -> None:
        self.state:dict = self.get_state_from_file()
        self.max_email_count = config.get("DEFAULT", "daily_email_limit")
        
        self.check_and_reset_if_new_day()


    def get_state_from_file(self) -> dict:
        try:
            with open(path, "r") as f:
                loaded_state = json.load(f)
                # Convert the date string back to a datetime object
                loaded_state["todays_date"] = datetime.datetime.strptime(loaded_state["todays_date"], "%Y-%m-%d %H:%M:%S.%f")
                return loaded_state
        except (FileNotFoundError, KeyError):
            # Initialize with default values if the file is missing or corrupted
            return {"todays_date": datetime.datetime.now(), "sent_today": 0}


    def update_state_file(self) -> None:
        self.max_email_count = config.get("DEFAULT","daily_email_limit")
        # Ensure todays_date is converted to a string before saving
        temp_state = self.state.copy()
        temp_state["todays_date"] = temp_state["todays_date"].strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(path, "w") as f:
            json.dump(temp_state, f, indent=4)


    def check_and_reset_if_new_day(self) -> None:
        if datetime.datetime.now() - self.state["todays_date"] >= datetime.timedelta(days=1):
            self.state["todays_date"] = datetime.datetime.now()
            self.state["sent_today"] = 0
            self.update_state_file()


    def can_send_email(self) -> bool:
        return self.state["sent_today"] < int(self.max_email_count)


    def increment_sent(self) -> bool:
        if self.can_send_email():
            self.state["sent_today"] += 1
            self.update_state_file()
            return True
        return False


state_manager = StateManager()
print("State manager loaded")
print(f"Lockout Date: {state_manager.state['todays_date']}")
print(f"        Sent: {state_manager.state['sent_today']}")
