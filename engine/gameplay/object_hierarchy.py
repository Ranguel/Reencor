from engine.constant.physics import *


def children_set_attribute(
    self: object = None, attribute: str = "", value: any = None, **kwargs
):
    """Kill the object instantly."""
    for child in self.children:
        if hasattr(child, attribute):
            setattr(child, attribute, value)


def children_kill(self: object = None, state_interruption=False, **kwargs):
    """Kill the object instantly."""
    for child in self.children:
        if hasattr(child, "life_time"):
            if state_interruption:
                if self.state_interruption and child.space == PositionSpace.LOCAL:
                    child.life_time = 0
            else:
                child.life_time = 0
