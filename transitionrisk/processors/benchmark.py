import numpy as np
import pandas as pd
import os
from transitionrisk.utils.dataframefile import DataFrameFile
from datetime import datetime
from IPython.display import display, HTML

from transitionrisk.utils.dataframefile import DataFrameFile

class BenchmarkException(Exception):
    pass

class Benchmark:
    '''
    Benchmark will host the back end code for data visualization in the
    front-end Ipython Notebook to make the user experience cleaner
    '''

    def __init__(self, years, data={}, aggregateTable=None):
        self.years = years # user will pass in years
        self.data = data
        self.aggregateTable = aggregateTable

    def show_sample_tables(self, switch=None):
        if switch == "Carbon":
            columns = ["Company(Company)", "Coal(GtCO2)", "Oil(GtCO2)", "Gas(GtCO2)"]
            data = {
                "Company(Company)" : ["Best Coal", "Some Gas", "More Oil", "Better Coal", "Decent Coal"],
                "Coal(GtCO2)" : [10.0,0.0,0.0,20.0,5.0],
                "Oil(GtCO2)" : [0, 5.0, 10.0, 0, 0],
                "Gas(GtCO2)" : [0, 2.5, 2.5, 0, 0],
            }
            df = pd.DataFrame(data, columns=columns)

        elif switch == "Equity":
            columns2 = ["Stocks", "EndingMarketValue"] #any other columns you include will be preserved but won't be operated on
            data2 = {
                "Stocks" : ["SM GAS CLASS A", "MORE OIL", "DCT COAL OPTIONS", "BST COAL", "BTTR COAL 2"],
                "EndingMarketValue" : [54987651.0, 13654977.0, 546879852.0, 1124568.0, 1549865.0]
            }
            df = pd.DataFrame(data2, columns=columns2)

        elif switch == "Financial":
            columns3 = ["Company", "MarketCap(B)"] # make sure you convert whatever the listed market caps are to B
            data3 = {
                "Company" : ["Best Coal", "Some Gas", "More Oil", "Better Coal", "Decent Coal"],
                "MarketCap(B)" : [25.8, 50.2, 44.3, 10.0, 0.5]
            }
            df = pd.DataFrame(data3, columns=columns3)

        else:
            print("Please select a sample table to view.")

        return display(df)

    # pull the data frames that were written out by Analyst
    def get_tables(self):
        dataframefile = DataFrameFile()
        data = {}
        with os.scandir(path="./data/benchmarks") as it:
            currentFiles = [x.name for x in it]  # store name attributes of all files in a folder
            recentDate = max([datetime.strptime(fileName[:8], "%Y%m%d") for fileName in currentFiles])
            recentDate = datetime.strftime(recentDate, "%Y%m%d")
            for fileName in currentFiles:
                if recentDate in fileName:
                    df = dataframefile.read(os.path.join('./data/benchmarks/', fileName))
                    data[fileName[8:12]] = df
        assert len(data.keys()) == len(self.years)
        self.data = data
        return self.data

    def company_names(self):
        for year in self.years:
            companyNames = self.data[year]["Company"].values
            numberOfCompanies = len(companyNames)
            print(f"{year}")
            print(f"You owned investments in {numberOfCompanies} fossil fuel companies:")
            companySentence = ", ".join(companyNames)
            print(f"{companySentence}")

    def get_total_equity(self):
        # read in the equity dataframes
        dataframefile = DataFrameFile()
        data = {}
        with os.scandir(path="./data/equity_data") as it:
            currentFiles = [x.name for x in it]  # store name attributes of all files in a folder
            for fileName in currentFiles:
                df = dataframefile.read(os.path.join("./data/equity_data/", fileName))
                data[fileName[0:4]] = df
        assert len(data.keys()) == len(self.years)
        totalEquity = {}
        for year in data:
            totalEquity[year] = data[year]["EndingMarketValue"].sum()
        return totalEquity

    def aggregate_table(self):
        # make Total Individual Equity column
        totalEquity = self.get_total_equity()
        totalEquity = pd.DataFrame.from_dict(data=totalEquity, orient="index")
        totalEquity.columns = ["Total Individual Equity"]

        # make the aggregate columns with Year
        aggregateColumns = ["Year"]
        aggregateTable = pd.DataFrame(columns=aggregateColumns)
        aggregateTable.loc[:, aggregateColumns] = 0
        aggregateTable.loc[:, "Year"] = self.data.keys()
        aggregateTable.set_index("Year", inplace=True)

        # initiate table to aggregate fossil fuel equity by fuel type
        fossilFuelEquity = pd.DataFrame()

        row = 0
        for year in self.data:
            fossilFuelEquity.loc[row, "Year"] = year
            fossilFuelEquity.loc[row, "Fossil Fuel Equity"] = self.data[year].loc[:, "EndingMarketValue"].sum()
            row += 1
        fossilFuelEquity.set_index("Year", inplace=True)

        # dollars by fuel type
        coalEmv = {}
        oilEmv = {}
        gasEmv = {}

        for year in self.data:
            coalRows = self.data[year].loc[:, "Coal(tCO2)"] > 0
            oilRows = self.data[year].loc[:, "Oil(tCO2)"] > 0
            gasRows = self.data[year].loc[:, "Gas(tCO2)"] > 0
            # to allocate dollars by fuel type, divide fuel type reserve by sum of total reserves and multiply by EMV
            totalReservesCoal = self.data[year].loc[coalRows, ["Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]].sum(axis=1)
            coalEmv[year] = ((self.data[year].loc[coalRows, "Coal(tCO2)"] / totalReservesCoal)
                              * self.data[year].loc[coalRows, "EndingMarketValue"])
            totalReservesOil = self.data[year].loc[oilRows, ["Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]].sum(axis=1)
            oilEmv[year] = ((self.data[year].loc[oilRows, "Oil(tCO2)"] / totalReservesOil)
                              * self.data[year].loc[oilRows, "EndingMarketValue"])
            totalReservesGas = self.data[year].loc[gasRows, ["(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]].sum(axis=1)
            gasEmv[year] = ((self.data[year].loc[gasRows, "Gas(tCO2)"] / totalReservesGas)
                              * self.data[year].loc[gasRows, "EndingMarketValue"])

        coalEquity = pd.DataFrame()
        oilEquity = pd.DataFrame()
        gasEquity = pd.DataFrame()

        row = 0
        for year in self.data:
            coalEquity.loc[row, "Year"] = year
            coalEquity.loc[row, "Coal Equity"] = coalEmv[year].sum()

            oilEquity.loc[row, "Year"] = year
            oilEquity.loc[row, "Oil Equity"] = oilEmv[year].sum()

            gasEquity.loc[row, "Year"] = year
            gasEquity.loc[row, "Gas Equity"] = gasEmv[year].sum()

            row += 1

        coalEquity.set_index("Year", inplace=True)
        oilEquity.set_index("Year", inplace=True)
        gasEquity.set_index("Year", inplace=True)

        # total carbon reserves
        coalReserves = pd.DataFrame()
        oilReserves = pd.DataFrame()
        gasReserves = pd.DataFrame()
        totalReserves = pd.DataFrame()

        row = 0
        for year in self.data:
            coalReserves.loc[row, "Year"] = year
            coalReserves.loc[row, "Coal Reserves (tCO2)"] = self.data[year].loc[:, "Coal(tCO2)"].sum()

            oilReserves.loc[row, "Year"] = year
            oilReserves.loc[row, "Oil Reserves (tCO2)"] = self.data[year].loc[:, "Oil(tCO2)"].sum()

            gasReserves.loc[row, "Year"] = year
            gasReserves.loc[row, "Gas Reserves (tCO2)"] = self.data[year].loc[:, "Gas(tCO2)"].sum()

            totalReserves.loc[row, "Year"] = year
            totalReserves.loc[row, "Total Reserves (tCO2)"] = self.data[year].loc[:, ["Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)"]].sum().sum()

            row += 1

        coalReserves.set_index("Year", inplace=True)
        oilReserves.set_index("Year", inplace=True)
        gasReserves.set_index("Year", inplace=True)
        totalReserves.set_index("Year", inplace=True)

        # carbon reserves by fuel type

        aggregateTable = pd.concat([aggregateTable, fossilFuelEquity, totalEquity, coalEquity, oilEquity, gasEquity,
                                    coalReserves, oilReserves, gasReserves, totalReserves]
                                    , axis=1)
        self.aggregateTable = aggregateTable
        return display(aggregateTable)

    def show_top(self, rows=5, sort="EMV"):
        sortMap = {
            "EMV" : "EndingMarketValue",
            "COAL" : "Coal(tCO2)",
            "OIL" : "Oil(tCO2)",
            "GAS" : "Gas(tCO2)"
        }
        columns = ["Company", "Coal(tCO2)", "Oil(tCO2)", "Gas(tCO2)", "EndingMarketValue"]
        for year in self.years:
            print(f"Top {rows} sorted by {sortMap[sort]} for {year}")
            top5 = self.data[year].loc[:, columns].sort_values(by=sortMap[sort], ascending=False).iloc[0:rows, :]
            display(top5)
