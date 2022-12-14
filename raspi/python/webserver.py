from flask import Flask
import lib

app = Flask(__name__)


@app.route('/')
def get_settings():
    
    return lib.get_settings()


@app.route("/<int:seconds>")
def dispense_seconds(seconds):
    
    lib.dispense(seconds)
    return 

if __name__ == '__main__':
   app.run()