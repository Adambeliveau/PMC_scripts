from os.path import dirname, join
import datetime

import pandas as pd
import matplotlib.pyplot as plt

total_time = 0
estimated_time = int(int((datetime.datetime.now().date() - datetime.datetime.strptime('2022-05-02', '%Y-%m-%d').date()).days / 7)*(945/15))


def make_pie_chart(filename):
    global total_time
    data = pd.read_csv(join(dirname(__file__), filename), dtype=object).rename({'Time spent seconds': 'time'}, axis=1)
    data['time'] = data['time'].astype(int)
    total_time = data.iloc[-1]['time'] / 3600
    data.dropna(subset=['Author'], inplace=True)
    data['time'] = data.groupby('Author')['time'].transform('sum')
    data.drop_duplicates(['Author'], inplace=True)
    data = data[['Author', 'time']]

    data['time'] = data['time'].apply(lambda x: int(x) / 3600)

    fig, ax = plt.subplots()
    tempsum = 0
    for i in data.index:
        if i > 0:
            ax.bar(x=f"total de l'équipe: {total_time:.0f}h", height=data.loc[i, 'time'], bottom=tempsum, width=0.5, label=data.loc[i, 'Author'])
        else:
            ax.bar(x=f"total de l'équipe: {total_time:.0f}h", height=data.loc[i, 'time'], width=0.5, label=data.loc[i, 'Author'])
        tempsum += data.loc[i, 'time']

    ax.bar(x=f'total estimée: {estimated_time}h', height=estimated_time, width=0.5, label='total estimée')
    ax.bar(x='\n', height=0, width=1)
    ax.legend(loc='upper right')
    plt.title(f'Heures travaillées par personne (total: {total_time:.2f}h)')
    plt.savefig(join(dirname(__file__), f'bar_chart_{datetime.datetime.now().date()}.png'), format='png')


def slice_value(x):
    return f'{(x / 100) * total_time:.2f}h ({x:.2f}%)'


make_pie_chart('worklogs.csv')
