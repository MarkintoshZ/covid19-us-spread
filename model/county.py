from random import randint
from collections import namedtuple
from functools import reduce

import numpy as np

from community import Community
from population import Population


class County:
    work_spread_rate = 1.1
    home_spread_rate = 1.1

    def __init__(self, state: str, county: str, pop: int, 
                 area: float, lat: float, lon: float):
        self.state = state
        self.county = county
        self.population = pop
        self.area = area
        self.latitude = lat
        self.longitude = lon

        self.day_populations = []
        self.residence_populations = []

    def add_work_pop(self, pop):
        self.day_populations.append(pop)

    def add_home_pop(self, pop):
        self.residence_populations.append(pop)

    def update_pop(self):
        pop = reduce(lambda v, p: v + p.population, self.residence_populations, 0)
        if self.population - pop > 0:
            self.day_populations.append(Population(self.population - pop))
        pop = reduce(lambda v, p: v + p.population, self.residence_populations, 0)
        if self.population - pop > 0:
            self.residence_populations.append(Population(self.population - pop))

    def spread_work(self):
        Community.spread(self.day_populations)

    def spread_home(self):
        Community.spread(self.residence_populations)

    def report(self):
        infected = self.total_value('infected')
        confirmed = self.total_value('confirmed')
        death = self.total_value('death')
        print('{} {}: '.format(self.state, self.county) + \
              'infected: {} {:0.2}% | '.format(infected, infected/self.population) + \
              'confirmed: {} {:0.2}% | '.format(confirmed, confirmed/self.population) + \
              'death: {} {}%'.format(death, death/self.population))

    def log(self):
        return [self.state, self.county, self.population] + \
            [self.total_value(n) for n in ['infected', 'immuned', 'confirmed', 'death']]

    def total_value(self, attri_name):
        return reduce(lambda v, obj: v + getattr(obj, attri_name), 
            self.residence_populations, 0)

    def add_confirmed(self, confirmed):
        prob = [p.population for p in self.residence_populations]
        # normalize to sum == 1
        prob = np.array(prob)
        prob = prob / prob.sum()
        choices = np.random.choice(
            len(self.residence_populations), confirmed, 
            p=prob)
        choices = np.unique(choices, return_counts=True)
        for i, c in zip(*choices):
            self.residence_populations[i].set_confirmed(c)
