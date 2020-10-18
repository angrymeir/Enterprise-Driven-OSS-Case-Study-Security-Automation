import json


def load_status(sec_status):
    """
    Load security to project mapping.

    :param sec_status: string, filename for security to project mapping
    :return: dict, mapping projects to security tools used in these projects
    """
    with open(sec_status, 'r') as infile:
        return json.load(infile)


def filter_projects(project_services):
    """
    Filter projects for that we crawled log files.

    :param project_services: dict, map project, CI services
    :return: list of project names
    """
    return [project for project, services in project_services.items() if "Travis" in services or "GitHub" in services]


def combine_results(projects, ci_sec, log_sec):
    """
    Combine the security tools findings of CI files and Log files.

    :param projects: list of project names
    :param ci_sec: dict, mapping projects to security tools used in these projects detected in CI files
    :param log_sec: dict, mapping projects to security tools used in these projects detected in log files
    :return: dict, mapping projects to security tools used in these projects detected in either, CI files or log files
    """
    security_common = {}
    for project in projects:
        sec = []
        if project in ci_sec:
            sec.extend(ci_sec[project])
        if project in log_sec:
            sec.extend(log_sec[project])
        security_common[project] = list(set(sec))
    return security_common


def main():
    project_ci_services = load_status('../results/01.crawling/01.project_ci_services.json')
    file_security = load_status('../results/03.tools_usage_detection/ci_files_security.json')
    log_file_security = load_status('../results/03.tools_usage_detection/log_files_security.json')

    relevant_projects = filter_projects(project_ci_services)
    security_combined = combine_results(relevant_projects, file_security, log_file_security)

    with open('../results/03.tools_usage_detection/all_projects_security.json', 'w') as infile:
        json.dump(security_combined, infile)


if __name__ == "__main__":
    main()
