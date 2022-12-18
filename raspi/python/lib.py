from gpiozero import Motor
from Weekday import Weekday
import json
import time
from Task import Task
import os
import copy
import schedule

motor_forward_pin = 18
motor_backward_pin = 17
motor = Motor(motor_forward_pin, motor_backward_pin)
sched = {Weekday.monday:[],Weekday.tuesday:[],Weekday.wednesday:[],Weekday.thursday:[],Weekday.friday:[],Weekday.saturday:[],Weekday.sunday:[]}
settings = {"schedule" : sched}
settings_path = "raspi/python/settings.json"

def main():
    
    """
    Main loop for the device.
    Initiates the device and then checks once every minute for tasks that need doing.
    """
    
    print("now in main")
    init()
    print("Done initializing")
    add_new_task(Weekday.friday,"23:25",10)
    add_new_task(Weekday.tuesday,"12:10",20)
    
    while True:
        
        print("checking for tasks that need running")
        schedule.run_pending()
        print("Current task done")
        time.sleep(60)
    
def init():
    """
    Initilizes the device by loading settings from the settings.json
    and settign up the schedule.
    """
    
    get_settings()
    init_schedule() 

def init_schedule():
    """
    Sets up the initial schedule with tasks from the settings.
    TODO: Refactor in a way that the day in the schedule function can be easily exchanged. So that i don't need 7 loops.
    https://github.com/dbader/schedule/issues/496 This issue might fix that.
    """
    
    #This goes through all days and executes schedule.every().""insert day"".at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    print(schedule.get_jobs())
    
    for day in sched:
        
        for task in sched.get(day):
        
            getattr(schedule.every(), day.name).at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    print(schedule.get_jobs())
    
def put_new_task_on_schedule(weekday: Weekday, task: Task):
    """
    Puts a new task on the current schedule.
    TODO: Refactor in a way that the day in the schedule function can be easily exchanged. So that i don't need 8 ifs.
    https://github.com/dbader/schedule/issues/496 This issue might fix that.
    """
    
    
    
    
    if (weekday == 0):
        
        schedule.every().monday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    
    elif(weekday == 1):
        
        schedule.every().tuesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    elif(weekday == 2):
        
        schedule.every().wednesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)         
        
    elif(weekday == 3):
        
        schedule.every().thursday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 4):
        
        schedule.every().friday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 5):
        
        schedule.every().saturday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 6):
        
        schedule.every().sunday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 7):
        
        schedule.every().day.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
         
def add_new_task(weekday: Weekday, time : str, dispense_seconds: int):
    """
    Creates a new Task and adds it to the settings and current schdule
    TODO: Refactor loop into it's own function for code prettiness.
    """
    
    global settings
    global sched
    
    task = Task(time, dispense_seconds)
    
    if weekday == weekday.everyday:
        
        for day in sched:
            
            was_added = False
    
            for saved_task in day:
        
                if same_task(saved_task, task):
            
                    saved_task.dispense_seconds = task.dispense_seconds
                    was_added = True
                    break
    
            if not was_added:
        
                day.append(task)
        
    else:
        
        day = sched.get(weekday)
        was_added = False
    
        for saved_task in day:
        
            if same_task(saved_task, task):
            
                saved_task.dispense_seconds = task.dispense_seconds
                was_added = True
                break
    
        if not was_added:
        
            day.append(task)
        
    set_settings()
    put_new_task_on_schedule(weekday, task)

def get_settings():
    """
    Gets the settings from settings.json and saves it into the global settings variable.
    """
    
    global settings
    
    if os.path.exists(settings_path):
        
        json_settings = open(settings_path, "r")
        
        if (os.path.getsize(settings_path) <= 0):
            
            return
        
        settings = objectify_settings(json.load(json_settings))
        json_settings.close()   
    
    else:
        
        json_settings = open(settings_path, "x")
        json_settings.close()

def objectify_settings(settings_json):
    """
    Turns a settings json into a dictionary
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global settings
    
    settings ={}
    settings["schedule"] = objectify_schedule(settings_json.get("schedule"))
    return settings

def objectify_schedule(schedule_json): 
    """
    Turns a schedule json into a dictionary
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global sched
    
    for day in schedule_json:

        dict_day = []
        
        for task in schedule_json.get(day):
            
            dict_day.append(Task(task.get("time"), task.get("dispense_seconds")))
            
        sched.update({Weekday(int(day)):dict_day}) 
        
    return sched
    
def dictify_settings() -> dict:
    """
    Turns settings dictionary into a JSON
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    dictified_settings = {}
    
    dictified_settings["schedule"] = dictify_schedule()
    
    return dictified_settings
    
def dictify_schedule() -> dict:
    """
    Turns schedule dictionary into a JSON compatible dict.
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global sched
    
    dictified_schedule = {}
    
    for day, tasks in sched.items():
        
        dictified_day = []
        
        for task in tasks:
            
            dictified_day.append(task.to_dict())
            
        dictified_schedule[day.value] = dictified_day
        
    print(dictified_schedule)
        
    return dictified_schedule

def set_settings():
    """
    Sets the settings in settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    
    global settings
    
    if os.path.exists(settings_path):
        
        settings_file = open(settings_path,"r")
        settings_file_string = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open(settings_path,"x")
        _.close()
        settings_file_string = ""
    
    if(settings_file_string == ""):
        
        settings_file = open(settings_path,"w")
        json.dump(dictify_settings(), settings_file)
        settings_file.close()
        return

    settings_json = json.loads(settings_file_string)
    settings_json.update(dictify_settings())
    settings_file = open(settings_path,"w")
    json.dump(settings_json, settings_file)
    return

def dispense(dispense_seconds: int) -> None:
    """
    Turns the dispensing motor.
    """

    motor.forward()
    print(f"turning for {dispense_seconds} seconds")
    time.sleep(dispense_seconds)
    motor.stop()
    print("Stopped turning")
    return 

def same_task(task1: Task, task2: Task) -> bool:
    """
    Checks if two tasks are at the same time.
    TODO: Make this a class Metod in tasks
    """
    return task1.time == task2.time