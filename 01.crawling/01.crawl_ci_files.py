import os
import re
import datetime
import json
from time import sleep

import pandas as pd
from github import Github
from github.GithubException import RateLimitExceededException

cases = {'Travis': '.travis.yml', 'GitHub': '.github', 'GitLab CI': '.gitlab-ci.yml', 'Circle CI': '.circleci'}


def print_info(index, df, g):
    """
    Print crawling progress information including ratelimit information.

    :param index: Integer stating crawling progress
    :param df: pandas.Dataframe
    :param g: github.Github
    :return: None
    """
    print("STATUS! Remaining Request Number: ", g.get_rate_limit(), "Progress: ", index / df.shape[0], "%")


def authenticate(access_token):
    """
    Authenticate github api client.

    :param access_token: https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token
    :return: github.Github
    """
    g = Github(access_token)
    return g


def load_enterprise_oss():
    """
    Load Enterprise Open Source Software Dataframe.

    :return: pandas.Dataframe
    """
    e_oss_path = '../resources/enterprise-oss/enterprise_projects.txt'
    separator = '\t'
    column_names = ['url', 'project_id', 'sdtc', 'mcpc', 'mcve', 'star_number', 'commit_count', 'files', 'lines',
                    'pull_requests', 'most_recent_commit', 'committer_count', 'author_count', 'dominant_domain', 'dominant_domain_committer_commits', 'dominant_domain_author_commits', 'dominant_domain_committers', 'dominant_domain_authors', 'cik', 'fg500', 'sec10k', 'sec20f', 'project_name', 'owner_login', 'company_name', 'owner_company', 'license']

    oss_df = pd.read_csv(e_oss_path, sep=separator, names=column_names, header=None)
    return oss_df


def prepare_infrastructure(oss_df):
    """
    Create the necessary directories to store the CI files.

    :param oss_df: pandas.Dataframe
    :return: None
    """
    results_path = '../results/01.crawling/02.ci-files/'
    try:
        os.mkdir(results_path)
    except FileExistsError:
        print("The path ", results_path, " already exists.")

    for _, row in oss_df.iterrows():
        try:
            os.makedirs(results_path + row['owner_login'] + '/' + row['project_name'])
        except FileExistsError:
            pass


def save_ci_files(content, case, identifier, repo):
    """
    Save the CI files per project depending on the CI service used per project.

    :param content: github.ContentFile.ContentFile
    :param case: string containing name of CI service
    :param identifier: string "owner/project"
    :param repo: github.Repository.Repository
    :return: None
    """
    results_path = '../results/01.crawling/02.ci-files/' 
    if case == "GitHub":
        try:
            os.mkdir(results_path + identifier + '/.github')
            for gh_content in repo.get_contents('.github/workflows'):
                with open(results_path + identifier + '/' + '.github/' + gh_content.name, 'w') as file:
                    file.write(gh_content.decoded_content.decode("utf-8"))
        except:
            pass
    elif case == "Circle CI":
        try:
            os.mkdir(results_path + identifier + '/.cirleci')
            for ci_content in repo.get_contents('.circleci'):
                with open(results_path + identifier + '/' + '.circleci/' + ci_content.name, 'w') as file:
                    file.write(ci_content.decoded_content.decode("utf-8"))
        except:
            pass
    else:
        with open(results_path + identifier + '/' + content.name, 'w') as file:
            file.write(content.decoded_content.decode("utf-8"))


def identify_ci_files(contents, identifier, repo):
    """
    Identify if a CI service is used in project and if so, which.

    :param contents: list of github.ContentFile.ContentFile
    :param identifier: string "owner/project"
    :param repo: github.Repository.Repository
    :return: list of CI services
    """
    status = []
    for content in contents:
        for case, pattern in cases.items():
            if re.search(pattern, content.name):
                save_ci_files(content, case, identifier, repo)
                status.append(case)
    return status


def crawl_files(owner_project_id, g):
    """
    Manage crawling CI files for each project.

    :param owner_project_id: string "owner/project"
    :param g: github.Github
    :return: list of CI services
    """
    try:
        repo = g.get_repo(owner_project_id)
        contents = repo.get_contents('.')
        status = identify_ci_files(contents, owner_project_id, repo)
        return status
    except RateLimitExceededException:
        print("\n------------------------------------------------------------\n")
        print("RateLimitExceeded")
        raise Exception("RateLimitExceeded")
        status = ["Ratelimit"]
        return status
    except Exception as e:
        status = ["404"]
        return status


def manage_api_routine(df, g, project_status = {}, missing=False):
    """
    Manage api routine requests and ratelimits.

    :param df: pandas.Dataframe
    :param g: github.Github
    :param project_status: dict with project to CI services mapping, used in combination with missing
    :param missing: bool, used to crawl all projects that were missed due to ratelimit in the first run
    :return: dict with project to CI services mapping
    """
    if missing:
        for project, status in project_status.items():
            if status != ["Ratelimit"]:
                identifier = project.split("/")
                df.drop(df[(df['owner_login'] == identifier[0]) & (df['project_name'] == identifier[1])].index, inplace=True)

    for index, row in df.iterrows():
        identifier = row['owner_login'] + '/' + row['project_name']
        try:
            status = crawl_files(identifier, g)
            project_status[identifier] = status
        except Exception as e:
            print(e)
            next_reset = g.get_rate_limit().core.reset
            current_time = datetime.datetime.utcnow()
            to_sleep = next_reset - current_time
            print("Progress in Dataset: ", index / df.shape[0], '%')
            print("Seconds to wait: ", to_sleep.seconds)
            print("Start Sleeping (UTC): ", current_time)
            sleep(to_sleep.seconds + 10)
            print("Done Sleeping (UTC): ", datetime.datetime.utcnow())
            print("\n------------------------------------------------------------\n")
        if index % 500 == 0:
            print_info(index, df, g)
    with open('../results/01.crawling/01.project_ci_services.json', 'w') as file:
        json.dump(project_status, file)
    return project_status


def save_status(status, results_path):
    """
    Save project - CI file mapping as json file.

    :param status: dict with project to CI services mapping
    :param results_path: string to store file
    :return: None
    """
    with open(results_path, 'w') as outfile:
        json.dump(status, outfile)


def main():
    # 1. Run crawl all files possible
    oss_df = load_enterprise_oss()
    prepare_infrastructure(oss_df)
    g = authenticate("YOUR-TOKEN") #TODO: Add your personal github access token
    status = manage_api_routine(oss_df, g)

    # 2. Run crawl all files, that weren't crawled because of Ratelimit
    sleep(3610)
    status = manage_api_routine(oss_df, g, status, True)

    # 3. Final run to crawl all files, that also weren't crawled because of Ratelimit in 2. Run.
    sleep(3610)
    status = manage_api_routine(oss_df, g, status, True)
    save_status(status, '../results/01.crawling/01.project_ci_services.json')


if __name__ == '__main__':
    main()
