"""
Configurations.
Game data from https://stardewvalleywiki.com/Crops
"""
import numpy as np

init_gold = 500
max_land = 20
max_inv = 50
max_keg = np.maximum(np.floor(np.array(range(84)) / 7) - 5, 0).reshape((1, -1))
max_jar = np.maximum(np.floor(np.array(range(84)) / 5) - 3, 0).reshape((1, -1))

crops_dict = {
    0: "Blue Jazz", 1: "Cauliflower", 2: "Green Bean", 3: "Kale", 4: "Parsnip", 5: "Potato", 6: "Strawberry",
    7: "Tulip", 8: "Unmilled Rice", 9: "Blueberry", 10: "Hops", 11: "Hot Pepper", 12: "Melon", 13: "Poppy",
    14: "Radish", 15: "Summer Spangle", 16: "Tomato", 17: "Corn", 18: "Wheat", 19: "Amaranth", 20: "Bok Choy",
    21: "Cranberries", 22: "Eggplant", 23: "Fairy Rose", 24: "Grape", 25: "Pumpkin", 26: "Yam"
}

seed_price = [30, 80, 60, 70, 20, 50, 100, 20, 40, 80, 75, 40, 80, 100, 40, 50, 50, 150, 10, 70, 50, 240, 20, 200,
              60, 100, 60]
sell_price = [50, 175, 40, 110, 35, 80, 120, 30, 30, 150, 25, 40, 250, 140, 90, 90, 60, 50, 25, 150, 80, 150, 60,
              290, 80, 320, 160]
keg_price = [-1, 394, 90, 248, 79, 180, 360, -1, 68, 450, 300, 120, 750, -1, 203, -1, 135, 113, 200, 338, 180, 450,
             135, -1, 240, 720, 360]
jar_price = [-1, 400, 130, 270, 120, 210, 290, -1, 110, 350, 100, 130, 550, -1, 230, -1, 170, 150, 100, 350, 210,
             350, -1, -1, 210, 690, 370]

growth_day = np.array([
    [7, -1], [12, -1], [10, 3], [6, -1], [4, -1], [6, -1], [8, 4], [6, -1],
    [6, -1], [13, 4], [11, 1], [5, 3], [12, -1], [7, -1], [6, -1], [8, -1],
    [11, 4], [14, 4], [4, -1], [7, -1], [4, -1], [7, 5], [5, 5], [12, -1],
    [10, 3], [13, -1], [10, -1]
])
keg_day = [-1, 4, 4, 4, 4, 4, 6, -1, 4, 6, 2, 6, 6, -1, 4, -1, 4, 4, 1, 4, 4, 6, 4, -1, 6, 4, 4]
jar_day = [-1, 3, 3, 3, 3, 3, 3, -1, 3, 3, 3, 3, 3, -1, 3, -1, 3, 3, 3, 3, 3, 3, 3, -1, 3, 3, 3]

harvest_num = [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]

regrowth_harvest = [None] * 27
for icrop in range(27):
    rday = growth_day[icrop, 1]
    if rday > 0:
        gday = growth_day[icrop, 0]
        regrowth_harvest[icrop] = np.array(
            [[(b in range(d + gday, 29, rday)) * harvest_num[icrop] for b in range(28)] for d in range(28)]
        )

regrowth_harvest[17] = np.array([[(b in range(d + 14, 57, 4)) for b in range(56)] for d in range(56)])
