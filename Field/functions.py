import math
import random


def function(p1, p2):
    if p1[0] == p2[0]:
        return [None, p1[0], p1, p2]
    else:
        # y = mx + b
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p1[1] - p1[0] * m
        return [m, b, p1, p2]


def functions_intersect(f1, f2):
    if f1[0] == f2[0]:  # steepness is the same for both
        return f1[1] == f2[1]  # either b1 = b2 or all of the x's are equal
    else:
        if f1[0] is None:
            p = [f1[1], f2[0] * f1[1] + f2[1]]
        elif f2[0] is None:
            p = [f2[1], f1[0] * f2[1] + f1[1]]
        else:
            x = (f2[1]-f1[1])/(f1[0]-f2[0])
            p = [x, f1[0]*x+f1[1]]
        return _point_between_points(p, f1[2], f1[3]) and _point_between_points(p, f2[2], f2[3])


def _point_between_points(p, p1, p2):
    x = p[0]
    y = p[1]

    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]

    if x2 < x1:  # make sure they are in order
        x1, x2 = x2, x1
    if y2 < y1:  # make sure they are in order
        y1, y2 = y2, y1
    return x1 <= x <= x2 and y1 <= y <= y2


def sqr(v):
    return v * v


def dist(p1, p2):
    return math.sqrt(sqr(p1[0] - p2[0]) + sqr(p1[1] - p2[1]))


def l(v):
    return math.sqrt(sqr(v[0]) + sqr(v[1]))


def multiply(v, m):
    return [m * v[0], m * v[1]]


def norm(v):
    return [v[0] / l(v), v[1] / l(v)]


def set_l(v, m):
    return multiply(norm(v), m)


def a(v1, v2):
    l1 = l(v1)
    l2 = l(v2)
    if l1 == 0 or l2 == 0:
        return 0
    return (v1[0] * v2[0] + v1[1] * v2[1]) / l(v1) / l(v2)


def choose_parents(s):
    p1 = _get_parent(s)
    p2 = _get_parent(s)
    while p1 == p2:
        p2 = _get_parent(s)
    return p1, p2

"""
def _get_parent(s):
    r1 = random.random() - 0.000001
    i = 0
    temp = s[0]
    while r1 > temp:
        i += 1
        temp += s[i]
    print(i, r1, s)
    return i

"""


def _get_parent(s):
    r1 = random.random() - 0.000001
    i = 0
    while r1 > s[i]:
        i += 1
    return i

