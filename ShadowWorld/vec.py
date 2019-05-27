import math


def add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])


def sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])


def mag(v):
    return math.sqrt((v[0] ** 2) + (v[1] ** 2))


def scale(v, s):
    return (v[0] * s, v[1] * s)


def limit(v, lim):
    m = mag(v)
    if m > lim:
        return scale(unit(v), lim)
    return v


def unit(v):
    m = mag(v)
    if m == 0:
        return 0
    return v[0] / m, v[1] / m


if __name__ == '__main__':
    v1 = (1, 0)
    v2 = (2, 1)
    assert add(v1, v2) == (3, 1)
    assert sub(v1, v2) == (-1, -1)
    assert mag(v1) == 1
    assert mag(unit(v1)) == 1

    print(unit(v1), unit(v2))
