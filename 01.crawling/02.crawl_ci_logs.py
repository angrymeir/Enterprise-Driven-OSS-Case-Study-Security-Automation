import requests
import json
import os
from pathlib import Path
from time import sleep
import datetime


def authenticate(token):
    """
    Authentication to Travis CI

    :param token: string, containing authentication toke for Travis CI
    :return: string, dict
    """
    base_url = "https://api.travis-ci.org"
    headers = {
        'Travis-API-Version': '3',
        'Authorization': 'token {}'.format(token)
    }
    return base_url, headers


def filter_projects():
    """
    Filter all projects using the Travis CI service.

    :return: list of project names
    """
    with open('../results/01.crawling/01.project_ci_services.json') as infile:
        projects = json.load(infile)

    travis_projects = [project for project, ci_services in projects.items() if "Travis" in ci_services]
    return travis_projects


def crawl_files(projects, base_url, headers):
    """
    For each project crawl log files if possible and store them.

    :param projects: list of project names
    :param base_url: string, contains base url for Travis CI api
    :param headers: dict, contains authentication headers for Travis CI api
    :return: dict, mapping project to log status
    """
    counter = 0
    project_log_status = {}
    base_path = '../results/01.crawling/03.logs/travis/'
    for i in range(len(projects)):
        project = projects[i]
        counter += 1
        Path(base_path + project).mkdir(parents=True)
        extension = "/repo/{}/builds".format(project.replace("/", "%2F"))
        log_status = {}
        try:
            response = requests.get(base_url + extension, headers=headers, params={'limit': 3})
            data = response.json()
            builds = data['builds']
            log_status['builds'] = len(builds)
            for build in builds:
                os.mkdir(base_path + '{}/{}'.format(project, build['id']))
                extension = "/build/{}/jobs".format(build['id'])
                response = requests.get(base_url + extension, headers=headers)
                data = response.json()
                jobs = data['jobs']
                log_status['jobs'] = len(jobs)
                for job in jobs:
                    extension = "/job/{}/log".format(job['id'])
                    response = requests.get(base_url + extension, headers=headers)
                    data = response.json()
                    log_status['files'] = len(data)
                    response = requests.get(base_url + data['@raw_log_href'])
                    with open(base_path + '{}/{}/{}.txt'.format(project, build['id'], job['id']),
                              'w') as infile:
                        infile.write(response.content.decode('utf-8'))
        except KeyError:
            print("Failed at Project: {}".format(project))
            pass
        except:
            print("Failed at Project: {}. Going to sleep at {}".format(project, datetime.datetime.now()))
            sleep(3600)
        finally:
            if counter % 10 == 0:
                print('Progress: {}'.format(counter / len(projects)))
            project_log_status[project] = log_status

    return project_log_status


def write_log_status(log_status):
    """
    Save status of log crawling for each project.

    :param log_status:
    :return: None
    """
    with open('../results/01.crawling/04.project_logs_overview.json', 'w') as outfile:
        json.dump(log_status, outfile)


def main():
    base_url, headers = authenticate('') #TODO: Add your personal Travis access token
    projects = filter_projects()
    project_logs = crawl_files(projects, base_url, headers)
    write_log_status(project_logs)


if __name__ == "__main__":
    main()
