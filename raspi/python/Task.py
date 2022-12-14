class Task:
    
    time: str
    dispense_seconds:int
    
    def __init__(self, t, ds):
        
        self.time = t
        self.dispense_seconds = ds
        
    def same_task(self, compare_to):
        
        return compare_to.time == self.time
        

        
