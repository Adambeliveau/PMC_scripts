import datetime
from datetime import timedelta
import re
from os.path import dirname, join

import pandas as pd

UNITS = {'s':'seconds', 'm':'minutes', 'h':'hours', 'd':'days', 'w':'weeks'}
splited_worklogs = pd.DataFrame()


def split_worklogs(row):
    try:
        if row['Author'] in splited_worklogs.columns and row['Issue'] in splited_worklogs.index:
            splited_worklogs.loc[row['Issue'], row['Author']] += round(int(row['Time spent seconds'])/3600, 2)
        else:
            splited_worklogs.loc[row['Issue'], row['Author']] = round(int(row['Time spent seconds'])/3600, 2)
            splited_worklogs.fillna(0, inplace=True)
    except KeyError as e:
        print(e)


worklogs = pd.read_csv(join(dirname(__file__), 'worklogs.csv'), dtype=object)[['Author', 'Issue', 'Time spent seconds']].apply(lambda x: split_worklogs(x), axis=1)
timesheet = pd.read_csv(join(dirname(__file__), 'timesheet-per-issue.csv'), dtype=object).rename({'Key': 'Issue'}, axis=1).set_index('Issue')
issues = pd.read_csv(join(dirname(__file__), 'issues.csv'), dtype=object).rename({'Issue key': 'Issue'}, axis=1)[['Summary', 'Issue']].set_index('Issue')


def make_timelogs():
    timelogs = pd.concat([timesheet, splited_worklogs], axis=1, join="inner").iloc[:-1, :-1]
    timelogs.drop(columns=['Summary'], inplace=True)
    timelogs = issues.join(timelogs, on='Issue', how='left')
    timelogs.fillna('', inplace=True)
    timelogs.drop(['Total time spent'], axis=1, inplace=True)
    timelogs.rename(columns=lambda x: re.sub(r'Time spent(.*)', 'Total time spent', x), inplace=True)
    timelogs['Estimated time'] = timelogs.apply(lambda x: calculate_estimated_time(x), axis=1)
    timelogs['Progress'] = timelogs['Progress'].apply(lambda x: x + '%')
    timelogs = timelogs.apply(lambda x: add_id_to_summary(x), axis=1)
    timelogs = timelogs[['Summary', 'Total time spent', 'Estimated time', 'Progress', 'Marie-Eve Castonguay', 'Antoine Laberge', 'Simon Pelletier', 'Jordan Choquet', 'Adam Beliveau', 'Jonathan Degoede', 'Joaquin Faundez Flores']]
    timelogs.to_csv(join(dirname(__file__), f'timelogs_{datetime.date.today()}.csv'), index=False)


def calculate_estimated_time(row):
    total_time = convert_to_seconds(row['Total time spent']) if row['Total time spent'] else 0
    progress = row['Progress'] if row['Progress'] else 0
    try:
        estimated_time = str(int(round((total_time / (int(progress) / 100)) / 3600, 0))) + 'h'
    except ZeroDivisionError:
        estimated_time = '0h'
    return estimated_time


def add_id_to_summary(row):
    row['Summary'] = '[' + row.name + '] ' + row['Summary']
    return row


def convert_to_seconds(s):
    return int(timedelta(**{
        UNITS.get(m.group('unit').lower(), 'seconds'): float(m.group('val'))
        for m in re.finditer(r'(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)', s, flags=re.I)
    }).total_seconds())


make_timelogs()