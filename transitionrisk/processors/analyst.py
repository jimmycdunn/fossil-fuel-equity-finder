import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz


class AnalystException(Exception):
    pass


class Analyst:
    """Analyst performs risk computations on the data within data structures"""
    def __init__(self, dfs):
        self.dfs = dfs

    def analyze(self, dataframefile):
        matchedDfs = self.match()
        # this is my intermediate write function that i will replace with benchmark design
        for year in matchedDfs:
            dataframefile.data = matchedDfs[year]
            dataframefile.write(year+'assessment', path="../carbon_assessment/")
            # filter for flagged carbon rows

        # BUILD OUT BENCHMARK CLASS AND CALL ITS METHODS HERE

        targetHeld = self.compute_target_held(matchedDfs)
        # print outputs of targetHeld to commandline for now
        for i in targetHeld:
            print(f"{i} {targetHeld[i]}%")

        carbonHeld = self.compute_carbon_held(matchedDfs)
        for year in carbonHeld:
            dataframefile.data = carbonHeld[year]
            dataframefile.write(year+'analysis', path="../benchmarks/")
        # write final assessment to a CSV file
        # DEVELOP: summary statistics to print to commandline

    def match(self):
        # this should return one master dictionary by year with ALL data in one dataframe for that year
        # i.e. dfs['2016carbon_data']
        # pull the first 4 chars of the key and store to keep track of how many years
        matchedDfs = {}
        years = [key[:4] for key in self.dfs]
        for year in years:
            print(f"{year}")
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
                    # this will match the best equityCompany to the current carbonCompany
                    matchRatio = fuzz.token_set_ratio(equityCompany, carbonCompany)
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
                        # pull the index matching the stock in matchedDf for updating and align indices
                        carbonValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index

                        # pull the financial data
                        financialRow = financial['Stocks'] == equityCompany
                        financialValues = financial[financialRow]

                        # align indices
                        financialValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index

                        # update matchedDf with both carbon and financial data
                        matchedDf.update(carbonValues)
                        matchedDf.update(financialValues)

            matchedDf.update(equity)  # index is already aligned to equity

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

    def compute_carbon_held(self, matchedDfs):
        # returns a dictionary of dataframes with carbon holdings information for each dataframe in matchedDfs
        carbonHeld = {}
        # find where the columns with units are - those like Name(Units)
        # pull the name from the Name and pull the Units from (Units)
        # populate fuels with Name != Company
        for year in matchedDfs:
            df = matchedDfs[year]
            fuels = self.get_fuels(df)  # I'm giving the user flexibility to do fuels by year
            # dictionary comprehension to modify the names
            reserves = {k: k+v for k, v in fuels.items()}

            for key in reserves:
                # populate dataframe with intensities (tCO2/$ of company market cap)
                # fuels[key] is the units of the name of the fuel, market cap has to be in B
                df[key + 'Intensity' + fuels[key] + '/$B'] = df[reserves[key]] / df['MarketCap(B)']
                # calculate the percentile of total reserves while we're here
                df[key + 'Pctile'] = df[reserves[key]].rank(pct=True)
                df[key + '(tCO2)'] = df[key + 'Intensity' + fuels[key] + '/$B'] * df['EndingMarketValue']
                # populate dataframe with absolute CO2 held per stock ($ held * CO2 intensity)
                df[key + '(tCO2)Pctile'] = df[key + '(tCO2)'].rank(pct=True)
                # df[key + 'DivestRatio'] = df[key + 'Intensity' + fuels[key] + '/$B'].divide(df['EndingMarketValue'])

            # remove any infinities created by EMV = 0
            df = df.replace(np.inf, np.nan)
            # only save rows that have carbon allocated to them
            df = df[df.loc[:, "Company(Company)"].notnull()]
            # drop financial rows not needed in this view
            df = df.drop(labels=['Shares', 'Price', 'EndingMarketValue', 'MarketCap(B)'], axis=1)
            carbonHeld[year] = df

        return carbonHeld

    def get_fuels(self, df):
        # returns a dictionary with keys as names of fuels and values of units of fuels
        fuels = {}
        for col in df.columns:
            if '(' in col and 'Company' not in col and 'MarketCap' not in col:
                # split the column into name and (unit) at the (
                splitCol = col.split('(')
                name = splitCol[0]
                unit = '(' + splitCol[1]  # add leading parenthesis back in
                fuels[name] = unit
        return fuels
