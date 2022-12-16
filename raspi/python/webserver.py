from flask import Flask, request, render_template
import lib
import threading
from Weekday import Weekday
from Task import Task
app = Flask(__name__, template_folder='templates', static_folder='staticFiles')

@app.route('/')
def get_settings():
    
    return render_template("index.html")

@app.route('/settings')
def send_settings():
    
    return lib.stringify_settings()

@app.route('/add-task')
def add_task():
    
    weekday = int(request.args.get("day"))
    time = request.args.get("time")
    dispense_seconds = int(request.args.get("amount"))
    lib.add_new_task(weekday, time, dispense_seconds)
    return "Done"

@app.route("/dispense")
def dispense_seconds():
    
    lib.dispense(int(request.args.get("amount")))
    return {"dispensed": True}

if __name__ == '__main__':
    
   mainThread = threading.Thread(target=lib.main, daemon=True)
    
   mainThread.start()
   app.run()