import unittest
import json
import lib

class Testlib(unittest.TestCase):
    
    def test_get_settings(self):
        
        should = open("raspi/python/settings.json").read()
        currently = lib.get_settings()
        self.assertEqual(should,currently)
        
        
    def test_set_settings(self):
        
        should = open("raspi/python/settings.json","w").write("")
        test_settings = json.dumps({"test":"eins", "test2": 2})
        lib.set_settings(test_settings)
        self.assertEqual(open("raspi/python/settings.json").read(),test_settings)
        
    
        
if __name__ == '__main__':
    
    unittest.main()