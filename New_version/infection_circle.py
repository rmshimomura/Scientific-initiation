from shapely.geometry import Point

class Infection_Circle:
    
    def __init__(self, circle, buffer):
        self.circle = circle
        self.buffer = buffer
    
    def grow(self, buffer_factor, threshold):

        # Fazer uma funcao decrescente aqui
        # De duas em duas semanas diminuir um valor calculado previamente?
        # Inversamente proporcial a distancia

        if self.buffer > threshold:
            self.buffer += 0.5
        else:
            self.buffer += 1
        self.circle = Point(self.circle.centroid.x, self.circle.centroid.y).buffer(self.buffer * buffer_factor)