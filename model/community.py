from functools import reduce
from random import uniform
import math

from population import Population


class Community:
    """Class for simulating multiple population bodies

    Static Methods
    -------
    spread(population, ...) -> None
        simulate spreading of disease when given population were joined for 1 iteration (day)
    """
    @staticmethod
    def spread(populations):
        """spread(population, ...) -> None
        simulate spreading of disease when given population were joined for 1 iteration (day)
        """
        uninfected = [p.uninfected for p in populations]
        infected = [p.infected for p in populations]
        total_uninfected = reduce(lambda l, r: l + r, uninfected, 0)
        total_infected = reduce(lambda l, r: l + r, infected, 0)
        total_population = reduce(lambda l, p: l + p.population, populations, 0)
        # print(total_infected, total_population)
        # calculate total new infected
        new_infected = math.floor(total_infected \
                * ((total_uninfected) / total_population) \
                * (Population.infection_rate))# + uniform(-0.1, 0.1)))
        for u, p in zip(uninfected, populations):
            p.spread(new_infected=new_infected * (u/total_uninfected))


if __name__ == "__main__":
    pop0 = Population(100, infected=3)
    pop1 = Population(1000, infected=1)
    pop2 = Population(100, infected=0)
    pop3 = Population(1000, infected=0)
    pop4 = Population(50, infected=5)
    pops = [pop0, pop1, pop2, pop3, pop4]
    for i in range(20):
        print(f'Day {i+1}')
        for p in pops:
            print(p)
        Community.spread(pops)
