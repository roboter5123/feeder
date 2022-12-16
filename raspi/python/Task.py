class Task:
    
    time: str
    dispense_seconds:int
    
    def __init__(self, t:str, ds:int,):
        

        self.time = t
        self.dispense_seconds = ds
            
    def toJSON(self):
        
        return self.__dict__
    

        
