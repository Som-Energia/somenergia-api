from __future__ import division
from math import log10, ceil, floor

class LinearScale(object):

    def __init__(self, lower=0, higher=100):
        self.low = lower
        self.high = higher

    def __call__(self, val):
        if self.low == self.high:
            return 1
        return (val - self.low) / (self.high - self.low)

    def inverse(self, val):
        return self.low + val * (self.high - self.low)

    def nice(self):
        niceHigh = 10 ** ceil(log10(self.high))
        if niceHigh / 5 > self.high:
            self.high = int(niceHigh / 5)
        elif niceHigh / 2 > self.high:
            self.high = int(niceHigh / 2)
        else:
            self.high = int(niceHigh)

        if self.low != 0:
            niceLow = int(10 ** floor(log10(self.low)))
            if niceLow * 5 < self.low:
                self.low = niceLow * 5
            elif niceLow * 2 < self.low:
                self.low = niceLow * 2
            else:
                self.low = niceLow

    def ticks(self, count=4):
        ticks = []
        for step in range(count + 1):
            ticks.append(self.low + int((self.high-self.low) * (step * 1/count)))
        return ticks


class LogScale(object):

    def __init__(self, higher, lower=1):
        if higher < lower:
            raise ValueError("Lower value is greater than higher value")
        if lower <= 0:
            raise ValueError("Log not defined for values <= 0")
        self.low = lower
        self.high = higher

    def __call__(self, val):
        if val <= 0:
            return 0

        return log10(val / self.low) / log10(self.high / self.low)

    def inverse(self, val):
        return self.low * (self.high /self.low) ** val
