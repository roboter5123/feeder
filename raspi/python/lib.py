from gpiozero import Motor
import json
import time

motor_forward_pin = 17
motor_backward_pin = 18

motor = Motor(motor_forward_pin, motor_backward_pin)

def get_settings(_ = None):
    
    json_settings = open("raspi/python/settings.json")
    settings = json_settings.read()
    json_settings.close()
    
    return settings

def set_settings(settings):
    
    settings = json.loads(settings)
    settings_file = open("raspi/python/settings.json","r")
    settings_file_string = settings_file.read()
    
    if(settings_file_string == ""):
        
        settings_file.close()
        settings_file = open("raspi/python/settings.json","w")
        settings_file.write(json.dumps(settings))
        settings_file.close()
        return
    
    json_settings = json.loads(settings_file_string)
    settings_file.close()
    
    for setting in settings:
        
        if not json_settings.get(setting, False):
            
            json_settings[setting] = settings[setting]
            
    settings_file = open("raspi/python/settings.json","w")
    settings_file.write(json.dumps(json_settings))
    settings_file.close()
        
    return

def dispense(seconds):

    motor.forward()
    print(f"turning for {seconds} seconds")
    time.sleep(seconds)
    motor.stop()
    print("Stopped turning")
    return 

