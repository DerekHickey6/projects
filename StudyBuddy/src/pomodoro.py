import time
from dataclasses import dataclass

@dataclass   # decorator  - adds extra fucntionality to classes
class PomodoroState:
    phase: str = "focus"
    remaining_sec = int = 30 * 60    # Default 30 mins

# Main pomodoro class
class Pomodoro:
    # initializes state(phase and timer) & number of session completed
    def __init__(self):
        self.state = PomodoroState()
        self.session_count = 0
        
    # Counts down timer and transitions state
    def tick(self):
        """Called once per second to update timer"""
        self.state.remaining_sec -= 1
        if self.state.remaining_sec <= 0:
            self._transition()
    
    # non-public transition method
    def _transition(self):
        """Switch between focus/break phases"""
        # Checks phase state
        if self.state.phase == "focus":
            self.session_count += 1
            # Every 4th session, take a longer break
            if self.session_count % 4 == 0:
                self._set_phase("long_break", 20)
            else:
                self._set_phase("short_break", 5) 
        else:
            self._set_phase("focus", 25)
    
    # Restarts the phase that is transitioned to
    def _set_phase(self, phase, minutes):
        self.state.phase = phase
        self.state.remaining_sec = minutes * 60