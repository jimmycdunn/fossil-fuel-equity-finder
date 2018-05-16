from io import StringIO
import time
from unittest import (
    TestCase,
    mock,
)
import os

import pandas as pd

from ffequity.utils.dataframefile import (
    DataFrameFile,
    DataFrameFileException,
)



class TestRead(TestCase):
    '''
    Test the read() function from DataFrameFile
    '''

    def test_read_csv_to_dataframe(self):
        '''
        Test that the read() function successfully converts a csv to a pd.DataFrame
        '''
        textStream = StringIO("Col1,Col2,Col3\n1,2,3")
        dff = DataFrameFile()
        results = dff.read(textStream)
        self.assertIsInstance(results, pd.DataFrame)
        self.assertIsInstance(dff.data, pd.DataFrame)

        assert results.loc[0, "Col1"] == 1
        assert results.loc[0, "Col3"] == 3

class TestWrite(TestCase):
    """
    Test the write() function from DataFrameFile
    """

    @classmethod
    def setUpClass(cls):
        '''
        Sets up a temporary directory to store outputs of write() function
        '''
        cls.tmp_test_dir = "tests/test_tmp_" + str(time.time())
        os.mkdir(cls.tmp_test_dir)

    @classmethod
    def tearDownClass(cls):
        '''
        Removes temporary directory storing outputs of write() function
        '''
        os.rmdir(cls.tmp_test_dir)

    def test_empty_data_raises_exception(self):
        '''
        Tests that write raises DataFrameFileException with an empty data frame
        '''
        dff = DataFrameFile()
        with self.assertRaises(DataFrameFileException):
            dff.write('fakeFileName')

    @mock.patch('transitionrisk.utils.dataframefile.DataFrameFile.get_file_prefix',
                return_value='file_prefix')
    def test_writes_to_csv(self, mock1):
        '''
        Tests that write() successfully outputs a csv file with data in it
        '''
        textStream = StringIO("Col1,Col2,Col3\n1,2,3")
        dff = DataFrameFile()
        results = dff.read(textStream)
        fileName = "testFilename"
        dff.write(fileName, path=self.tmp_test_dir)

        mock1.assert_called_once()
        fullFilename = self.tmp_test_dir+"/"+"file_prefix"+fileName+".csv"
        with open(fullFilename, "r") as fd:
            assert fd.readline() == ',Col1,Col2,Col3\n'
            assert fd.readline() == '0,1,2,3\n'

        os.remove(fullFilename)
