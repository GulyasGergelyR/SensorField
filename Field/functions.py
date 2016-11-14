import math


def function(p1, p2):
    if p1[0] == p2[0]:
        return [None, p1[0]]
    else:
        # y = mx + b
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p1[1] - p1[0] * m
        return [m, b]


def functions_intersect(f1, f2, x1, x2):
    if f1[0] == f2:  # steepness is the same for both
        return f1[1] == f2[1]  # either b1 = b2 or all of the x's are equal
    else:
        if f1[0] is None:
            x = f1[1]
        elif f2[0] is None:
            x = f2[1]
        else:
            x = (f2[1]-f1[1])/(f1[0]-f2[0])
    if x2 < x1:  # make sure they are in order
        x1, x2 = x2, x1
    return x1 < x < x2


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

