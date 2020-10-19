import json
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np


def load_project_security():
    """
    Load the mapping of projects to security tools.
    """
    with open('../../results/03.tools_usage_detection/all_projects_security.json', 'r') as infile:
        return json.load(infile)


def load_sec_patterns():
    """
    Load the mapping of security activities to security tools.
    """
    with open('../../resources/security_patterns.json', 'r') as infile:
        return json.load(infile)


def load_timespan():
    """
    Load the mapping of projects to the time they were created and last updated.
    """
    with open('../../results/01.crawling/05.characteristics/project_timespan.json', 'r') as infile:
        return json.load(infile)


project_sec = load_project_security()
security_act = load_sec_patterns()
project_timespan = load_timespan()


def map_sec_act_to_project(sec_projects):
    """
    Map security activities to projects.

    :param sec_projects: dict, mapping of projects to security tools
    :return: dict, mapping of projects to security activities
    """
    mapping = {}

    for project, tools in sec_projects.items():
        proj_act = []
        for tool in tools:
            for sec_act, val in security_act.items():
                if tool in val.keys():
                    proj_act.append(sec_act)
        mapping[project] = proj_act
    return mapping


def map_stars_to_sec(mapping):
    """
    Map projects to stars and security tools.
    
    :param mapping: dict, mapping of projects to security activities
    :return: dict, mapping project to number of security actvities and stars
    """
    star_map = {}
    with open('../../results/01.crawling/05.characteristics/project_stars.json', 'r') as infile:
        stars_count = json.load(infile)

    for project, stars in stars_count.items():
        if project in mapping:
            star_map[project] = (len(mapping[project]), stars)
    return star_map


def visualize_star_sec(mapping):
    """
    Visualize mapping of stars to projects performing security vs. projects not performing security.

    :param mapping: dict, mapping project to number of security activities and stars
    """
    plt.figure()
    zero_act = [val[1] for _, val in mapping.items() if val[0] == 0]
    one_act = [val[1] for _, val in mapping.items() if val[0] > 0]
    print("Quartiles of Stars")
    print("Zero Act:", np.median(zero_act), np.quantile(zero_act, q=0.25), np.quantile(zero_act, q=0.75))
    print("One Act:", np.median(one_act), np.quantile(one_act, q=0.25), np.quantile(zero_act, q=0.75))
    print("------------------------------")

    plt.ylabel('Security Activities')
    labels = ['No Security ({})'.format(len(zero_act)),
              'Security ({})'.format(len(one_act)),
              ]
    plt.xlabel('Stars (log2)')
    acts = [zero_act, one_act]
    plt.boxplot(acts, vert=False, showfliers=False, labels=labels)
    plt.savefig('../../results/visualization/sec_star_mapping.png', format='png', dpi=500, bbox_inches='tight')


def stars():
    mapping = map_sec_act_to_project(project_sec)
    mapping_vis = map_stars_to_sec(mapping)
    visualize_star_sec(mapping_vis)


# Time
def timespan_maintained():
    """
    Visualize the number of years a projects is/has been maintained depending on whether it uses security or not.
    """
    timespan_sec_mapping = defaultdict(list)
    for project, sec in project_sec.items():
        secs = len(sec) > 0
        try:
            timespan_sec_mapping[secs].append(project_timespan[project][1] - project_timespan[project][0])
        except KeyError:
            pass

    plt.figure()
    data = [timespan_sec_mapping[True], timespan_sec_mapping[False]]
    labels = ['Security ({})'.format(len(timespan_sec_mapping[True])),
              'No Security ({})'.format(len(timespan_sec_mapping[False]))]
    plt.boxplot(data, vert=False, showfliers=False, labels=labels)
    print("Quartiles for Years Maintained:")
    print("Maintained Sec:", np.quantile(timespan_sec_mapping[True], q=0.25), np.quantile(timespan_sec_mapping[True], q=0.5), np.quantile(timespan_sec_mapping[True], q=0.75))
    print("Maintained No Sec:", np.quantile(timespan_sec_mapping[False], q=0.25), np.quantile(timespan_sec_mapping[False], q=0.5), np.quantile(timespan_sec_mapping[False], q=0.75))
    print("------------------------------")
    plt.xlabel('Years maintained')
    plt.savefig('../../results/visualization/maintained.png', format='png', dpi=500, bbox_inches='tight')


def timespan_created():
    """
    Visualize the years a projects has been created in depending on whether it uses security or not.
    """
    timespan_sec_mapping = defaultdict(list)
    for project, sec in project_sec.items():
        secs = len(sec) > 0
        try:
            timespan_sec_mapping[secs].append(project_timespan[project][0])
        except KeyError:
            pass

    plt.figure()
    data = [timespan_sec_mapping[True], timespan_sec_mapping[False]]
    labels = ['Security ({})'.format(len(timespan_sec_mapping[True])),
              'No Security ({})'.format(len(timespan_sec_mapping[False]))]
    print("Quartiles for Year created:")
    print("Created Sec:", np.quantile(timespan_sec_mapping[True], q=0.25),
          np.quantile(timespan_sec_mapping[True], q=0.5), np.quantile(timespan_sec_mapping[True], q=0.75))
    print("Created No Sec:", np.quantile(timespan_sec_mapping[False], q=0.25),
          np.quantile(timespan_sec_mapping[False], q=0.5), np.quantile(timespan_sec_mapping[False], q=0.75))
    print("------------------------------")
    plt.boxplot(data, vert=False, showfliers=False, labels=labels)
    plt.xlabel('Created at')
    plt.tight_layout()
    plt.savefig('../../results/visualization/created.png', format='png', dpi=500, bbox_inches='tight')


def timespan_last_updated():
    """
    Visualize the years a projects has been lasted update in depending on whether it uses security or not.
    """
    timespan_sec_mapping = defaultdict(list)
    for project, sec in project_sec.items():
        secs = len(sec) > 0
        try:
            timespan_sec_mapping[secs].append(project_timespan[project][1])
        except KeyError:
            pass

    plt.figure()
    data = [timespan_sec_mapping[True], timespan_sec_mapping[False]]
    labels = ['Security ({})'.format(len(timespan_sec_mapping[True])),
              'No Security ({})'.format(len(timespan_sec_mapping[False]))]
    plt.boxplot(data, vert=False, showfliers=False, labels=labels)
    print("Quartiles for year last updated:")
    print("Updated Sec:", np.quantile(timespan_sec_mapping[True], q=0.25),
          np.quantile(timespan_sec_mapping[True], q=0.5), np.quantile(timespan_sec_mapping[True], q=0.75))
    print("Updated No Sec:", np.quantile(timespan_sec_mapping[False], q=0.25),
          np.quantile(timespan_sec_mapping[False], q=0.5), np.quantile(timespan_sec_mapping[False], q=0.75))
    print("Projects updated in Year (with sec):", Counter(timespan_sec_mapping[True]))
    print("Projects updated in Year (without sec):", Counter(timespan_sec_mapping[False]))
    print("------------------------------")
    plt.xlabel('Last update')
    plt.savefig('../../results/visualization/last_updated.png', format='png', dpi=500, bbox_inches='tight')


def time():
    timespan_maintained()
    timespan_created()
    timespan_last_updated()


def main():
    stars()
    time()


if __name__ == "__main__":
    main()
