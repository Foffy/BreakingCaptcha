from numpy import array, zeros, argmin, inf
from numpy.linalg import norm
import os


import sys

with open('trash', 'w') as f:
    so, se = sys.stdout, sys.stderr
    sys.stdout = f
    sys.stderr = f
    import librosa
    sys.stdout, sys.stderr = so, se



def dtw(x, y, dist=lambda x, y: norm(x - y, ord=1)):
    """ Computes the DTW of two sequences.
    :param array x: N1*M array
    :param array y: N2*M array
    :param func dist: distance used as cost measure (default L1 norm)
    Returns the minimum distance, the accumulated cost matrix and the wrap path.
    """

    x = array(x)
    if len(x.shape) == 1:
        x = x.reshape(-1, 1)
    y = array(y)
    if len(y.shape) == 1:
        y = y.reshape(-1, 1)

    r, c = len(x), len(y)

    D = zeros((r + 1, c + 1))
    D[0, 1:] = inf
    D[1:, 0] = inf

    for i in range(r):
        for j in range(c):
            D[i+1, j+1] = dist(x[i], y[j])

    for i in range(r):
        for j in range(c):
            D[i+1, j+1] += min(D[i, j], D[i, j+1], D[i+1, j])

    D = D[1:, 1:]

    dist = D[-1, -1] / sum(D.shape)

    return dist, D, _trackeback(D)


def _trackeback(D):
    i, j = array(D.shape) - 1
    p, q = [i], [j]
    while (i > 0 and j > 0):
        tb = argmin((D[i-1, j-1], D[i-1, j], D[i, j-1]))

        if (tb == 0):
            i = i - 1
            j = j - 1
        elif (tb == 1):
            i = i - 1
        elif (tb == 2):
            j = j - 1

        p.insert(0, i)
        q.insert(0, j)

    p.insert(0, 0)
    q.insert(0, 0)
    return (array(p), array(q))


def k_nearest(sound, dir, k=5):
    """ Computes the k nearest digits to the sound.
    MFCC is calculated for the two sounds and passed to dtw() for comparison
    :param string sound: Path to .wav input file
    :param string dir: Path to directory of known sounds   
    """
    y1, sr1 = librosa.load(sound)
    known = librosa.feature.mfcc(y1, sr1)
    dists = []
    for dirName, subdirList, fileList in os.walk(dir):
        for fName in filter(lambda x: x.endswith(".wav"), fileList):
            unknownPath = "{}/{}".format(dirName, fName)
            unknown_y1, unknown_sr1 = librosa.load(unknownPath)
            unknown = librosa.feature.mfcc(unknown_y1, unknown_sr1)
            dist, cost, path = dtw(known.T, unknown.T)
            dists.append((dirName[-1:], dist))

    dists.sort(key=lambda x: x[1])
    return dists[:k]