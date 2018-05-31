# mimic ffequity.py in process but do it for carbon allocation
from utils.dataframefile import DataFrameFile
from processors.validator import Validator
from processors.analyst import Analyst

folderNames = ['assessment', 'financial_data']

def main():
    # create object instance of DataFrameFile
    # have it read in the assessment data files and the financial data
    # run the fair share allocation for each year
    # write the final data to .csv in benchmark
    # create object instance of dataframefile and validator
    dataframefile = DataFrameFile()
    # read in the assessment datafiles and the financial datafiles
    validator = Validator(folderNames)

    # tell validator to use dataframefile to validate all data and read into dfs
    dfs = validator.validate(dataframefile)
    # create analyst object and pass in dfs to be written out to master spreadsheets
    analyst = Analyst(dfs)
    analyst.analyze_carbon(dataframefile)
    print("Congratulations, the tool has completed the analysis!")

if __name__ == "__main__":
    main()
