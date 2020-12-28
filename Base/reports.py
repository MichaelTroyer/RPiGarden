# -*- coding: utf-8 -*-
"""
Created on 2020-10-26
@author: michael

report.py creates the data summary, air temperature and humidity charts, pickles the df
for the period of interest and emails it to the email within the yaml file using the
email and password in the yaml file (emails to self).

Schedule using cron.
"""


import datetime
import getpass
import os
import yaml

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import gmail

from database import Database


ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REPORT_DIR = os.path.join(ROOT, 'Reports')


def create_line_chart(column, title, y_axis):
    chartFig, chartAx = plt.subplots()
    column.plot(kind='line', ax=chartAx, title=title)
    column.rolling(100).mean().plot(kind='line', ax=chartAx)
    chartAx.set_xlabel('Time')
    chartAx.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    chartAx.set_ylabel(y_axis)
    fig_path = os.path.join(REPORT_DIR, f'{column.name}.png')
    chartFig.savefig(fig_path)
    return fig_path


def create_summary(data):
    min_date = data.index.min().date()
    max_date = data.index.max().date()
    if min_date == max_date:
        date_str = min_date
    else:
        date_str = f'{min_date} - {max_date}'

    finished_charts = []
    charts_to_create = [
        (data.AirTemperature, f'Air Temperature\n[{date_str}]', 'Degrees Fahrenheit'),
        (data.Humidity, f'Humidity\n[{date_str}]', 'Percent Humidity'),
        ]
    for chart in charts_to_create:
        finished_charts.append(create_line_chart(*chart))

    summary = f'{date_str}\n'
    for col in data.columns:
        summary += str(col) + '\n'
        summary += data[col].describe().apply("{0:.2f}".format).to_string() + '\n\n'

    return summary, finished_charts


def send_email(email_add, passx, subject, body, atts=None):
    mail = gmail.GMail(email_add, passx)
    mail.connect()
    msg = gmail.Message(subject=subject, to=email_add, text=body, attachments=atts)
    mail.send(msg)
    mail.close()


def email_report(database, email_add, passx, start=None, end=None):
    df = Database(database)
    data = df.get_data(start, end)
    df_pickle = os.path.join(REPORT_DIR, 'DataFrame.pkl')
    data.to_pickle(df_pickle)
    summary, charts = create_summary(data)
    attachments = charts + [df_pickle]
    send_email(email_add, passx, f'Daily Report: {start}', summary, attachments)


if __name__ == '__main__':

    import sys

    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    database = os.path.join(root, 'Data', 'Garden.db')
    yamlfile = os.path.join(root, 'Base', 'config', 'config.yaml')

    with open(yamlfile) as f:
        credentials = yaml.safe_load(f)

    args = sys.argv
    end = datetime.datetime.now()
    if not len(args) == 3:
        start = end - datetime.timedelta(days=1)
    else:
        # e.g. python report.py days 3
        unit, period = args[1:3]
        start = end - datetime.timedelta(**{unit:int(period)})

    report(
        database,
        credentials['Email'],
        credentials['Password'],
        start,
        end,
        )
