import matplotlib.pyplot as plt

newD = {1: {'program': [111.7, 114.1, 111.2],
            'programavg': 112.33333333333333,
            'rawchunk': 15728640,
            'rawchunkMB': 15.0,
            'rawsteralisedchunk': 378152,
            'rawsteralisedchunkMB': 0.36063385009765625},
        4: {'program': [192.2, 191.8, 193.1],
            'programavg': 192.36666666666667,
            'rawchunk': 62914560,
            'rawchunkMB': 60.0,
            'rawsteralisedchunk': 805160,
            'rawsteralisedchunkMB': 0.7678604125976562},
        9: {'program': [319.2, 319.4, 320.3],
            'programavg': 319.63333333333327,
            'rawchunk': 141557760,
            'rawchunkMB': 135.0,
            'rawsteralisedchunk': 1256744,
            'rawsteralisedchunkMB': 1.1985244750976562},
        16: {'program': [504.4, 493.4, 509.9],# New Optimsations
             'programavg': 502.5666666666666,  # 300
             'rawchunk': 251658240,  # 16777368 NOW 2097304
             'rawchunkMB': 240.0, # 16
             'rawsteralisedchunk': 1732904,
             'rawsteralisedchunkMB': 1.6526260375976562},
        25: {'program': [718.9, 719.5, 720.2],
             'programavg': 719.5333333333334,
             'rawchunk': 393216000,
             'rawchunkMB': 375.0,
             'rawsteralisedchunk': 2233640,
             'rawsteralisedchunkMB': 2.1301651000976562},
        36: {'program': [970.5, 997.7],
             'programavg': 984.1,
             'rawchunk': 566231040,
             'rawchunkMB': 540.0,
             'rawsteralisedchunk': 2758952,
             'rawsteralisedchunkMB': 2.6311416625976562},
        49: {'program': [1326.3, 1315.5],
             'programavg': 1320.9,
             'rawchunk': 770703360,
             'rawchunkMB': 735.0,
             'rawsteralisedchunk': 3308840,
             'rawsteralisedchunkMB': 3.1555557250976562},
        64: {'program': [1684.4],
             'programavg': 1684.4,
             'rawchunk': 1006632960, # 8388760
             'rawchunkMB': 960.0,
             'rawsteralisedchunk': 3883304,
             'rawsteralisedchunkMB': 3.7034072875976562}}

type = "rawsteralisedchunkMB"
x = newD.keys()

y = [data[type] for data in newD.values()]

plt.plot(x, y)
plt.show()