# -*- coding: utf-8 -*-
"""
The libmseed test suite.
"""

from obspy.mseed import libmseed
import inspect
import os
import unittest


class LibMSEEDTestCase(unittest.TestCase):
    """
    Test cases for libmseed.
    """
    def setUp(self):
        # Directory where the test files are located
        path = os.path.dirname(inspect.getsourcefile(self.__class__))
        self.path = os.path.join(path, 'data')
    
    def tearDown(self):
        pass

    def test_readTraces(self):
        """
        Compares waveform data read by libmseed with an ASCII dump.
        
        Checks the first 13 datasamples when reading BW.BGLD..EHE.D.2008.001
        using traces. The values in BW.BGLD..EHE.D.2008.001_first20lines.ASCII
        are assumed to be correct. The file was created using Pitsa.
        Only checks relative values.
        """
        mseed_file = os.path.join(self.path, 'BW.BGLD..EHE.D.2008.001')
        ascii_file = os.path.join(self.path, 
                                  'BW.BGLD..EHE.D.2008.001_first20lines.ASCII')
        mseed=libmseed()
        f=open(ascii_file,'r')
        datalist=f.readlines()
        datalist[0:7]=[]
        for i in range(len(datalist)):
            datalist[i]=int(datalist[i])
        header, data, numtraces=mseed.read_ms_using_traces(mseed_file)
        self.assertEqual('BGLD', header['station'])
        self.assertEqual('EHE', header['channel'])
        self.assertEqual(200, header['samprate'])
        self.assertEqual(1199145599915000, header['starttime'])
        self.assertEqual(numtraces, 1)
        for i in range(len(datalist)-1):
            self.assertEqual(datalist[i]-datalist[i+1], data[i]-data[i+1])
    
    def test_readAnWriteTraces(self):
        """
        Writes, reads and compares files created via libmseed.
        
        This uses all possible encodings, record lengths and the byte order 
        options. A reencoded SEED file should still have the same values 
        regardless of write options.
        """
        # define test ranges
        record_length_values = [2**i for i in range(8, 21)]
        encoding_values = [1, 3, 10, 11]
        byteorder_values = [0, 1]
        
        mseed=libmseed() 
        mseed_file = os.path.join(self.path, 'test.mseed')
        header, data, numtraces=mseed.read_ms_using_traces(mseed_file)
        # Deletes the dataquality indicators
        testheader=header.copy()
        del testheader['dataquality']
        # loops over all combinations of test values
        for reclen in record_length_values:
            for byteorder in byteorder_values:
                for encoding in encoding_values:
                    filename = 'temp.%s.%s.%s.mseed' % (reclen, byteorder, 
                                                        encoding)
                    temp_file = os.path.join(self.path, filename)
                    mseed.write_ms(header, data, temp_file,
                                   numtraces, encoding=encoding, 
                                   byteorder=byteorder, reclen=reclen)
                    result = mseed.read_ms_using_traces(temp_file)
                    newheader, newdata, newnumtraces = result
                    del newheader['dataquality']
                    self.assertEqual(testheader, newheader)
                    self.assertEqual(data, newdata)
                    self.assertEqual(numtraces, newnumtraces)
                    os.remove(temp_file)
    
    def test_findGaps(self):
        """
        Compares calculated gaps in a MiniSEED file with known values.
        
        The values are compared with the printgaplist method of the libmseed 
        library and visually compared with the SeisGram2K viewer.
        """
        mseed = libmseed()
        gapslist = mseed.findgaps(os.path.join(self.path,'gaps.mseed'))
        self.assertEqual(gapslist[0][0], long(1199145601970000 ))
        self.assertEqual(gapslist[1][0], long(1199145608150000))
        self.assertEqual(gapslist[2][0], long(1199145614330000))
        self.assertEqual(gapslist[0][1], 2065000)
        self.assertEqual(gapslist[1][1], 2065000)
        self.assertEqual(gapslist[2][1], 4125000)


def suite():
    return unittest.makeSuite(LibMSEEDTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
