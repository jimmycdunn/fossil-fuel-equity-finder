from io import StringIO
import time
from unittest import (
    TestCase,
    mock,
)
import os

import pandas as pd

from ffequity.utils.validator import (
    Validator,
    ValidatorException,
)

class TestValidateFolders(TestCase):
    '''
    Tests the validate_folders() function from Validator
    '''

    @classmethod
    def setUpClass(cls):
        '''
        Sets up a temporary directory to store dummy csv data
        '''
        cls.tmp_test_dir = "tests/test_tmp_" + str(time.time())
        os.mkdir(cls.tmp_test_dir)

    @classmethod
    def tearDownClass(cls):
        '''
        Removes temporary directory to store dummy csv data
        '''
        os.rmdir(cls.tmp_test_dir)

    def test_missing_folder(self):
        '''
        Tests that validate_folders() raises exception if a folder is missing
        '''
        folderNames = ['equity_data', 'carbon_data', 'financial_data']
        validator = Validator(folderNames)
        # create an empty directory for carbon_data only and see if
        # ValidatorException is raised
