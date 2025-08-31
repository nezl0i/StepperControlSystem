from abc import ABC, abstractmethod

class HardwareInterface(ABC):
    @abstractmethod
    def move_axis(self, axis: str, steps: int):
        pass
    
    @abstractmethod
    def set_holding_torque(self, axis: str, enable: bool):
        pass
    
    @abstractmethod
    def read_endstop(self, pin: int) -> bool:
        pass
    
    @abstractmethod
    def emergency_stop(self):
        pass
    
    @abstractmethod
    def cleanup(self):
        pass