# Created By: Virgil Dupras
# Created On: 2011-08-05
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __iter__(self):
        yield self.x
        yield self.y
    

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.w
        yield self.h
    
    @classmethod
    def from_corners(cls, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2
        return cls(min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2))
    
    def center(self):
        return Point(self.x + self.w/2, self.y + self.h/2)
    
    def corners(self):
        return Point(self.x, self.y), Point(self.x+self.w, self.y+self.h)
    
    def intersects(self, other):
        r1pt1, r1pt2 = self.corners()
        r2pt1, r2pt2 = other.corners()
        if r1pt1.x < r2pt1.x:
            xinter = r1pt2.x >= r2pt1.x
        else:
            xinter = r2pt2.x >= r1pt1.x
        if not xinter:
            return False
        if r1pt1.y < r2pt1.y:
            yinter = r1pt2.y >= r2pt1.y
        else:
            yinter = r2pt2.y >= r1pt1.y
        return yinter
    
