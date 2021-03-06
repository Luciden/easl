__author__ = 'Dennis'

from mechanism import Mechanism
from easl import *
from easl.visualize import *
import random


class NewSimpleVisual(Visual):
    @staticmethod
    def visualize(self):
        trees = {}
        for action in self.motor_signals_and_domains:
            trees[action] = {}
            for value in self.motor_signals_and_domains[action]:
                trees[action][value] = 0.0

        for combination in self.all_possibilities(self.motor_signals_and_domains):
            for k, v in combination.iteritems():
                trees[k][v] += self.probabilities.get_value(combination)

        group = Group("simple")
        for action in trees:
            group.add_element(Tree(action, trees[action]))

        return group


class OperantConditioningMechanism(Mechanism):
    """ Reinforces motor signals that are followed by a 'reward' state.

    Attributes
    ----------
    observations : {name: value}
        Stores current, new, observations.
    rule : LearningRule
    action : (name, value)
        The action that was performed last.
    counts : {name: {value: int}}
        Maintains a count for any action/value pair.
    rewards : [(name, value)]
        List of sensory stimuli that are considered as rewarding.
    """
    def __init__(self, rewards):
        """
        Parameters
        ----------
        rewards : [(name, value)]
            List of sensory stimuli that are considered as rewarding.
        """
        super(OperantConditioningMechanism, self).__init__()
        self.visual = NewSimpleVisual()

        self.observations = {}
        self.rewards = rewards

        self.action = None
        self.probabilities = None

        self.motor_signal_valuation = lambda x: 1.0
        self.motor_signal_bias = 1.0

        self.delta_pos = 0.1
        self.delta_neg = 0.05
        self.min_probability = 0.01

    def init_internal(self, entity):
        super(OperantConditioningMechanism, self).init_internal(entity)

        # Initialize the probability table
        self.probabilities = utils.FullTable(self.motor_signals_and_domains)
        # Initialize with uniform distribution
        # Count total possibilities
        n = len(self.all_possibilities(self.motor_signals_and_domains))

        p = 1 / float(n)
        self.probabilities.map_function_over_all_values(lambda x: p)
        print self.probabilities.table

    def set_motor_signal_bias(self, valuation, bias):
        self.motor_signal_valuation = valuation
        self.motor_signal_bias = bias

    def sense(self, observation):
        name, value = observation

        self.observations[name] = value

    def act(self):
        # Change the counts according to selected action and whether a
        # reward is present
        if self.action is not None:
            self.__update_probabilities(self.__got_reward())

        # Select a new action (max probability)
        self.action = self.__select_action()

        return [(x, y) for x, y in self.action.iteritems()]

    def __select_action(self):
        """
        Select the combination of actions with the maximum likelihood of
        resulting in a reward.
        """
        values = []
        total = 0.0

        print self.probabilities.table

        possibilities = self.all_possibilities(self.motor_signals_and_domains)

        for combination in possibilities:
            v = self.probabilities.get_value(combination) * self.motor_signal_valuation(combination)
            values.append(v)

            total += v

        r = random.random() * total

        cumulative = 0.0
        for i in range(len(values)):
            cumulative += values[i]

            if cumulative >= r:
                print "Selected {0}, which had probability {1}".format(possibilities[i], values[i] / float(total))
                return possibilities[i]

    def __update_probabilities(self, rewarded):
        old = self.probabilities.get_value(self.action)
        new = 0

        # Change probability of one particular
        if rewarded:
            print "Rewarded"
            new = old + self.delta_pos
        else:
            new = max(old - self.delta_neg, self.min_probability)

        self.probabilities.set_value(self.action, new)

        # Renormalize
        self.__normalize(1.0 + (new - old))

        print "Old: {0}, New {1}, Normalized {2}".format(old, new, self.probabilities.get_value(self.action))

    def __normalize(self, new_total):
        self.probabilities.map_function_over_all_values(lambda x: x / float(new_total))

    def __increase_probability(self, combination):
        old = self.probabilities.get_value(self.action)

        # Change probability of one particular
        new = old + self.delta_pos

        self.probabilities.set_value(combination, new)

        return new - old

    def __update_probabilities_subsets(self, rewarded):
        if rewarded:
            print "Rewarded"
            new_total = 1.0
            for combination in self.all_possibilities(self.motor_signals_and_domains):
                match = False

                for k, v in self.action.iteritems():
                    if combination[k] == v:
                        match = True

                if match:
                    new_total += self.__increase_probability(combination)
            print "New {0}".format(new_total)
            self.__normalize(new_total)
        else:
            self.__update_probabilities(rewarded)

    def __got_reward(self):
        """
        Returns
        -------
        got_reward : boolean
            True if a rewarding stimulus is present, False otherwise.
        """
        for (name, value) in self.rewards:
            if name in self.observations and self.observations[name] == value:
                return True
        return False
