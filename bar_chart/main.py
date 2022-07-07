from itertools import permutations
from os import listdir
from os.path import dirname, join
import datetime
from random import sample

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

total_time = 0
estimated_time = 233

worklogs = {}

colors = ['red', 'green', 'blue', 'orange', 'purple', 'yellow', 'pink', 'brown', 'black', 'grey', 'cyan', 'magenta', 'olive', 'teal']


def make_pie_chart():
    global worklogs
    fig, ax = plt.subplots(figsize=(7, 5))
    sum_by_author = {
        'Simon Pelletier': 0,
        'Jordan Choquet': 0,
        'Adam Beliveau': 0,
        'Jonathan Degoede': 0,
        'Joaquin Faundez Flores': 0,
        'Marie-Eve Castonguay': 0,
        'Antoine Laberge': 0
    }
    for week, data in worklogs.items():
        for i in data.index:
            if week != 'semaine 1':
                if i == 0:
                    ax.barh(y=data.loc[i, 'Author'], width=data.loc[i, 'time'],
                            left=sum_by_author[data.loc[i, 'Author']],
                            height=0.5, label=week, color=colors[int(week[8:]) - 1])
                else:
                    ax.barh(y=data.loc[i, 'Author'], width=data.loc[i, 'time'],
                            left=sum_by_author[data.loc[i, 'Author']],
                            height=0.5, color=colors[int(week[8:]) - 1])
                sum_by_author[data.loc[i, 'Author']] += data.loc[i, 'time']
            else:
                if i == 0:
                    ax.barh(y=data.loc[i, 'Author'], width=data.loc[i, 'time'], height=0.5, label=week,
                            color=colors[int(week[8:]) - 1])
                else:
                    ax.barh(y=data.loc[i, 'Author'], width=data.loc[i, 'time'], height=0.5, color=colors[int(week[8:]) - 1])
                sum_by_author[data.loc[i, 'Author']] = data.loc[i, 'time']
        ax.barh(y="Estimation d'heure", width=8, left=(int(week[8:]) - 1)*8, height=0.5, color=colors[int(week[8:]) - 1])

    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
    ax.set_xlabel('Heures travaillées (h)')
    plt.title(f'Heures travaillées par personne')
    plt.savefig(join(dirname(__file__), f'bar_chart_{datetime.datetime.now().date()}.png'), format='png',
                bbox_inches="tight")


def read_csv():
    global worklogs
    files = [x for x in listdir(join(dirname(__file__), 'csv')) if x.endswith('.csv')]
    for file in files:
        data = pd.read_csv(join(dirname(__file__), 'csv', file), dtype=object).rename({'Time spent seconds': 'time'},
                                                                                      axis=1)
        data['time'] = data['time'].astype(int)
        data.dropna(subset=['Author'], inplace=True)
        data['time'] = data.groupby('Author')['time'].transform('sum')
        data.drop_duplicates(['Author'], inplace=True)
        data = data[['Author', 'time']]
        data = data.sort_values(by=['Author'], ascending=False)

        data['time'] = data['time'].apply(lambda x: int(x) / 3600)

        worklogs.update({file.rstrip('.csv'): data})
    worklogs = dict(sorted(worklogs.items(), key=lambda x: int(x[0][8:])))


read_csv()
make_pie_chart()
