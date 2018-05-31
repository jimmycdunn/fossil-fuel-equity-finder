import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz


class AnalystException(Exception):
    pass


class Analyst:
    """Analyst performs risk computations on the data within data structures"""
    def __init__(self, dfs):
        self.dfs = dfs

    def analyze_equity(self, dataframefile):
        # analyze will match the available data and then compute summary statistics
        # first, get the years that the user has requested
        years = sorted(set([key[:4] for key in self.dfs]))
        matchedData = self.match_data(years)
        # write the matched files to /assessment/
        for year in matchedData:
            dataframefile.data = matchedData[year]
            dataframefile.write(year+'assessment', path="./data/assessment/")
            companyNames = pd.DataFrame(dataframefile.data.loc[:, "Company(Company)"])
            companyNames = companyNames[companyNames.loc[:, "Company(Company)"].notnull()]
            companyNames["MarketCap(B)"] = None
            dataframefile.data = companyNames
            dataframefile.write(year+'MarketCaps', path="./data/financial_data/")

    def analyze_carbon(self, dataframefile):
        # get the years
        years = sorted(set([key[:4] for key in self.dfs]))
        # check if the user has financial data for this year
        completeData = {}
        for year in years:
            completeData[year] = self.dfs[year + "assessment"]
            try:
                financial = self.dfs[year+"financial_data"]
            except KeyError:
                print(f"No financial data for {year}, will not compute fair-share allocation")
                continue
            # if the user has financial data, update the matched data to include it
            completeData[year] = self.match_finance(year, completeData[year], financial)

        # compute carbon held if there was financial data provided
        analyzedData = self.analyze_data(completeData)
        # write fossil fuel assessment to CSV files in /benchmarks
        for year in analyzedData:
            dataframefile.data = analyzedData[year]
            dataframefile.write(year+'benchmarks', path="./data/benchmarks/")

    def match_data(self, years):
        matchedData = {}
        for year in years:
            # check if the user has equity data for this year
            try:
                equity = self.dfs[year+"equity_data"]
            except KeyError:
                print(f"No equity data for {year}, will not match")
                continue

            # check if the user has carbon data for this year
            try:
                carbon = self.dfs[year+"carbon_data"]
            except KeyError:
                print(f"No carbon data for {year}, will not match")
                continue
            # if the user has both equity and carbon data, match them
            matchedData[year] = self.match_equity(year, equity, carbon)


        return matchedData

    def match_equity(self, year, equity, carbon):
        # will return a dataframe with the matched data
        # first, instantiate the matched dataframe from the equity index
        # and the columns from both data files
        allColumns = [x for x in equity.columns] + [y for y in carbon.columns]
        # remove duplicate values from allColumns, order doesn't matter
        allColumns = set(allColumns)
        # create matchedDf with columns of all three data sets
        matchedDf = pd.DataFrame(index=range(len(equity.index)), columns=allColumns)
        # populate Stocks column for pd.merge(left, right, on='Stocks')
        matchedDf.Stocks = equity.Stocks

        # get a list of carbon comapnies and equity stock names for matching
        carbonCompanies = [x for x in carbon.loc[:, 'Company(Company)']]
        equityCompanies = [x for x in equity.loc[:, 'Stocks']]

        # iterate through all of the carbon companies first, because the user
        # is trying to see if a stock is on the carbon list
        for carbonCompany in carbonCompanies:
            bestStocks = [] # create a place to store best matches
            # for now, using edit distance w/90% match threshhold
            # in the future, would recommend cosine similarity to catch abbreviations
            for equityCompany in equityCompanies:
                matchRatio = fuzz.partial_token_set_ratio(equityCompany, carbonCompany)
                thresh = 90
                if matchRatio < thresh:
                    continue
                else:
                    bestStocks.append(equityCompany)

                # if there are no matches to the carbon company, then move on
                if len(bestStocks) == 0:
                    continue
                else:
                    # grab the data row from carbonCompanies for current carbonCompany
                    carbonRow = carbon['Company(Company)'] == carbonCompany
                    carbonValues = carbon[carbonRow]

                    # iterate if there are multiple stock options in one company
                    for equityCompany in bestStocks:
                        # pull the index matching the stock in matchedDf for updating and align indices
                        carbonValues.index = matchedDf[matchedDf['Stocks'] == equityCompany].index # ValueError
                        # the above error occurs when a company has a duplicate row in both the Coal AND Oil and Gas
                        # update matchedDf with both carbon data
                        matchedDf.update(carbonValues)

        matchedDf.update(equity)  # index is already aligned to equity
        print(f"{year} complete...")
        return matchedDf

    def match_finance(self, year, matchedDf, financial):
        # create a new column in matchedDf to include MktCap
        matchedDf["MarketCap(B)"] = None
        # iterate through the carbon company names in matchedDf
        carbonCompanies = matchedDf.loc[matchedDf.loc[:, "Company(Company)"].notnull()].loc[:, "Company(Company)"]
        for carbonCompany in carbonCompanies:
            # check if carbon company is in financial list
            if carbonCompany in financial.loc[:, "Company(Company)"].values:
                # get financial data linked to the company
                financialRow = financial.loc[:, 'Company(Company)'] == carbonCompany
                financialData = financial[financialRow].loc[:, "MarketCap(B)"].values[0]
                matchedRow = matchedDf.loc[:, "Company(Company)"] == carbonCompany
                matchedDf.loc[matchedRow, "MarketCap(B)"] = financialData

        return matchedDf

    def analyze_data(self, completeData):
        analyzedData = {}
        for year in completeData:
            df = completeData[year]
            fuels = self.get_fuels(df) # get fuels by year
            # modify the fuel names
            reserves = {k: k+v for k, v in fuels.items()}

            for key in reserves:
                # populate dataframe with intensities
                # fuels[key] is the units of the name of the fuel, market cap is in B
                try:
                    df[key + 'Intensity' + fuels[key] + '/$B'] = df[reserves[key]] / df['MarketCap(B)']
                    df[key + '(tCO2)'] = df[key + 'Intensity' + fuels[key] + '/$B'] * df['EndingMarketValue']
                except KeyError:
                    continue

            # remove infinities created by EMV = 0
            df = df.replace(np.inf, np.nan)
            # save rows that have a carbon company affiliated
            df = df[df.loc[:, "Company(Company)"].notnull()]
            # address companies with multiple stock options
            df = self.combine_multiple_stocks(df)

            for key in reserves:
                df[key + 'Pctile'] = df[reserves[key]].rank(pct=True)
                df[key + '(tCO2)Pctile'] = df[key + '(tCO2)'].rank(pct=True)

            analyzedData[year] = df
        return analyzedData

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
        multipleStockCompanies = set(df[df.duplicated(subset="Company(Company)")].loc[:, "Company(Company)"])
        for duplicate in multipleStockCompanies:
            combinedStocksCompany = pd.DataFrame()
            allCompanyStocks = df[df.loc[:, "Company(Company)"] == duplicate]
            keepSame = ["Company(Company)", "MarketCap(B)", "Stocks", "CoalIntensity(GtCO2)/$B",
                        "OilIntensity(GtCO2)/$B", "GasIntensity(GtCO2)/$B"]
            sumColumns = ["EndingMarketValue", "Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]

            for col in keepSame:
                combinedStocksCompany.loc[0,col] = allCompanyStocks.loc[:, col].values[0]

            for col in sumColumns:
                combinedStocksCompany.loc[0,col] = allCompanyStocks.loc[:, col].sum()

            df.drop(allCompanyStocks.index, inplace=True)
            df = df.append(combinedStocksCompany, ignore_index=True)

        return df
