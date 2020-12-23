# -*- coding: utf-8 -*-
"""
Created 2020-10-26
@author: michael
"""


import datetime
import os
import sqlite3

import pandas as pd


class Database():
    """
    Database is a class for handling database creation as well as adding and
    retrieving records from the GardenData table.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        if not os.path.exists(db_path):
            self.build_database()

    def build_database(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            create = """CREATE TABLE IF NOT EXISTS GardenData (
                        DateTime date,
                        AirTemperature real,
                        Humidity real,
                        HeaterOn integer,
                        FanOn integer
                        );"""
            cur.execute(create)

    def add_data(self, data):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO GardenData values (?,?,?,?,?)",
                (                
                    data['DateTime'],
                    data['AirTemperature'],
                    data['Humidity'],
                    data['HeaterOn'],
                    data['FanOn'],
                    )
                )

    def get_data(self, start_date=None, end_date=None):
        filters = []
        if start_date:
            filters.append(("DateTime > ?", start_date))
        if end_date:
            filters.append(("DateTime < ?", end_date))
        with sqlite3.connect(self.db_path) as con:
            query = "SELECT * FROM GardenData"
            if filters:
                clauses = [f[0] for f in filters]
                query += " WHERE " + " AND ".join(clauses)
            df = pd.read_sql(
                query, con,
                params=[f[1] for f in filters],
                parse_dates='DateTime',
                index_col='DateTime',
                )
            return df


if __name__ =='__main__':

    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    database = os.path.join(root, 'Data', 'Garden.db')

    today = datetime.date.today()

    db = Database(database)
    data = db.get_data(start_date=today)
    print(data)