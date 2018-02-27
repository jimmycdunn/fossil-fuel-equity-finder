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
            dataframefile.write(year+'assessment') # UPDATE: .write to include a PATH argument

        targetHeld = self.compute_target_held(matchedDfs)
        # print outputs of targetHeld to commandline for now
        for i in targetHeld:
            print(f"{i} {targetHeld[i]}%")

        carbonHeld = self.compute_carbon_held(matchedDfs)
        for year in carbonHeld:
            dataframefile.data = carbonHeld[year]
            dataframefile.write(year+'analysis') # UPDATE: .write to include a PATH argument
        # write final assessment to a CSV file
        # DEVELOP: summary statistics to print to commandline

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

    def compute_carbon_held(self, matchedDfs):
        # returns a dictionary of dataframes with carbon holdings information for each dataframe in matchedDfs
        carbonHeld = {}
        fuels = ['Coal', 'Oil', 'Gas'] # I manually instantiate this but i need to pull it from the column headers
        # find where the columns with units are - those like Name(Units)
        # pull the name from the Name and pull the Units from (Units)
        # populate fuels with Name != Company
        for year in matchedDfs:
            df = matchedDfs[year]
            fuels = self.get_fuels(df) # I'm giving the user flexibility to do fuels by year
            # dictionary comprehension to modify the names
            reserves = {k:k+v for k, v in fuels.items()} # I'm not sure i can append v to k so easily but i can try

            for key in reserves:
                # populate dataframe with intensities (tCO2/$ of company market cap)
                df[key + 'Intensity' + fuels[key] + '/$B'] = df[reserves[key]] / df['MarketCap(B)'] # fuels[key] is the units of the name of the fuel, market cap has to be in B
                df[key + 'Pctile'] = df[reserves[key]].rank(pct=True) # calculate the percentile of total reserves while we're here
                df[key + '(tCO2)'] = df[key + 'Intensity' + fuels[key] + '/$B'] * df['EndingMarketValue'] # populate dataframe with absolute CO2 held per stock ($ held * CO2 intensity)
                df[key + '(tCO2)Pctile'] = df[key + '(tCO2)'].rank(pct=True)
                df[key + 'DivestRatio'] = df[key + 'Intensity' + fuels[key] + '/$B'] / df['EndingMarketValue'] # populate dataframe with ratio of intensity to holdings (CO2 intensity / $ held)

            # remove any infinities created by EMV = 0
            df = df.replace(np.inf, np.nan)
            # drop financial rows not needed in this view
            df = df.drop(labels=['Shares', 'Price', 'EndingMarketValue', 'MarketCap(B)'], axis=1)
            carbonHeld[year] = df

        return carbonHeld

        def get_fuels(self, df):
            # returns a dictionary(?) with keys as names of fuels and values of units of fuels
            fuels = {}
            for col in df.columns:
                # split the column into name and (unit) at the (
                splitCol = col.split('(') # this may not work if col is a Index object and not a str; maybe have to use .values[0]
                name = splitCol[0]
                unit = splitCol[1]
                fuels[name] = unit
            return fuels
