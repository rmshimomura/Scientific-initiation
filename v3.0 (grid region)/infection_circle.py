from shapely.geometry import Point

class Infection_Circle:
    
    def __init__(self, circle, buffer, discovery_day):
        self.circle = circle
        self.buffer = buffer
        self.life_span = 1
        self.discovery_day = discovery_day
    
    def grow(self, growth_function, base):

        if self.life_span < 105:
            self.life_span += 1
            self.buffer = growth_function(self.life_span, base)
            self.circle = Point(self.circle.centroid.x, self.circle.centroid.y).buffer(self.buffer)
            
        else:
            return