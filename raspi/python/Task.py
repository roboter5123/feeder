class Task:
    
    time: str
    dispense_seconds:int
    
    def __init__(self, t:str, ds:int,) -> None:
        

        self.time = t
        self.dispense_seconds = ds
            
    def to_dict(self) -> dict[str, any]:
        
        return self.__dict__
    
    def same_task(task1, task2) -> bool:
        """
        Checks if two tasks are at the same time.
        """
        
        return task1.time == task2.time
    

        
