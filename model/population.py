import math
from random import uniform
from collections import deque
import numpy as np


class Population:
    """Class for simulating single body population

    Static Attributes
    ----------
    self_recover_rate : float
        chance of self recovering
    self_recover_time : int
        average iterations (days) needed to recover
    infection_rate : float
        possibility of getting infected by 1 person in 1 iteration
    hospitalized_rate : float
        percentage of infected turns into hospitalized after self_recover_time

    Attributes
    ----------
    population : int
        total population
    infected : int
        number of people currently infected
    uninfected : int
        number of people who has never been infected (they do not have immunity)
    immuned : int
        number of people who has immunity for the disease (have been infected and had recovered)
    hospitalized: int
        number of death after being hospitalized (since spread of virus after hospitalized is low,
        people who have been hospitalized but recovered counts in attribute immuned)s
    Methods
    -------
    spread() -> None
        simulate spreading of disease for 1 iteration (day)
    """
    self_recover_rate = 0.9
    self_recover_time = 4     # iterations (days)
    infection_rate = 0.5      # possibility of getting infected by 1 person in 1 iteration
    confirm_rate = 0.2        # percentage of infected turns into confirmed case after self_recover_time
    death_rate = confirm_rate*0.019         # percentage of infected turns into death after self_recover_time

    def __init__(self, population, infected=0, immuned=0, confirmed=0, death=0):
        assert population > 0, 'negative population'
        assert infected >= 0, 'negative infected'
        assert immuned >= 0, 'negative immuned'
        assert confirmed >= 0, 'negative confirmed'
        assert death >= 0, 'negative death'

        self.population = population
        self.infected = infected
        self.uninfected = population - infected
        self.immuned = immuned
        self.confirmed = confirmed
        self.death = death # represents the death count after being hospitalized
        self._infection_history = deque([], maxlen=Population.self_recover_time + 1)

    def _add_sick_count(self, n):
        n = min(n, self.uninfected)
        self.infected += n
        self.uninfected -= n
        return n

    def set_confirmed(self, n):
        sick = n / Population.confirm_rate
        sick = self._add_sick_count(sick)
        self.confirmed = sick * Population.confirm_rate

    def spread(self, new_infected=None):
        """spread() -> None
        simulate spreading of disease for 1 iteration (day)
        """
        if not new_infected:
            new_infected = math.floor(self.infected \
                * ((self.uninfected) / self.population) \
                * (Population.infection_rate)) #+ uniform(-0.1, 0.1)))
        if (int(round(new_infected)) < 0):
            print('negative!')
        new_infected = self._add_sick_count(int(round(new_infected)))
        self._infection_history.append(new_infected)
        if len(self._infection_history) >= Population.self_recover_time:
            old_infection = self._infection_history.popleft()
            conds = np.random.rand(old_infection)
            new_death = (conds < Population.death_rate).sum()
            new_confirmed = (conds < Population.confirm_rate).sum()
            self.confirmed += new_confirmed
            self.death += new_death
            self.immuned += old_infection - new_death
            self.infected -= old_infection

    def __str__(self):
        pop = self.population
        return "Population: {} | Infected: {} ({:.2f}) | ".format(pop, self.infected, self.infected / pop) + \
               "Uninfected: {} ({:.2f}) | ".format(self.uninfected, self.uninfected / pop) + \
               "Immuned: {} ({:.2f}) | ".format(self.immuned, self.immuned / pop) + \
               "Confirmed: {} ({:.2f}) | ".format(self.confirmed, self.confirmed / pop) + \
               "Death: {} ({:.2f}) ".format(self.death, self.death / pop)


if __name__ == "__main__":
    pop = Population(327.2E6, infected=53/Population.confirm_rate, confirmed=53)
    for i in range(20):
        print(f'Day {i+1}')
        print(pop)
        pop.spread()

    pop = Population(2250, infected=9)
    for i in range(20):
        print(f'Day {i+1}')
        print(pop)
        pop.spread()
