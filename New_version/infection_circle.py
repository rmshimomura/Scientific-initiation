from shapely.geometry import Point

class Infection_Circle:
    
    def __init__(self, circle, buffer):
        self.circle = circle
        self.buffer = buffer
    
    def grow(self, buffer_factor, day):

        # if self.buffer > day:
        #     self.buffer += 0.5
        # else:
        #     self.buffer += 1

        self.buffer += 1 - (day // 10.5)/10 # After 105 days or 15 weeks, the growth stops

        self.circle = Point(self.circle.centroid.x, self.circle.centroid.y).buffer(self.buffer * buffer_factor)