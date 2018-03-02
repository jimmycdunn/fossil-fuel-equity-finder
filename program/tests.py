import unittest
import numpy as np
import pandas as pd
from datetime import date
from utils.dataframefile import DataFrameFile
from processors.validator import Validator
from processors.analyst import Analyst

# my test fixture will make dummy data for equity, carbon, finance

# make a test for each class
# COVERAGE
# DataFrameFile: check
# Validator: check
# Analyst:
# assess.py:

# TestCase
class TestRead(unittest.TestCase):
    '''
    Test the read() function from DataFrameFile
    '''

    # instantiate fakeData from unittest.mock

    def setUp(self):
        self.classInstance = DataFrameFile()

    def test_read_csv_to_dataframe(self):
        '''
        Test that the read() function successfully converts a csv to a pd.DataFrame
        '''
        dummyFileName = fakeData.name
        result = classInstance.read(dummyFileName)
        self.assertIs(result, pd.DataFrame()) # other better one might be assertIsInstance()

class TestWrite(unittest.TestCase):
    '''
    Test the write() function from DataFrameFile
    '''

    # instantiate fakeData from unittest.mock

    def setUp(self):
        self.classInstance = DataFrameFile()

    def test_write_dataframe_to_csv(self):
        '''
        Test that the write() function successfully converts a pd.DataFrame to a csv in the correct folder
        '''
        dummyFileName = fakeData.name
        classInstance.data = classInstance.read(dummyFileName)
        dummyWriteLocation = fakeLocation
        with self.assertRaises(DataFrameFileException):
            classInstance.write(dummyWriteLocation)

class TestGetFilePrefix(unittest.TestCase):
    '''
    Test the get_file_prefix() function from DataFrameFile
    '''

    def setUp(self):
        self.classInstance = DataFrameFile()

    def test_get_file_prefix(self):
        '''
        Test that the get_file_prefix() function successfully returns current date
        '''
        result = get_file_prefx()
        self.assertEqual(result, ''.join([str(i) for i in today.timetuple()[0:3]]))

class TestValidate(unittest.TestCase):
    '''
    Test the validate() function from Validator
    '''

    def setUp(self):
        self.classInstance = Validator()

    def test_validate(self):
        '''
        Test that the validate() function successfully validates and loads csv data into dataframes
        '''
        # do the stuff
        self.assertIs(result, dict)

class TestValidateFolders(unittest.TestCase):
    '''
    Test the validate_folders() function from Validator
    '''

    def setUp(self):
        folderNames = ['equity_data', 'carbon_data', 'financial_data']
        self.classInstance = Validator(folderNames)

    def test_validate_folders(self):
        '''
        Test that the validate_folders() function successfully validates folder names in the CWD
        '''
        with self.assertRaises(ValidatorException):
            classInstance.validate_folders() # will this catch the raise or should i put something WRONG in here to trigger the raise?

class TestValidateFiles(unittest.TestCase):
    '''
    Test the validate_files() function from Validator
    '''

    def setUp(self):
        folderNames = ['equity_data', 'carbon_data', 'financial_data']
        self.classInstance = Validator(folderNames)

    def test_validate_files(self):
        '''
        Test that the validate_files() function successfully validates file names
        '''
        with self.assertRaises(ValidatorException):
            classInstance.validate_files()

class TestValidateData(unittest.TestCase):
    '''
    Test the validate_data() function from Validator
    '''

    def setUp(self):
        folderNames = ['equity_data', 'carbon_data', 'financial_data']
        self.classInstance = Validator(folderNames)

    def test_validate_data(self):
        '''
        Test that the validate_data() function successfully validates data
        '''
        dataframefile = DataFrameFile()
        with self.assertRaises(ValidatorException):
            classInstance.validate_data(dataframefile)

class TestAnalyze(unittest.TestCase):
    '''
    Test the analyze() function from Analyst
    '''

    def setUp(self):
        fakeDataFrames = {} # populate dict with keys as years and values as DataFrame objects
        self.classInstance = Analyst(fakeDataFrames)

    def test_analyze(self):
        '''
        Test that the analyze() function sucessfully manipulates the data and writes its output to .csv
        '''
        dataframefile = DataFrameFile()
        result = classInstance.analyze()
        self.assertEqual(result, answer) #answer is a dictionary of dataframes that are correctly manipulated

class TestMatch(unittest.TestCase):
    '''
    Test the match() function from Analyst
    '''

    def setUp(self):
        fakeDataFrames = {} # populate dict with keys as years and values as DataFrame objects
        self.classInstance = Analyst(fakeDataFrames)

    def test_match():
        '''
        Test that the match() function successfully matches carbon companies to equity company names
        '''
        result = classInstance.match()
        self.assertEqual(result, answer) #answer is a dictionary of dataframes that have been correctly matched

class TestComputeTargetHeld(unittest.TestCase):
    '''
    Test the compute_target_held() function from Analyst
    '''

    def setUp(self):
        fakeDataFrames = {} # populate dict with keys as years and values as DataFrame objects
        fakeMatchedDataFrames = {} # populate dict with keys as years and values
        self.classInstance = Analyst(fakeDataFrames)

    def test_compute_target_held():
        '''
        Test that the compute_target_held() function succesfully computes summary statistics about carbon equity
        '''
        result = classInstance.compute_target_held(fakeMatchedDataFrames)
        self.assertEqual(result, answer) # answer is a dictionary of values that represent the target held percentages by year
