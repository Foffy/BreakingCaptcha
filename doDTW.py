import DTW.dtw as dtw
import pickle
from collections import Counter


def run(in_file):
    """ Interface for recognising unknown sounds.
        Any unrecognised sound will be predicted and the corresponding value will be modified
        Will rewrite the input file with modified values
        :param in_file: pickle object with a list of what prior recognision predicts
    """
    with open(in_file, 'rb') as v_file:
        values = pickle.load(v_file)

    for x in range(len(values)):
        if values[x] == None:
            values[x] = get_nearest(x)
        else:
            try:
                val = int(values[x])
            except ValueError:
                values[x] = str(get_nearest(x))

    to_file = []
    for x in values:
        if not x == None:
            to_file.append(x)

    with open(in_file, "wb") as f:
        pickle.dump(to_file, f, protocol=2)

def get_nearest(value):
    print("Getting dtw for: {}".format(value))
    """ Determines the k_nearest in respect to the requested sound.
        Will use the vote() method to determine the best choise
        :param value: List of what prior recognision predicts
        :return int: Predicted value of sound
    """
    k_nearest = dtw.k_nearest("Sounds/{}.wav".format(value), "Sounds/known/", 15)
    k_nearest = [x[0] for x in k_nearest if x[1] < 300]

    if len(k_nearest) > 0:
        return vote(k_nearest)
    return None

def vote(values):
    print("Voting for: {}".format(values))
    """ Votes to find best choise for nearest number of selected sound
        :param values: List of k_nearest distances to the sound
        :return int: Predicted value of sound
    """
    data = Counter(values).most_common(2)
    if not data[0][1] == data[1][1]:
        return data[0][0]
    else:
        return vote(values[:-1])

if __name__ == '__main__':
    """ Simply runs run() if this is run as main
    """
    import argparse

    parser = argparse.ArgumentParser(description="Interface for running DTW module from external script")
    parser.add_argument("-i", "--input", dest="file", default=None, help="File containing recognised values")

    args = parser.parse_args()
    
    if args.file == None:
        print("The DTW interface requires a binary value file")
    else:
        run(args.file)