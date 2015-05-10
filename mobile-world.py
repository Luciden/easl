"""
Containing the experiment based on the mobile experiment.
"""
import functools

from easl import *
from easl.agent import *
from easl.visualize import Visualizer


#
# Infant functions
#

def calc_direction(a, b):
    """
    Calculates which direction b is from a.
    """
    d = {"down": -1, "middle": 0, "up": 1}

    if d[a] == d[b]:
        return "still"
    if d[a] < d[b]:
        return "up"
    if d[a] > d[b]:
        return "down"


def new_position(position, direction):
    if direction == "still" or direction == "up" and position == "up" or direction == "down" and position == "down":
        # Already at maximum, so nothing changes
        return position
    elif direction == "up":
        if position == "down":
            return "middle"
        if position == "middle":
            return "up"
    elif direction == "down":
        if position == "up":
            return "middle"
        if position == "middle":
            return "down"

    raise RuntimeError("Unhandled movement {1} from {0}.".format(position, direction))


def relative_direction(self, value, attribute):
    """
    Callback function for the infant's limbs.
    """
    self.try_change(attribute, new_position(self.a[attribute], value))


def move(old, new):
    return "movement", {"direction": calc_direction(old, new)}


#
# Mobile functions
#

def swing(self):
    speed = self.a["speed"]
    if 0 < speed <= 10:
        self.try_change("speed", speed - 1)
    if speed > 10:
        self.try_change("speed", 10)


def moved(self, direction):
    self.a["speed"] += 4


def movement_emission(self):
    s = []
    if self.a["speed"] > 0:
        s.append(Signal("sight", "movement", True, [True, False]))

    return s


class SightSensor(Sensor):
    def init(self):
        self.signals.update({"movement": [True, False]})
        self.default_signals.update({"movement": False})

    def detects_modality(self, modality):
        return modality == "sight"


def create_infant(agent):
    """
    Parameters
    ----------
    agent : string
        Name of the type of agent to use.
    """
    infant = Entity("infant")

    if agent == "random":
        infant.set_agent(RandomAgent())
    elif agent == "operant":
        infant.set_agent(OperantConditioningAgent())
        infant.agent.set_primary_reinforcer("movement", {"value": True})
    elif agent == "causal":
        cla = CausalLearningAgent()
        cla.set_values({"movement": True})
        infant.set_agent(cla)
    else:
        raise RuntimeError("Undefined agent type.")

    infant.add_attribute("left-hand-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("right-hand-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("left-foot-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("right-foot-position", "down", ["down", "middle", "up"], move)

    infant.add_action("left-hand",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="left-hand-position"))

    infant.add_action("right-hand",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="right-hand-position"))

    infant.add_action("left-foot",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="left-foot-position"))

    infant.add_action("right-foot",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="right-foot-position"))

    infant.add_sensor(SightSensor())

    return infant


def create_mobile():
    mobile = Entity("mobile")

    mobile.add_attribute("speed", 0, range(0, 10), lambda old, new: None)
    mobile.set_physics(swing)

    mobile.add_trigger("movement", moved)
    mobile.set_emission(movement_emission)

    return mobile


def create_experimenter(experiment_log):
    """
    Parameters
    ----------
    log : Log
        Log to play back kicking behavior from.
    """
    experimenter = Entity("experimenter")
    # second argument is dictionary of which actions of the original log match which actions.
    agent = LogAgent("infant", experiment_log)
    agent.set_watched("right-foot-position", "mechanical-hand", calc_direction)
    experimenter.set_agent(agent)

    experimenter.add_attribute("mechanical-hand-position", "down", ["down", "middle", "up"], move)

    experimenter.add_action("mechanical-hand",
                            ["up", "still", "down"],
                            "still",
                            functools.partial(relative_direction, attribute="mechanical-hand-position"))

    return experimenter


def experimental_condition():
    infant = create_infant("causal")
    mobile = create_mobile()

    world = World()
    world.add_entity(infant)
    world.add_entity(mobile)
    world.set_area_of_effect("infant", "right-foot-position", "movement", "mobile")

    world.run(30)

    return world.log


def control_condition(experiment_log):
    infant = create_infant("random")
    mobile = create_mobile()
    experimenter = create_experimenter(experiment_log)

    world = World()
    world.add_entity(infant)
    world.add_entity(mobile)
    world.add_entity(experimenter)
    world.set_area_of_effect("experimenter", "mechanical-hand-position", "movement", "mobile")

    world.run(30)

    return world.log


if __name__ == '__main__':
    log = experimental_condition()

    #v = Visualizer()
    #v.visualize(log)

    #log2 = control_condition(log)

    #v.visualize(log2)
