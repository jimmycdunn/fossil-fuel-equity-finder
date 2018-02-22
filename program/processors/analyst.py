import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz

class AnalystException(Exception):
    pass

class Analyst:
    """This guys job is to perform risk computations on the data within data structures"""
    def __init__(self, dfs):
        self.dfs = dfs

    def analyze(self, dataframefile):
        matchedDfs = self.match()
        # this is my intermediate write function that i will replace with final benchmarks
        for year in matchedDfs:
            dataframefile.data = matchedDfs[year]
            dataframefile.write(year+'assessment')

        targetHeld = self.compute_target_held(matchedDfs)
        for i in targetHeld:
            print(f"{i} {targetHeld[i]}%")
        # self.compute_carbon_held()
        # self.compute_carbon_quantiles()

    def match(self):
        # this should return one master dictionary by year with ALL data in one dataframe for that year
        # i.e. dfs['2016carbon_data']
        # pull the first 4 chars of the key and store to keep track of how many years
        matchedDfs = {}
        years = [key[:4] for key in self.dfs]
        for year in years:
            # pull that year's equity and carbon data
            # check to make sure there is equity, carbon, and financial data for that year
            try:
                equity = self.dfs[year+"equity_data"]
                carbon = self.dfs[year+"carbon_data"]
                financial = self.dfs[year+"financial_data"]
            except KeyError:
                print(f"No complete match for {year}")
                continue

            allColumns = [x for x in equity.columns] + [y for y in carbon.columns] + [z for z in financial.columns]
            # remove duplicate values from allColumns
            allColumns = set(allColumns)
            # create matchedDf with columns of all three data sets
            matchedDf = pd.DataFrame(index=range(len(equity.index)), columns=allColumns)
            # populate Stocks column for pd.merge(left, right, on='Stocks')
            matchedDf.Stocks = equity.Stocks

            # get lists of all companies in CARBON data and all companies in EQUITY data
            carbonCompanies = [x for x in carbon.loc[:, 'Company(Company)']]
            equityCompanies = [x for x in equity.loc[:, 'Stocks']]

            for carbonCompany in carbonCompanies:
                bestStocks = []

                # iterate through all equityCompanies and store matches of 100% to bestStocks
                for equityCompany in equityCompanies:
                    matchRatio = fuzz.token_set_ratio(equityCompany, carbonCompany) # this will match the best equityCompany to the current carbonCompany
                    if matchRatio != 100:
                        continue
                    else:
                        bestStocks.append(equityCompany)

                if len(bestStocks) == 0:
                    continue
                else:
                    # grab the data row from carbonCompanies for current carbonCompany
                    carbonRow = carbon['Company(Company)'] == carbonCompany
                    carbonValues = carbon[carbonRow]

                    for equityCompany in bestStocks:
                        # pull the index matching the stock in matchedDf for updating
                        carbonValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index # align indices
                        # pull the financial data
                        financialRow = financial['Stocks'] == equityCompany
                        financialValues = financial[financialRow]
                        financialValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index # align indices

                        # update matchedDf with both carbon and financial data
                        matchedDf.update(carbonValues)
                        matchedDf.update(financialValues)

            matchedDf.update(equity) # index is already aligned to equity

            # append populated matchedDf to the dictionary keyed by year
            matchedDfs[year] = matchedDf
            print("It's working...")
        return matchedDfs

    def compute_target_held(self, matchedDfs):
        # for each dataframe in matchedDfs
        targetHeld = {}
        for year in matchedDfs:
            df = matchedDfs[year]
            totalEquityValue = df['EndingMarketValue'].sum()
            targetEquityValue = df.loc[df['Company(Company)'].notnull(), 'EndingMarketValue'].sum()
            targetHeld[year] = targetEquityValue / totalEquityValue
        return targetHeld
