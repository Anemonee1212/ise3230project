"""
This program determines the optimal farming strategy in the video game Stardew Valley
(https://www.stardewvalley.net/). The authors specifically emphasized the maximized
profit of 1st year generated only by farming. The solution is submitted as the final
project of OSU ISE 3230 course on 12/1/2021.

@Author: Anne Wei, Robert Shi
@Date: 11/20/2021
"""
__Anne_best_farm__ = 1

import cvxpy as cp
import pandas as pd

from config import *
from matplotlib import pyplot as plt


def harvest_land_constraints(constrts, ic, day, net_rev, dland, season):
    """
    - Define crop_harvest
    - "Free" the land if
        1. single-growth crops are harvested
        2. regrowth crops reach the end of season
    - Add crops revenue to net_rev
    """
    assert len(season) == 28

    gd = growth_day[ic, 0]
    rd = growth_day[ic, 1]
    if rd == -1 and day >= gd:  # Take the starting days into consideration
        constrts.append(crops_harvest[ic, day] == seeds_plant[ic, day - gd] * harvest_num[ic])
        dland += seeds_plant[ic, day - gd]
    elif rd == -1:
        constrts.append(crops_harvest[ic, day] == 0)
    elif ic == 17:  # Corns survive from summer to autumn, and thus needs 56 * 56 regrowth matrix
        day_in_season = day - 28
        assert 0 <= day_in_season <= 55
        constrts.append(
            crops_harvest[ic, day] == seeds_plant[ic, range(28, 84)] @ regrowth_harvest[ic][:, day_in_season]
        )
    else:
        day_in_season = day - season[0]
        assert 0 <= day_in_season <= 27
        constrts.append(
            crops_harvest[ic, day] == seeds_plant[ic, season] @ regrowth_harvest[ic][:, day_in_season]
        )
        if day_in_season == 27:
            dland += cp.sum(seeds_plant[ic, season])

    net_rev += (crops_harvest[ic, day] - crops_store[ic, day]) * sell_price[ic]
    return net_rev, dland


def keg_jar_constraints(constrts, day, net_rev):
    """
    - Enforce constraints on number of kegs and jars in use
    - Add artisan goods revenue to net_rev
    """
    if day >= 6:
        dkeg = cp.sum(keg[:, day])
        djar = cp.sum(jar[:, day])
        for ic in range(27):
            kd = keg_day[ic]
            jd = jar_day[ic]
            if kd > 0:
                dkeg -= keg[ic, day - kd]
                djar -= jar[ic, day - jd]
                net_rev += keg[ic, day - kd] * keg_price[ic]
                net_rev += jar[ic, day - jd] * jar_price[ic]

        if day <= 82:
            constrts.extend([
                dkeg == max_keg[0, day + 1] - max_keg[0, day],
                djar == max_jar[0, day + 1] - max_jar[0, day]
            ])

    return net_rev


def add_daily_constraints(constrts, day):
    """
    - Enforce constraints of money:
        money today = money yesterday - cost of seeds + revenue of sold crops
            + revenue of artisan goods
    - Enforce constraints of land:
        land today = land yesterday - number of seeds planted
            + number of single-growth crop harvested

    :param constrts: pointer to list of constraints
    :param day: number of days in the game - 1
    :return: dummy return
    """
    assert 0 <= day <= 83

    net_rev = -np.array(seed_price) @ seeds_plant[:, day]
    dland = -cp.sum(seeds_plant[:, day])
    if 0 <= day <= 27:  # Spring
        for ic in range(9):
            net_rev, dland = harvest_land_constraints(constrts, ic, day, net_rev, dland, range(28))

    elif 28 <= day <= 55:  # Summer
        for ic in range(9, 19):
            net_rev, dland = harvest_land_constraints(constrts, ic, day, net_rev, dland, range(28, 56))

    else:  # Autumn
        for ic in range(17, 27):
            net_rev, dland = harvest_land_constraints(constrts, ic, day, net_rev, dland, range(56, 84))

    net_rev = keg_jar_constraints(constrts, day, net_rev)
    constrts.extend([
        money[day + 1] == money[day] + net_rev,
        land[day + 1] == land[day] + dland
    ])

    return 0


