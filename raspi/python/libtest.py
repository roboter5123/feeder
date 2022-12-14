import unittest
import json
import os
import lib

class Testlib(unittest.TestCase):
    
#===============================get settings========================================
    
    def test_get_settings(self):
        file = open("feeder/raspi/python/settings.json","w+")
        should = file.read()
        file.close()
        currently = lib.get_settings()
        self.assertEqual(should,currently)
        
    def test_get_settings_file_not_exist(self):
        
        os.remove("feeder/raspi/python/settings.json")
        should = ""
        currently = lib.get_settings()
        self.assertEqual(should,currently)
        
#===============================set settings========================================
        
    def test_set_settings_already_same(self):
        
        should ={"test":"eins", "test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        file.write(json.dumps(should))
        file.close()
        
        lib.set_settings(json.dumps(should))
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
        
    def test_set_settings_empty_file(self):
        
        should ={"test":"eins", "test2": 2}
        file = open("feeder/raspi/python/settings.json","w")
        file.write("")
        file.close()
        
        lib.set_settings(json.dumps(should))
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
    def test_set_settings_file_doesnt_exist(self):
            
        should ={"test":"eins", "test2": 2}
        os.remove("feeder/raspi/python/settings.json")
        
        lib.set_settings(json.dumps(should))
        
        file = open("feeder/raspi/python/settings.json","r")
        self.assertEqual(file.read(),json.dumps(should))
        file.close()
        
if __name__ == '__main__':
    
    unittest.main()