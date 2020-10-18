import json
from collections import defaultdict, Counter

with open('../../results/03.tools_usage_detection/all_projects_security.json', 'r') as infile:
    sec_in_projects = json.load(infile)


with open('../../resources/security_patterns.json', 'r') as infile:
    sec_patterns = json.load(infile)

def prevalence_in_projects():
    all = len(sec_in_projects)
    sec = len([pr for pr, sec in sec_in_projects.items() if len(sec)])
    print("Prevalence in projects is {:.2%}. {} of {} projects perform security.".format(sec/all, sec, all))


def distr_of_sec_act():
    act_project_map = []
    for project, tools in sec_in_projects.items():
        proj_act = set()
        for tool in tools:
            for act, ts in sec_patterns.items():
                if tool in ts:
                    proj_act.add(act)
        act_project_map.extend(list(proj_act))
    print("Distribution of performed security activities:", Counter(act_project_map))


def act_performed_together():
    num_act = []
    combined_cases = defaultdict(int)
    for proj, tools in sec_in_projects.items():
        act = []
        for tool in tools:
            for sec_act, val in sec_patterns.items():
                if tool in val.keys():
                    act.append(sec_act)
        num_act.append(len(list(set(act))))
        if len(act) > 1:
            combined_cases[tuple(sorted(list(set(act))))] +=1
    print("How many security activities are performed per project?")
    print(Counter(num_act))
    print("Activities performed together")
    print({k: v for k, v in sorted(combined_cases.items(), key=lambda item: item[1], reverse=True)})

def main():
    #prevalence_in_projects()
    #distr_of_sec_act()
    act_performed_together()


if __name__ == "__main__":
    main()