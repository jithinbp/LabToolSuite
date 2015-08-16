#!/usr/bin/python
import unittest

class TestUnit(unittest.TestCase):
 
    def setUp(self):
        import Labtools
        print 'import successful'
        pass
 
    def test_voltage_read(self):
    	import Labtools.interface as i
    	I=i.Interface()
        print self.I.get_average_voltage('CH1')
 
 
if __name__ == '__main__':
    unittest.main()
