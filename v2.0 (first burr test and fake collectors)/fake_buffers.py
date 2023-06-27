from shapely.geometry import LineString

class Fake_Buffer():

    def __init__(self, line: LineString, buffer: float):
        self.line = line
        self.buffer = buffer
        self.life_span = 1


    def grow(self, growth_function, base):

        if self.life_span < 105:
            self.life_span += 1
            self.buffer = growth_function(self.life_span, base)
            
        else:
            return
        
class Fake_Buffer_List():

    def __init__(self, collector_id) -> None:
        self.buffer_list = []
        self.collector_id = collector_id
    
