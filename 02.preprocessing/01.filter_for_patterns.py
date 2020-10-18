import json
import yaml
import glob


def load_patterns():
    """
    Load patterns to find usage of package managers in CI files.

    :return: List of patterns
    """
    with open('../resources/package_manager_patterns.txt', 'r') as infile:
        return [pattern.strip() for pattern in infile.readlines()]


def filter_projects():
    """
    Filter for projects for that we already crawled log files.

    :return: list of projects
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


def ci_files_for_projects(projects):
    """
    Load CI files for projects.

    :param projects: list of projects for that we already crawled log files
    :return: dict, map project to CI files
    """
    ci_files = {}
    for project in projects:
        files = glob.glob('../results/01.crawling/02.ci-files/{}/.travis.yml'.format(project))
        ci_files[project] = files
    return ci_files


def log_files_for_project(projects):
    """
    Load log files for projects.

    :param projects: list of projects for that we already crawled log files
    :return: dict, map project to log files
    """
    log_files = {}
    for project in projects:
        files = glob.glob('../results/01.crawling/03.logs/travis/{}/*/*.txt'.format(project))
        log_files[project] = files

    return log_files


def traverse_yaml(content):
    """
    Parse commands in CI file to list of commands for easier pattern detection.

    :param content: dict, mapping project to CI files
    :return: list of strings containing commands
    """
    commands = []
    if type(content) == str:
        commands.append(content)
    elif type(content) in [bool, float, int]:
        commands.append(str(content))
    elif type(content) == dict:
        for _, values in content.items():
            commands.extend(traverse_yaml(values))
    elif type(content) == list:
        for values in content:
            commands.extend(traverse_yaml(values))
    else:
        pass
    return commands


def filter_ci_files(proj_files, patterns):
    """
    Filter projects in which package manager patterns are used.
    Save start and end command of the script that need to be removed in the log files.

    :param proj_files: dict, map project to CI files
    :param patterns: List of patterns
    :return: dict, mapping of project to chunk that needs to be removed
    """
    remove_in_file = {}
    counter = 1
    for project, ci_files in proj_files.items():
        if not counter % 100:
            print("Progress: {:.2%}".format(counter / len(proj_files)))
        counter += 1
        for ci_file in ci_files:
            to_remove = []
            with open(ci_file) as infile:
                try:
                    content = yaml.load(infile, Loader=yaml.FullLoader)
                    removable = {}
                    commands = traverse_yaml(content)
                    for i in range(len(commands)):
                        command = commands[i]
                        remove = False
                        for pattern in patterns:
                            if pattern in command:
                                remove = True
                                if "start" not in removable:
                                    removable["start"] = command
                        if "start" in removable and not remove:
                            removable["end"] = command
                            if i < len(commands)-1:
                                removable["alternative end"] = commands[i+1]
                            to_remove.append(removable)
                            removable = {}
                except Exception as e:
                    to_remove.append({'start': 'not valid', 'stop': 'not valid'})
            remove_in_file[project] = to_remove
    return remove_in_file


def write_to_file(to_remove):
    """
    Save mapping of project to chunk that needs to be removed.

    :param to_remove: dict, mapping of project to chunk that needs to be removed
    :return: None
    """
    with open('../results/02.preprocessing/patterns_in_files.json', 'w') as outfile:
        json.dump(to_remove, outfile)


def main():
    projects = filter_projects()
    ci_files = ci_files_for_projects(projects)
    patterns = load_patterns()
    remove_in_file = filter_ci_files(ci_files, patterns)
    write_to_file(remove_in_file)


if __name__ == "__main__":
    main()
