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

    def __init__(self, data, cellAddresses={}):
        self.data = data # passing in matchedDfs to compute key metrics
        self.cellAddresses = cellAddresses # a static list that will contain the

    def write_benchmarks():
        '''
        write_benchmarks() will read in a Excel workbook and go through
        all of the benchmarks provided in equity and carbon and call
        write_cell() to put them in the correct cells in the Excel workbook
        '''

    def write_cell():
        '''
        write_cell() will take a value and place it in the corresponding
        excel cell based on the value's key in the dictionary
        '''
        # example
        # data = {'Number Companies Flagged': 64}
        # self.celladdress[data.key] will return 'B7'
        # if in the excel sheet, 'Number Companies Flagged' is located in B7
        # BUT the '64' will be written in the rightmost adjacent empty cell

    def compute_metrics():
        '''
        compute_metrics() will look through the equity and carbon data to
        aggregate sum of equity investments and held reserves
        '''
        # compute sum of dollars held in carbon Companies

        # compute percentage of dollars held in carbon companies compared to
        # total individual equity

        # compute aggregate coal risk in $
        # compute aggregate oil risk in $
        # compute aggregate natural gas risk in $

        # compute aggregate carbon reserves in invested companies (GtCO2)
        # compute aggregate invested reserves
        # compute percentage of invested reserves to total reserves

        # compute aggregate invested coal holdings
        # compute aggregate invested oil holdings
        # compute aggregate invested natural gas holdings

    def compute_top_holdings():
        '''
        compute_top_holdings() will sort coal, oil, and gas stocks by invested
        holdings and will write the top 10%, top 25%, and top 50 percent
        companies to the excel sheet for visualization
        '''

        # aggregate company duplicates here?
        # sort by top coal invested holdings
        # write out the top 10%
        # write out the top 25%
        # write out the top 50%

        # repeat for oil and natural gas
