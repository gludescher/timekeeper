import pandas as pd
import sys
import os

class TimeDataframe(object):
    CURRENT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

    def __init__(self, path=CURRENT_DIR, file_name="timekeeper.csv"):
        self.__df = pd.DataFrame()
        self.__path = path
        self.__file_name = file_name

    def open(self, force_create_new=False):
        if not force_create_new and os.path.exists(self.__path+'/'+self.__file_name):
            self.__open_dataframe()
        else:
            self.__create_dataframe()
        pass

    def __open_dataframe(self):
        self.__df = pd.read_csv(self.__path+'/'+self.__file_name, parse_dates=['date', 'begin_time', 'end_time'])
        pass

    def __create_dataframe(self):    
        self.__df = pd.DataFrame(columns=['date', 'begin_time', 'end_time', 'comments'])
        pass

    def close(self):
        self.__df.sort_values(by='date').to_csv(self.__path+'/'+self.__file_name, index=False)
        pass

    def add(self, date, begin_time, end_time, comment):
        new_row = self.__df.shape[0]
        self.__df.loc[new_row] = [date, begin_time, end_time, comment]
        return new_row

    def read(self, id):
        return self.__df.loc[id]

    def update(self, id, data, begin_time, end_time, comment):
        self.__df.loc[id] = [data, begin_time, end_time, comment]
        pass

    def length(self):
        return self.__df.shape[0]

    def last_entry_id(self, end_time=None):
        if end_time:
            return self.__df[(pd.isnull(self.__df['end_time'])) & (self.__df['begin_time'] < end_time)].tail(1).index[0]
        else:
            return 0 if self.__df.shape[0] == 0 else self.__df.shape[0] - 1

    def get_entries_between(self, start_date, end_date):
        return self.__df[(self.__df['date'] >= start_date) & (self.__df['date'] <= end_date)]

    def get_all(self):
        return self.__df
