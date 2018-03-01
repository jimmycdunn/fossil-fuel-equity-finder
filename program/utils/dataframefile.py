import numpy as np
import pandas as pd
from datetime import date

class DataFrameFileException(Exception):
    pass

class DataFrameFile:
    """ Wrapper around dataframe supporting file operations"""
    def __init__(self, data=None):
        self.data = data

    def read(self, fileName):
        """Read in filename, store in self.data"""
        self.data = pd.read_csv(fileName, encoding = "ISO-8859-1") # make sure fileName is correct
        return self.data

    def write(self, fileName, path=None):
        """Write current dataframe to fileName"""
        # if data is none raise exception
        if self.data is None:
            raise DataFrameFileException("No data to write.")
        self.data.to_csv(path + self.get_file_prefix() + fileName + '.csv') # make sure fileName is correct

    @staticmethod
    def get_file_prefix(today=date.today()):
        return ''.join([str(i) for i in today.timetuple()[0:3]])
