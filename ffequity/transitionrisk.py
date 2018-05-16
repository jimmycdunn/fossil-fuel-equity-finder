# Description of program
# free distribution information
# define functions here
# declare folderNames
from utils.dataframefile import DataFrameFile
from processors.validator import Validator
from processors.analyst import Analyst

folderNames = ['equity_data', 'carbon_data', 'financial_data']

def main():
    # create object instance of dataframefile and validator
    dataframefile = DataFrameFile()
    validator = Validator(folderNames)

    # tell validator to use dataframefile to validate all data and read into dfs
    dfs = validator.validate(dataframefile)

    # create analyst object and pass in dfs to be written out to master spreadsheets
    analyst = Analyst(dfs)
    analyst.analyze(dataframefile)
    print("Congratulations, the tool has completed the analysis!")

if __name__ == "__main__":
    main()
