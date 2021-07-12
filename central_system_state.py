
from ocpp.v201.enums import Action
from enum import Enum


class CentralSystemStates(str, Enum):
    Off = 'Off'
    Booted = 'Booted'
    Active = 'Active'


class CentralSystemState:
    def __init__(self):
        self.state = {}
        self.steps = {
            Action.BootNotification: {'required': CentralSystemStates.Off,
                                      'transition': CentralSystemStates.Booted},
            Action.StatusNotification: {'required': CentralSystemStates.Booted,
                                        'transition': CentralSystemStates.Active},
        }

    def add_handled_charging_point(self, cp_id: str):
        self.state[cp_id] = CentralSystemStates.Off

    def remove_handled_charging_point(self, cp_id: str):
        self.state.pop(cp_id, None)

    def validate_change_state(self, cp_id: str, action: Action):
        if cp_id not in self.state or action not in self.steps:
            return False

        if self.state[cp_id] != self.steps[action]['required']:
            return False

        self.state[cp_id] = self.steps[action]['transition']

        return True
