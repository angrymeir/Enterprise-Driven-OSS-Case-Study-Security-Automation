import json
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np


def load_project_security():
    """
    Load the mapping of projects to security tools.
    """
    with open('../../results/03.tools_usage_detection/all_projects_security.json') as infile:
        return json.load(infile)


def load_sec_patterns():
    """
    Load the mapping of security activities to security tools.
    """
    with open('../../resources/security_patterns.json', 'r') as infile:
        return json.load(infile)


project_sec = load_project_security()
security_act = load_sec_patterns()


def visualize_tools(sec_projects):
    """
    Determine the number of projects that used a certain tool for all tools.
    """
    tools = defaultdict(int)
    for _, val in sec_projects.items():
        for tool in val:
            tools[tool] += 1

    tools = {key: value for key, value in sorted(tools.items(), key=lambda item: item[1], reverse=True)}

    print("Security tools used along with the number of projects using them:")
    for tool, count in tools.items():
        print(tool, count)

    plt.bar(range(len(tools)), list(tools.values()), align='center')
    plt.ylabel('Projects')
    plt.xticks(range(len(tools)), list(tools.keys()), rotation=90, fontsize=5)
    plt.savefig('../../results/visualization/tools_graph.png', format='png', dpi=500, bbox_inches='tight')


def main():
    visualize_tools(project_sec)


if __name__ == "__main__":
    main()
