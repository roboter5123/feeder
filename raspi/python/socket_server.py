import lib
import json
import socket
from Weekday import Weekday
import time

login_url:str = "192.168.0.2"
server: socket
server_functions = {}
port = 8058

def start_sockets():
    """
    Main method of the socket connection to the main sever.
    Establishes connection and listens for commands. Then executes them.
    """
    global server_functions
    
    while True:
        
        server_functions = {"get" : get_settings, "set" : set_settings, "dispense" : dispense_from_connection, "add": add_task_from_connection}

        try:
            
            start_outgoing_socket()
            listen_for_instructions()

        except Exception as e:
            
            print(e)
            lib.log(e)
            time.sleep(60)
            print("Retrying connection")
            lib.log("Retrying connection")
            continue
        
def start_outgoing_socket():
    """
    Creates the socket and connects to the main server.
    """
    
    global server
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connecting")
    server.connect((login_url, port))
    print("connected")
    print("Successfully connected")
    lib.log("Successfully connected to login server")
    return
                
def listen_for_instructions():
    """
    Listens for instructions and executes them with their arguments.
    """
    global server
    
    while True:
        
        response = server.recv(1024).decode()
        response = response[0:(len(response)-2)]
        response = response.split("#")
        command = response[0]
        del response[0]
        args = response
        
        print("Command: " + command)
        print("Args: " + str(args))
        
        try:
            
            response = server_functions.get(command)(args)
            response += "\n"

        except Exception as e:
            
            response = str(e) + "\n"
        
        server.sendall(response.encode())

def set_settings(args: list) -> bool:
    """
    Sets settings from arguments received over socket connection.
    Arguments should be a a list with only 1 settings dictionary in it.
    """
    global settings
    global sched
    
    new_settings = json.loads(args[0])
    print(new_settings)
    new_settings = lib.objectify_settings(new_settings)
    settings = new_settings
    sched = settings.get("schedule")
    lib.save_settings()
    lib.load_settings()
    print(settings)
    return str(True)

def get_settings(args: list) -> dict:
    """
    Gets the current settigs and returns them to be sent back to the server.
    """
    return json.dumps(lib.dictify_settings())

def add_task_from_connection(args: list) -> bool:
    """
    Adds a task to the schedule from socket connection.
    Args should be a list with: 
    int representing a weekday on index 0
    str representing time of day on index 1
    int representing seconds of dispensing on index 2
    """
    
    day = Weekday(int(args[0]))
    time = args[1]
    dispense_seconds = int(args[2])
    lib.add_new_task_to_sched(day,time,dispense_seconds)
    return str(True)

def dispense_from_connection(args: list) -> bool:
    """
    Dispensese from socket connection
    args should be a list with:
    int representing seconds of dispensing on index 0
    """
    lib.dispense(int(args[0]))
    return str(True)
        
