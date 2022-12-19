from shapely.geometry import Point

class Infection_Circle:
    
    def __init__(self, circle, buffer):
        self.circle = circle
        self.buffer = buffer
    
    def grow(self, buffer_factor):
        self.buffer += 1
        self.circle = Point(self.circle.centroid.x, self.circle.centroid.y).buffer(self.buffer * buffer_factor)