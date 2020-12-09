import pandas as pd
import sys
import os

class TimeDataDataframe(object):
    CURRENT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

    def __init__(self, path=CURRENT_DIR, file_name="timekeeper.csv"):
        self.__df = None
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
        self.__df = pd.DataFrame(columns=['date', 'begin_time', 'end_time', 'time_spent', 'comments'])
        pass

    def close(self):
        self.__df.sort_values(by='date').to_csv(self.__path+'/'+self.__file_name, index=False)
        pass

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
        