import json
import glob
from collections import defaultdict


def filter_projects():
    """
    Filter out all projects using Travis CI and GitHub Actions.

    :return: list of project names
    """
    with open('../results/01.crawling/01.project_ci_services.json', 'r') as infile:
        projects = json.load(infile)
        tr_projects = []
        for project, value in projects.items():
            if "GitHub" in value or "Travis" in value:
                tr_projects.append(project)
    return tr_projects


def file_for_project(projects):
    """
    Get files projects.

    :param projects: list of project names
    :return: list of CI file names
    """
    project_files = {}
    for project in projects:
        github_files = glob.glob('../results/01.crawling/02.ci-files/{}/.github/*'.format(project))
        travis_files = glob.glob('../results/01.crawling/02.ci-files/{}/.travis/*'.format(project))
        github_files.extend(travis_files)
        project_files[project] = github_files

    return project_files


def load_patterns():
    """
    Load security tool patterns.

    :return: dict, mapping security activities to security tools to security patterns.
    """
    with open('../resources/security_patterns.json', 'r') as infile:
        sec_patterns = json.load(infile)

    return sec_patterns


def analyze_files(proj_files, patterns):
    """
    Analyze CI files whether they use security tools.

    :param proj_files: list of CI file names
    :param patterns: dict, mapping security activities to security tools to security patterns.
    :return: dict, mapping projects to security tools used in these projects
    """
    sec_in_projects = defaultdict(list)
    counter = 0
    for project, files in proj_files.items():

        if counter % 1000 == 0:
            print('Progress: {:.2%}'.format(counter/len(proj_files)))
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
    projects = filter_projects()
    files = file_for_project(projects)
    sec_patterns = load_patterns()
    sec_in_projects = analyze_files(files, sec_patterns)
    write_to_file(sec_in_projects, '../results/03.tools_usage_detection/ci_files_security.json')


if __name__ == "__main__":
    main()
