import os
import re


class ValidatorException(Exception):
    pass


class Validator:
    """This guys job is to find the data, validate it, and put it into data structures"""
    def __init__(self, folderNames):
        self.folderNames = folderNames

    def validate(self, dataframefile):
        self.validate_folders()
        self.validate_files()
        dfs = self.validate_data(dataframefile)
        return dfs  # to an Analyst instance

    def validate_folders(self):
        with os.scandir(path='./data') as it: # try ./data
            # store name attribute of each os.DirEntry in iterator provided by scandir()
            currentFolders = [x.name for x in it]
            for folder in self.folderNames:
                if folder not in currentFolders:
                    raise ValidatorException(f"Required folder not present: {folder}")
            it.close()  # Explicitly close the iterator to free memory
        print("Folders Validated")

    def validate_files(self):
        for folder in self.folderNames:
            with os.scandir(path='./data/'+folder) as it:
                currentFiles = [x.name for x in it]  # store name attributes of all files in a folder
                for fileName in currentFiles:
                    if not fileName.endswith(".csv"):  # validate filetype is a csv
                        raise ValidatorException(f"File Type is not csv: {fileName}")
                    if not re.match(r"\d{4}", fileName[:4]):  # validate that first four digits of file name is a year
                        raise ValidatorException(f"File name must start with YYYY: {fileName}")
            it.close()  # Explicity close the iterator to free memory
            print(f"All files validated within {folder}")
        print("Files validated")

    def validate_data(self, dataframefile):
        # dfs is a dictionary of dataframes
        dfs = {}
        for folder in self.folderNames:
            with os.scandir(path='./data/'+folder) as it:
                currentFiles = [x.name for x in it]  # store name attributes of all files in a folders
                for fileName in currentFiles:
                    df = dataframefile.read(os.path.join('./data/', folder, fileName))
                    # check the column titles
                    for col in df.columns:
                        if type(col) is not str:  # ensure column names are string types
                            raise ValidatorException(f"File {fileName} needs to be formatted correctly: {col}")
                    # if column names are valid, then we can safely store the dataframe to our master dictionary
                    dfs[fileName[:4] + folder] = df
                    # i.e. dfs['2016carbon_data']
            it.close()
            print(f"All data validated within {folder}")
        print("Data validated")
        return dfs