def add_zero_constraints(constrts):
    """
    Preliminary constraints
    """
    # Each crop has specific season(s) to plant and harvest
    constrts.extend([
        seeds_plant[0:9, 28:84] == 0,
        seeds_plant[9:28, 0:28] == 0,
        seeds_plant[9:17, 56:84] == 0,
        seeds_plant[19:28, 28:56] == 0,
        crops_harvest[0:9, 28:84] == 0,
        crops_harvest[9:28, 0:28] == 0,
        crops_harvest[9:17, 56:84] == 0,
        crops_harvest[19:28, 28:56] == 0
    ])

    # Strawberry seeds can only be purchased at day 13/14
    constrts.append(seeds_plant[6, 0:13] == 0)

    # Artisan goods are not allowed in starting days
    constrts.extend([
        keg[:, 0:18] == 0,
        jar[:, 0:18] == 0
    ])

    return 0


def output_solution(data, file, sheet_name):
    """
    Output optimal solution into Excel Spreadsheets for future analysis

    :param data: numpy.ndarray
    :param file: pandas.ExcelWriter
    :param sheet_name: Sheet name to specify in Excel
    :return: dummy return
    """
    df = pd.DataFrame(data)
    df.index = crops_dict.values()
    df = df.loc[np.any(df != 0, axis = 1)]
    df.to_excel(file, sheet_name)
    print("<<< Successfully written \"" + sheet_name + "\" >>>")
    return 0


if __name__ == '__main__':
    money = cp.Variable((85, ), nonneg = True)              # The money (gold) in the game
    land = cp.Variable((85, ), integer = True)              # The area of land available
    seeds_plant = cp.Variable((27, 84), integer = True)     # Number of seeds planted
    crops_harvest = cp.Variable((27, 84), integer = True)   # Number of crops harvested
    crops_store = cp.Variable((27, 84), integer = True)     # Number of harvest crops stored
    keg = cp.Variable((27, 84), integer = True)             # Number of inventory put into keg
    jar = cp.Variable((27, 84), integer = True)             # Number of inventory put into jar

    inventory = cp.cumsum(crops_store - keg - jar, axis = 1)

    constraints = [
        money[0] == init_gold,
        land[0] == max_land,
        land >= 0,
        land <= max_land,
        seeds_plant >= 0,
        crops_harvest >= crops_store,
        crops_store >= 0,
        keg >= 0,
        jar >= 0,
        inventory >= 0,
        cp.sum(inventory, axis = 0) <= max_inv
    ]

    add_zero_constraints(constraints)
    for iday in range(84):
        add_daily_constraints(constraints, iday)

    val_func = money[84]
    # Winter: all inventories preserved into artisan goods
    val_func += np.maximum(keg_price, jar_price) @ inventory[:, 83]

    problem = cp.Problem(cp.Maximize(val_func), constraints)
    problem.solve(solver = cp.GUROBI, verbose = True)

    print()
    print("Maximized money (gold) at the end of 1 year is: ")
    print(val_func.value)
    print()

    with pd.ExcelWriter("output/strategies.xlsx") as writer:
        output_solution(seeds_plant.value, writer, "Farming")
        output_solution(crops_harvest.value, writer, "Harvested")
        output_solution(crops_harvest.value - crops_store.value, writer, "Sold")
        output_solution(crops_store.value, writer, "Stored")
        output_solution(inventory.value, writer, "Inventory")
        output_solution(keg.value, writer, "Keg use")
        output_solution(jar.value, writer, "Jar use")

    plt.plot(range(86), np.append(money.value, val_func.value))
    plt.show()

    print()
    print("Session Terminated.")

