import math
from datetime import timedelta
import re
from os.path import dirname, join

import pandas as pd
import matplotlib.pyplot as plt

UNITS = {'s':'seconds', 'm':'minutes', 'h':'hours', 'd':'days', 'w':'weeks'}
splited_worklogs = pd.DataFrame()


def split_worklogs(row):
    try:
        if row['Author'] in splited_worklogs.columns and row['Issue'] in splited_worklogs.index:
            splited_worklogs.loc[row['Issue'], row['Author']] += round(int(row['Time spent seconds'])/3600, 2)
        splited_worklogs.loc[row['Issue'], row['Author']] = round(int(row['Time spent seconds'])/3600, 2)
    except KeyError as e:
        print(e)


worklogs = pd.read_csv(join(dirname(__file__), 'worklogs.csv'), dtype=object)[['Author', 'Issue', 'Time spent seconds']].apply(lambda x: split_worklogs(x), axis=1)
timesheet = pd.read_csv(join(dirname(__file__), 'timesheet-per-issue.csv'), dtype=object).rename({'Key': 'Issue'}, axis=1).set_index('Issue')


def make_timelogs():
    timelogs = pd.concat([timesheet, splited_worklogs], axis=1, join="inner").iloc[:-1, :-1]
    timelogs.drop(['Total time spent'], axis=1, inplace=True)
    timelogs.rename(columns=lambda x: re.sub(r'Time spent(.*)', 'Total time spent', x), inplace=True)
    timelogs['Estimated time'] = timelogs.apply(lambda x: calculate_estimated_time(x), axis=1)
    timelogs['Progress'] = timelogs['Progress'].apply(lambda x: x + '%')
    timelogs = timelogs[['Summary', 'Total time spent', 'Estimated time', 'Progress', 'Marie-Eve Castonguay', 'Antoine Laberge', 'Simon Pelletier', 'Jordan Choquet', 'Adam Beliveau', 'Jonathan Degoede', 'Joaquin Faundez Flores']]
    timelogs.to_csv(join(dirname(__file__), 'timelogs.csv'), index=False)


def calculate_estimated_time(row):
    total_time, progress = convert_to_seconds(row['Total time spent']), row['Progress']
    return str(int(round((total_time / (int(progress) / 100)) / 3600, 0))) + 'h'


def convert_to_seconds(s):
    return int(timedelta(**{
        UNITS.get(m.group('unit').lower(), 'seconds'): float(m.group('val'))
        for m in re.finditer(r'(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)', s, flags=re.I)
    }).total_seconds())


make_timelogs()