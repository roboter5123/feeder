import unittest
from gpiozero import Motor
from Weekday import Weekday
import json
import time
import schedule
import Task
import os
import lib

class Testlib(unittest.TestCase):
    
#===============================get settings========================================
    
    def test_get_settings(self):
        
        should ={"test":"eins", "test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        file.write(json.dumps(should))
        file.close()
        
        file = open("feeder/raspi/python/settings.json","r")
        should = json.load(file)
        file.close()
        currently = lib.get_settings()
        self.assertEqual(should,currently)
        
    def test_get_settings_file_not_exist(self):
        
        os.remove("feeder/raspi/python/settings.json")
        should = {}
        currently = lib.get_settings()
        self.assertEqual(should,currently)
        
#===============================set settings========================================
        
    def test_set_settings_already_same(self):
        
        should ={"test":"eins", "test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        json.dump(should, file)
        file.close()
        
        lib.set_settings(should)
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
    def test_set_settings_missing(self):
        
        should ={"test":"eins", "test2": 2}
        
        initial_settings = {"test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        json.dump(initial_settings, file)
        file.close()
        
        lib.set_settings(should)
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
    def test_set_setting_different(self):
        
        should = {"test":"eins", "test2": 2}
        
        initial_settings = {"test":1, "test2": "zwei"}
        file = open("feeder/raspi/python/settings.json","w")
        json.dump(initial_settings, file)
        file.close()
        
        lib.set_settings(should)
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
    def test_set_settings_empty_file(self):
        
        should ={"test":"eins", "test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        file.write("")
        file.close()
        
        lib.set_settings(should)
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
    def test_set_settings_file_doesnt_exist(self):
            
        should = {"test":"eins", "test2": 2}
        os.remove("feeder/raspi/python/settings.json")
        
        lib.set_settings(should)
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()     
        
if __name__ == '__main__':
    
    unittest.main()