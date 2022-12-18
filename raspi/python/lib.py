from gpiozero import Motor
from Weekday import Weekday
import json
import time
from Task import Task
import os
import schedule
import threading

#Type aliases

Json_task = dict[str, any]
Json_day = list[Json_task]
Json_sched = dict[int,Json_day]

motor_forward_pin: int = 18
motor_backward_pin: int = 17
motor: Motor = Motor(motor_forward_pin, motor_backward_pin)
sched: dict[Weekday, list[Task]] = {Weekday.monday:[],Weekday.tuesday:[],Weekday.wednesday:[],Weekday.thursday:[],Weekday.friday:[],Weekday.saturday:[],Weekday.sunday:[]}
settings: dict[str,any] = {"schedule" : sched}
settings_path: str = "raspi/python/settings.json"

def main() -> None:
    """
    Main loop for the device.
    Initiates the device and then checks once every minute for tasks that need doing.
    """
    
    init()
    add_new_task_to_sched(Weekday.friday,"23:25",10)
    add_new_task_to_sched(Weekday.tuesday,"12:10",20)
    
    while True:
        
        task_thread = threading.Thread(target=execute_current_tasks, daemon=True)
        task_thread.start()
        time.sleep(60)
    
def execute_current_tasks():
    
    print("checking for tasks that need running")
    schedule.run_pending()
    print("Current task done")
    
def init() -> None:
    """
    Initilizes the device by loading settings from the settings.json
    and settign up the schedule.
    """
    
    print("Initializing")
    load_settings()
    init_schedule() 
    print("Done initializing")

def init_schedule() -> None:
    """
    Sets up the initial schedule with tasks from the settings.
    """
    
    global sched
    
    #This goes through all days and executes schedule.every().""insert day"".at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    for day in sched:
        
        for task in sched.get(day):
        
            getattr(schedule.every(), day.name).at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    
def put_new_task_on_schedule(day: Weekday, task: Task) -> None:
    """
    Puts a new task on the current schedule.
    """

    #Equivilant to schedule.every()."insert day"..at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    dispense_seconds: int = task.dispense_seconds
    time: str = task.time
    day_name: str = day.name
    getattr(schedule.every(), day_name).at(time).do(dispense,dispense_seconds)
         
def add_new_task_to_sched(weekday: Weekday, time : str, dispense_seconds: int) -> None:
    """
    Creates a new Task and adds it to the settings and current schdule
    TODO: Refactor loop into it's own function for code prettiness.
    """
    
    global settings
    global sched
    
    task: Task = Task(time, dispense_seconds)
    
    if weekday == weekday.everyday:
        
        for day in sched:
            
            add_new_task_to_day(task, sched.get(day))
        
    else:
        
        day = sched.get(weekday)
        add_new_task_to_day(task, day)
        
    set_settings()
    put_new_task_on_schedule(weekday, task)

def add_new_task_to_day(task: Task, day: list[Task]) -> None:
    
    was_added: bool = False
    
    for saved_task in day:
        
        if saved_task.same_task(task):
            
            saved_task.dispense_seconds = task.dispense_seconds
            was_added = True
            break
    
    if not was_added:
        
        day.append(task)

def load_settings() -> None:
    """
    Loads the settings from settings.json and saves it into the global settings variable.
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

def objectify_settings(settings_json: dict[str,any]) -> dict[str, any]:
    """
    Turns a settings json into a dictionary
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global settings
    
    settings ={}
    settings["schedule"] = objectify_schedule(settings_json.get("schedule"))
    return settings

def objectify_schedule(schedule_json: Json_sched) -> dict[Weekday, list[Task]]: 
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
    
def dictify_settings() -> dict[str, any]:
    """
    Turns settings dictionary into a JSON
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    dictified_settings: dict[str, dict[int, list[dict[str,any]]]] = {}
    
    dictified_settings["schedule"] = dictify_schedule()
    
    return dictified_settings
    
def dictify_schedule() -> Json_sched:
    """
    Turns schedule dictionary into a JSON compatible dict.
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global sched
    
    dictified_schedule: dict[int, list[dict[str,any]]] = {}
    
    for day, tasks in sched.items():
        
        dictified_day: list[dict[str,any]] = []
        
        for task in tasks:
            
            dictified_day.append(task.to_dict())
            
        dictified_schedule[day.value] = dictified_day
        
    return dictified_schedule

def set_settings() -> None:
    """
    Sets the settings in settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    
    global settings
    
    if os.path.exists(settings_path):
        
        settings_file = open(settings_path,"r")
        settings_file_string: str = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open(settings_path,"x")
        _.close()
        settings_file_string: str = ""
    
    if(settings_file_string == ""):
        
        settings_file = open(settings_path,"w")
        json.dump(dictify_settings(), settings_file)
        settings_file.close()
        return

    settings_json: dict[str, any] = json.loads(settings_file_string)
    settings_json.update(dictify_settings())
    settings_file = open(settings_path,"w")
    json.dump(settings_json, settings_file)

def dispense(dispense_seconds: int) -> None:
    """
    Turns the dispensing motor.
    """

    motor.forward()
    print(f"turning for {dispense_seconds} seconds")
    time.sleep(dispense_seconds)
    motor.stop()
    print("Stopped turning")