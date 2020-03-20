import os

from random import randint
from collections import namedtuple
from functools import reduce
from multiprocessing import Pool

import pandas as pd
import numpy as np
from tqdm import tqdm, trange

from population import Population
from community import Community


# constants
MULTIPROCESSING = True

START_DATE = pd.datetime(2020, 2, 24)
SPREAD_DAYS = 30

Node = namedtuple('Node', ['state', 'county'])
Connection = namedtuple('Connection', ['destination', 'population'])

counties = {}


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
        infected = self.total_infected()
        confirmed = self.total_confirmed()
        death = self.total_death()
        print('{} {}: '.format(self.state, self.county) + \
              'infected: {} {:0.2}% | '.format(infected, infected/self.population) + \
              'confirmed: {} {:0.2}% | '.format(confirmed, confirmed/self.population) + \
              'death: {} {}%'.format(death, death/self.population))

    def total_infected(self):
        infected = [p.infected for p in self.residence_populations]
        return reduce(lambda l, r: l + r, infected, 0)

    def total_confirmed(self):
        confirmed = [p.confirmed for p in self.residence_populations]
        return reduce(lambda l, r: l + r, confirmed, 0)

    def total_death(self):
        death = [p.death for p in self.residence_populations]
        return reduce(lambda l, r: l + r, death, 0)

    def add_confirmed(self, confirmed):
        choices = np.random.choice(
            len(self.residence_populations), confirmed, 
            p=[p.population for p in self.residence_populations])
        for i, c in enumerate(choices):
            self.residence_populations[i].set_confirmed(c)


def spread(county, report=False):
    county.spread_work()
    county.spread_home()
    if report:
        county.report()


def main():
    # load data
    df = pd.read_csv('data/cleaned/data_complete.csv')
    cunts = df[['State', 'County', 'Population', 'Total Area (km)', 
                'Latitude','Longitude']].drop_duplicates().reset_index(drop=True)
    cmmt = df[['State', 'County', 'Work State', 'Work County', 
            'Commuting Flow','Margin of Error']].drop_duplicates().set_index('State', drop=True)
    virus_df = pd.read_csv('data/cleaned/virus.csv', parse_dates=['Date'])

    # instantiate communites
    print('instantiating communites')
    for _, row in tqdm(cunts.iterrows()):
        counties[Node(row.State, row.County)] \
            = County(*row.values)
    # set connections
    print('setting connections')
    for key in tqdm(counties.keys()):
        state = cmmt.loc[key.state]
        cnncts = state[state['County'] == key.county]
        cnncts = cnncts[['Work State', 'Work County', 'Commuting Flow']].values
        for work_state, work_county, pop_size in cnncts:
            pop = Population(pop_size)
            counties[key].add_home_pop(pop)
            try:
                counties[Node(work_state, work_county)].add_work_pop(pop)
            except KeyError:
                # print(f'{Node(work_state, work_county)} does not exist in dataset')
                pass
    for v in tqdm(counties.values()):
        v.update_pop()

    # TODO
    # print('set confirmed cases')
    # virus_df = virus_df[virus_df.Date <= START_DATE]
    
    # print(virus_df)
    # virus_df = virus_df.groupby(['State', 'County']).sum()
    # print(virus_df)
    # exit()
    # # print(virus_df)
    # for _, row in tqdm(virus_df.iterrows()):
    #     print(row)
    #     counties[Node(*row[-2:])].add_confirmed(row['sum'])

    # iterate through days
    print('simulating')
    for idx in trange(SPREAD_DAYS):
        # spread
        if MULTIPROCESSING:
            with Pool(os.cpu_count()) as pool:
                pool.map(spread, list(counties.values()))
        else:
            for county in list(counties.values()):
                spread(county)


if __name__ == '__main__':
    main()
