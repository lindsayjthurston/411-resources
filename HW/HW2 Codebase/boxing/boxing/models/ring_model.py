import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """Represents a boxing ring that holds boxers and manages fights.
    
    This class simulates a boxing ring where two boxers can enter, fight, and have their statistics updated based on the outcome of the fight.
    """
    def __init__(self):
        """Initializes an empty list of boxers in the ring."""
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates a fight between two boxers in the ring.
        
        The fight is based on the boxers' skills, and a winner is determined using a probability function.
        
        Returns:
            str: The name of the winning boxer.
        
        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        # Determine the winner based on the skill difference
        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Clears the ring by removing all boxers."""
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to be added to the ring.

        Raises:
            TypeError: If the object is not a `Boxer`.
            ValueError: If the ring is already full.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of boxers currently in the ring."""
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates a boxer's fighting skill based on arbitrary factors.

        Args:
            boxer (Boxer): The boxer whose skill is being calculated.

        Returns:
            float: The fighting skill of the boxer.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill