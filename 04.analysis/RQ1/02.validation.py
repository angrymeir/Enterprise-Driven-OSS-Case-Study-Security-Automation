import pandas as pd
import json
from collections import Counter

with open('../../results/03.tools_usage_detection/all_projects_security.json') as infile:
    all_sec = json.load(infile)

df = pd.read_csv('../../resources/manual_review.tsv', sep='\t')


def aut_det_false_positives_negatives():
    """
    Determine the false positives and false negatives in direct comparison between manual and automatic review.
    """
    ov_f_n = []
    counter = 0
    print("Obvious False positives")
    for row in df.itertuples(index=False):
        project = row[0]
        sec = all_sec[project]
        if row[1] == 0:
            if len(sec) != 0:
                print(sec)
                counter += 1
    print("Total:", counter)
    print("\n--------------------\n")
    print("Obvious False negatives")
    counter = 0
    for row in df.itertuples(index=False):
        project = row[0]
        sec = all_sec[project]
        if row[1] != 0:
            if len(sec) == 0:
                print(project, row[2])
                counter += 1
                ov_f_n.append(row[2])
    print(Counter(ov_f_n))
    print("Total:", counter)
    print("\n--------------------\n")
    print("For Manual Inspection (Gave 3 additional false negatives)")
    counter = 0
    for row in df.itertuples(index=False):
        project = row[0]
        sec = all_sec[project]
        if row[1] != 0:
            if len(sec) != 0:
                print("Man Det.: {}, Auto. Det.: {}".format(row[2], sec))
                counter += 1
    print("Total:", counter)


def main():
    aut_det_false_positives_negatives()


if __name__ == "__main__":
    main()
