class Burr:

    def __init__(self, geometry, buffer, discovery_day):
        self.geometry = geometry
        self.buffer = buffer
        self.life_span = 1
        self.discovery_day = discovery_day
    def grow(self, growth_function, base):

        if self.life_span < 105:
            self.life_span += 1
            self.buffer = growth_function(self.life_span, base)
            self.geometry = self.geometry.buffer(self.buffer)