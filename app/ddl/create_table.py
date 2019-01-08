#  -*- encoding: utf-8 -*-

import psycopg2

from app.common.constants_and_variables import AppVariables, AppConstants


class CreateTable(object):

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()

    def create_table(self):
        database_connection = psycopg2.connect(self.app_variables.database_url, sslmode='require')
        cursor = database_connection.cursor()
        cursor.execute(self.app_constants.QUERY_CREATE_TABLE)
        cursor.close()
        database_connection.commit()
        database_connection.close()


if __name__ == '__main__':
    create_table_athlete_stats = CreateTable()
    create_table_athlete_stats.create_table()
