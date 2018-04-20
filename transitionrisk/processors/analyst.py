import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz


class AnalystException(Exception):
    pass


class Analyst:
    """Analyst performs risk computations on the data within data structures"""
    def __init__(self, dfs, cellAddresses):
        self.dfs = dfs
        self.cellAddresses = cellAddresses

    def analyze(self, dataframefile):
        matchedDfs = self.match()
        # this is my intermediate write function that i will replace with benchmark design
        for year in matchedDfs:
            dataframefile.data = matchedDfs[year]
            dataframefile.write(year+'assessment', path="./data/carbon_assessment/")
            # filter for flagged carbon rows

        # BUILD OUT BENCHMARK CLASS AND CALL ITS METHODS HERE
        #benchmark = Benchmark(matchedDfs, self.cellAddresses)
        #benchmark.write_benchmarks()

        targetHeld = self.compute_target_held(matchedDfs)
        # print outputs of targetHeld to commandline for now
        for i in targetHeld:
            print(f"{i} {targetHeld[i]}%")

        carbonHeld = self.compute_carbon_held(matchedDfs)
        for year in carbonHeld:
            dataframefile.data = carbonHeld[year]
            dataframefile.write(year+'analysis', path="./data/benchmarks/")
        # write final assessment to a CSV file
        # DEVELOP: summary statistics to print to commandline

    def match(self):
        # this should return one master dictionary by year with ALL data in one dataframe for that year
        # i.e. dfs['2016carbon_data']
        # pull the first 4 chars of the key and store to keep track of how many years
        matchedDfs = {}
        years = set([key[:4] for key in self.dfs])
        print(years)
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
                        # match financial data before replacing index in carbon values
                        currentCarbonCompany = carbonValues['Company(Company)'].values[0]
                        financialRow = financial['Company'] == currentCarbonCompany
                        financialValues = financial[financialRow]
                        # pull the index matching the stock in matchedDf for updating and align indices
                        carbonValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index # ValueError
                        # the above error occurs when a company has a duplicate row in both the Coal AND Oil and Gas
                        # for now, I'm concatenating values in the CSV itself but think about generalizing
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
                # populate dataframe with absolute CO2 held per stock ($ held * CO2 intensity)
                df[key + '(tCO2)'] = df[key + 'Intensity' + fuels[key] + '/$B'] * df['EndingMarketValue']
                # calculate the percentile of total reserves while we're here
            # remove any infinities created by EMV = 0
            df = df.replace(np.inf, np.nan)
            # only save rows that have carbon allocated to them
            df = df[df.loc[:, "Company(Company)"].notnull()]
            # address companies with multiple stock options here
            df = self.combine_multiple_stocks(df)

            for key in reserves:
                df[key + 'Pctile'] = df[reserves[key]].rank(pct=True)
                df[key + '(tCO2)Pctile'] = df[key + '(tCO2)'].rank(pct=True)
                # df[key + 'DivestRatio'] = df[key + 'Intensity' + fuels[key] + '/$B'].divide(df['EndingMarketValue'])
            # drop financial rows not needed in this view
            # 4/12/18 I'm commenting out this drop step because
            # 1) I cant guarantee what the equity columns will include
            # and 2) there is no harm in including all data in the analysis view for now
            #df = df.drop(labels=['Shares', 'Price', 'EndingMarketValue', 'MarketCap(B)'], axis=1)
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

    def combine_multiple_stocks(self, df):
        # returns an analysis dataframe with multiple stock rows combined
        # into one company row to aggregate holdings across multiple
        # options in a company
        multipleStockCompanies = set(df[df.duplicated(subset="Company")].Company)
        for duplicate in multipleStockCompanies:
            combinedStocksCompany = pd.DataFrame()
            allCompanyStocks = df[df.Company == duplicate]
            keepSame = ["Company", "MarketCap(B)", "Stocks", "CoalIntensity(GtCO2)/$B",
                        "OilIntensity(GtCO2)/$B", "GasIntensity(GtCO2)/$B"]
            sumColumns = ["EndingMarketValue", "Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]

            for col in keepSame:
                combinedStocksCompany.loc[0,col] = allCompanyStocks.loc[:, col].values[0]

            for col in sumColumns:
                combinedStocksCompany.loc[0,col] = allCompanyStocks.loc[:, col].sum()

            df.drop(allCompanyStocks.index, inplace=True)
            df = df.append(combinedStocksCompany, ignore_index=True)

        return df
