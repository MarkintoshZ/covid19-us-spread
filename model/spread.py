import os
import shutil
import configparser

from collections import namedtuple
from multiprocessing import Pool

import pandas as pd
import numpy as np
from tqdm import tqdm, trange

from county import County
from population import Population


config = configparser.ConfigParser()

Node = namedtuple('Node', ['state', 'county'])
Connection = namedtuple('Connection', ['destination', 'population'])

counties = {}


def spread(county):
    county.spread_work()
    county.spread_home()
    if VERBOSE:
        county.report()
    return county, county.log()


if __name__ == '__main__':
    # load settings
    config.read('settings.ini')
    VERBOSE = config['Computation'].getboolean('verbose')
    LOG = config['Computation'].getboolean('log')
    base_save_path = config['Path']['base_save_path']
    trail_name = config['Path']['trail_name']

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
                continue
    for v in tqdm(counties.values()):
        v.update_pop()

    print('set confirmed cases')
    start_date = config['Setup']['start_date'].split('-')
    start_date = pd.datetime(
        *[int(v) for v in start_date])
    virus_df = virus_df[virus_df.Date <= start_date]
    virus_df = virus_df.groupby(['State', 'County']).sum()['Case Count']
    print(virus_df)
    for idx, count in tqdm(virus_df.iteritems()):
        try:
            counties[Node(*idx)].add_confirmed(count)
        except KeyError:
            continue

    # iterate through days
    print('simulating')
    os.makedirs(base_save_path + \
                trail_name, exist_ok=True)
    for idx in trange(int(config['Setup']['iterations'])):
        # spread
        if config['Computation'].getboolean('multiprocessing'):
            with Pool(os.cpu_count()) as pool:
                log = pool.map(spread, list(counties.values()))
                county, log = zip(*log)
                df = pd.DataFrame(log, 
                    columns=['State', 'County', 'Population', 
                                'Infected', 'Immuned', 'Confirmed', 'Death'])
                df.to_csv(base_save_path + trail_name + \
                    (start_date + pd.DateOffset(day=idx)).strftime('%Y-%m-%d') + '.csv', 
                    index=False)
        else:
            [spread(county) for county in list(counties.values())]
            log = [county.log() for county in list(counties.values())]
            df = pd.DataFrame(log, 
                columns=['State', 'County', 'Population', 
                         'Infected', 'Immuned', 'Confirmed', 'Death'])
            df.to_csv(base_save_path + trail_name + \
                (start_date + pd.Timedelta(days=idx)).strftime('%Y-%m-%d') + '.csv', 
                index=False)
