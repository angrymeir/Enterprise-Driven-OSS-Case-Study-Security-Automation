import json
import glob
from collections import defaultdict


def filter_projects():
    """
    Filter projects for that we crawled log files.

    :return: list of project names
    """
    with open('../results/01.crawling/04.project_logs_overview.json', 'r') as infile:
        pr_log_status = json.load(infile)

    projects = []

    for project, builds in pr_log_status.items():
        try:
            builds['files']
        except:
            continue
        if builds['files']:
            projects.append(project)

    return projects


def file_for_project(projects, cleaned):
    """
    Load log files for projects.


    :param projects: list of project names
    :return: list of cleaned filenames
    """
    project_files = {}
    for project in projects:
        if cleaned:
            files = glob.glob('../results/01.crawling/03.logs/travis/{}/*/*.cleaned'.format(project))
        else:
            files = glob.glob('../results/01.crawling/03.logs/travis/{}/*/*.txt'.format(project))
        project_files[project] = files

    return project_files


def load_patterns():
    """
    Load security patterns.

    :return: dict, mapping of security activities to security tools to security patterns
    """
    with open('../resources/security_patterns.json', 'r') as infile:
        sec_patterns = json.load(infile)

    return sec_patterns


def analyze_files(proj_files, patterns):
    """
    Analyze log files whether they use security tools.

    :param proj_files: list of log file names
    :param patterns: dict, mapping security activities to security tools to security patterns.
    :return: dict, mapping projects to security tools used in these projects
    """
    sec_in_projects = defaultdict(list)
    counter = 0
    for project, files in proj_files.items():

        if counter % 10 == 0:
            print('Progress: {:.2%}'.format(counter / len(proj_files)))
        counter += 1

        for file in files:
            with open(file) as infile:
                content = infile.read()

                for _, tools in patterns.items():

                    for tool, details in tools.items():
                        sec = False
                        for pattern in details['Patterns']:
                            if pattern.lower() in content.lower():
                                sec = True
                        if sec:
                            sec_in_projects[project].append(tool)
    for project, tools in sec_in_projects.items():
        sec_in_projects[project] = list(set(tools))
    return sec_in_projects


def write_to_file(sec_in_projects, file_name):
    """
    Save projects to security tools mapping.

    :param sec_in_projects: dict, mapping projects to security tools used in these projects
    :param file_name: string, filename
    :return: None
    """
    with open(file_name, 'w') as outfile:
        json.dump(sec_in_projects, outfile)


def main():
    cleaned = True
    projects = filter_projects()
    files = file_for_project(projects, cleaned)
    sec_patterns = load_patterns()
    sec_in_projects = analyze_files(files, sec_patterns)
    if cleaned:
        write_to_file(sec_in_projects, '../results/03.tools_usage_detection/log_files_security.json')
    else:
        write_to_file(sec_in_projects, '../results/03.tools_usage_detection/log_files_security_not_cleaned.json')


if __name__ == "__main__":
    main()
