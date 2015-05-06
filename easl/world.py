__author__ = 'Dennis'

import csv


class Sensor(object):
    def __init__(self):
        self.observations = None

    def set_observations(self, observations):
        """
        Args:
            observations: a dictionary that the Sensor can use to put interpreted
                observations in.
        """
        self.observations = observations

    def detects_modality(self, modality):
        return False

    def notify(self, signal):
        pass


class Signal(object):
    def __init__(self, modality=None, sig_type=None, value=None):
        """
        Attributes:
            modality: string describing the modality that this signal is for
            type: string describing the type of signal this is; an abstract
                description
            value: any value associated with the signal
        """
        self.modality = modality
        self.sig_type = sig_type
        self.value = value


class Log(object):
    """
    Simple log that contains all experiment information (actions, observations).

    Time based. Logs for every time step what happened.

    Can (not yet) be read from/to files etc.
    """
    # TODO: How to get information from Agent? Make local Log?
    def __init__(self, fname=None):
        self.log = []
        self.verbose = False

        if fname is not None:
            self.__from_file(fname)

    def set_verbose(self):
        self.verbose = True

    def add_entry(self, time, kind, data):
        self.log.append([time, kind, data])

    def write_file(self, name):
        f = open(name, 'wt')
        try:
            writer = csv.writer(f)
            for entry in self.log:
                writer.writerow(entry)
        finally:
            f.close()

    def __from_file(self, name):
        f = open(name, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                self.log.append(tuple(row))
        finally:
            f.close()


class World(object):
    """
    Handles and arranges Entities and handles interactions between any
    observable event and its observer(s).

    Describing a World consists of describing the Entities in it and the
    relations between those Entities.

    Part is based on the RegionalSenseManager from "Artificial Intelligence for
    Games" while ignoring some parts as the representation used in this simulation
    is a kind of 'distanceless' representation.
    In other words, only the essentials.

    Differences with RegionalSenseManager:
     * no distances.
     * no notification queue, since all notifications are handled immediately.
     * signals are added in the beginning phase of a frame and sent at the end
       phase, which means all signals can be sent when all entities have been
       processed.

    Attributes
    ----------
    entities : {name: Entity}
        all entities in the world identified by name
    signals : [(Sensor, Signal)]
        All queued signals with their destinations.
    actions
    triggers : [(Entity, Entity, string)]
        the connections between entities that link actions and triggers
    time
    log
    """
    # TODO: Redesign event system, including area(?) of effect.
    def __init__(self):
        self.entities = {}

        self.signals = []
        self.actions = []

        self.triggers = []

        self.time = 0

        self.log = None

    def run(self, iterations=10):
        """
        Runs the simulation once with the currently specified Entities
        and relations between them.
        """
        self.log = Log()
        self.log.set_verbose()

        # Initialize initial states of all entities, including agents
        for e in self.entities:
            self.entities[e].start()

        for i in range(iterations):
            self.time = i

            print "step " + str(i)
            self.__do_physics()

            self.__queue_signals()
            self.__send_signals()

            self.__queue_actions()
            self.__execute_actions()

            self.__trigger_events()

            self.print_state()

        self.log.write_file("log.csv")

    def add_entity(self, name, entity):
        self.entities[name] = entity

    def set_in_area_of_effect(self, affected, event, area):
        """
        Setting the area of effect of an entity's change in attribute
        means that the affected entity's triggers are triggered when the
        attribute changes.

        This can be used to model position etc.

        Parameters
        ----------
        affected : string
            name of the entity that is to be triggered by the action
        event : string
            name of the type of event
        area : string
            identifier of the area that is affected
        """
        self.area_of_effect.append((affected, event, area))

    def set_area_of_effect(self, causing, attribute, event, affected):
        """

        Parameters
        ----------
        causing : string
            Name of the Entity that caused the event.
        attribute : string
            Name of the attribute of the Entity that caused the event.
        event : string
            Name of the type of event that occurred.
        affected : string
            Name of the Entity that is affected by the event.
        """
        self.triggers.append((causing, attribute, event, affected))

    def __do_physics(self):
        """
        Calls all Entities' physics method.
        """
        for entity in self.entities:
            self.entities[entity].physics(self.entities[entity])

    def __queue_signals(self):
        """
        Takes all signals that were queued to be emitted and sends queues them
        to be sent to the appropriate receivers.
        """
        for sender in self.entities:
            # First see if it still emits more signals.
            self.entities[sender].emit_signals()

            for signal in self.entities[sender].get_queued_signals():
                for receiver in self.entities:
                    for sensor in self.entities[receiver].sensors:
                        if not sensor.detects_modality(signal.modality):
                            continue

                        self.signals.append((sensor, signal))

    def __send_signals(self):
        while len(self.signals) > 0:
            n = self.signals.pop(0)
            n.sensor.notify(n.signal)

    def __queue_actions(self):
        """
        Makes all Entities prepare their actions.

        The querying and execution phase of the actions should be separated,
        because actions have effects on the Entities' attributes and all
        actions should be selected at the same point in time.
        """
        # Collect the actions by all entities and put them in one list

        for entity in self.entities:
            self.entities[entity].queue_actions()

    def __execute_actions(self):
        """
        Executes all actions
        """
        for entity in self.entities:
            entity.execute_actions()

    def __trigger_events(self):
        for cause in self.entities:
            while len(self.entities[cause].event_queue) > 0:
                attribute, event, params = self.entities[cause].event_queue.pop(0)

                # Find all entities that are triggered by this event
                for (causer, causer_attribute, caused_event, affected) in self.triggers:
                    if causer == cause and causer_attribute == attribute and caused_event == event:
                        self.entities[affected].call_trigger(event, params)

    def print_state(self):
        # Show all individual entity's state
        for entity in self.entities:
            print entity
            print self.entities[entity].print_state()
