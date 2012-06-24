# -*- coding: utf-8 -*-

import unittest
from Config import Config

class ConfigTest(unittest.TestCase):
    """
    TestCase for Config.py and some random methods of Config.py
    """

    def setUp(self):
        """
        sets self.config up
        """
        self.config = Config()

    def testRead(self):
        """
        Tests if self.config is filled
        """
        self.assertTrue(self.config is not None)

    def testStaticClass(self):
        """
        tests if self.config.config is the same instance of
        ConfigParser.SafeConfigParser() as Config().config
        """
        self.assertEqual(self.config.config, Config().config)

    def testgetStartEnergy(self):
        """
        Tests if config.__getStartEnergy__ returns the correct StartEnergy
        and the correct Type "int"
        """
        self.assertTrue(self.config.__getStartEnergy__() == 30)
        self.assertEqual(type(self.config.__getStartEnergy__()), int)

    def testgetMovingCosts(self):
        """
        tests if config.__getMovingCosts__() returns the right value
        """
        self.assertEqual(self.config.__getMovingCosts__(7), 2)
        self.assertEqual(type(self.config.__getMovingCosts__(7)), int)
        self.assertTrue(self.config.__getMovingCosts__(6) == 3)

    def testgetMovingCostsException(self):
        """
        tests if an Exception is raised if the value of destination isn't
        in range of our possible destinations
        """
        # not in use, just for example
        # self.assertRaises(Exception, self.config.__getMovingCosts__, 99)

if __name__ == '__main__':
    unittest.main()

