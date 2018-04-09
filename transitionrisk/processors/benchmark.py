import numpy as np
import pandas as pd

from openpyxl import Workbook

class BenchmarkException(Exception):
    pass

class Benchmark:
    '''
    Benchmark will take values passed into it and write them to specific cells
    within an XLSX workbook for high level benchmarking of transition risk
    '''

    def __init__(self, equity={}, carbon={}, cellAddresses={}):
        self.equity = equity # equity is % invested and companies held
        self.carbon = carbon # carbon is aggregate CO2 reserves invested
        self.cellAddresses = cellAddresses # a static list that will contain the

    def write_cell(data):
        '''
        write_cell() will take a value and place it in the corresponding
        excel cell based on the value's key in the dictionary
        '''
        # example
        # data = {'Number Companies Flagged': 64}
        # self.celladdress[data.key] will return 'B7'
        # if in the excel sheet, 'Number Companies Flagged' is located in B7
        # BUT the '64' will be written in the rightmost adjacent empty cell

    def write_benchmarks(data):
        '''
        write_benchmarks() will read in a Excel workbook and go through
        all of the benchmarks provided in equity and carbon and call
        write_cell() to put them in the correct cells in the Excel workbook
        '''
