import json
import datetime
from time import sleep
from github import Github
from github.GithubException import RateLimitExceededException


def authenticate(access_token):
    """
    Authenticate github api client.

    :param access_token: https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token
    :return: github.Github
    """
    g = Github(access_token)
    return g


def load_projects():
    """
    Load Project - CI file mapping to dict.

    :return: dict with project to CI services mapping
    """
    with open('../results/01.crawling/01.project_ci_services.json', 'r') as infile:
        projects = json.load(infile)
    return projects


def crawl_characteristics(g, projects, project_stars={}, project_languages={}, project_timespan={}, missing=False):
    """
    Crawl characteristics of projects.
    Characteristics:
    - Stars of project
    - Languages of project
    - Timespan of project, when it was created and when it was last updated

    :param g: github.Github
    :param projects: dict with project to CI services mapping
    :param project_stars: dict maping project to stars, used if missing
    :param project_languages: dict maping project to languages, used if missing
    :param project_timespan: dict maping project to timespan, used if missing
    :param missing: bool, used to crawl all projects that were missed due to ratelimit in the first run 
    :return: dict, mapping of github project to stars,
             dict, mapping of github project to languages,
             dict, mapping of github project to timespan
    """
    
    if missing:
        projects = {}
        for project, languages in project_languages.items():
            if languages == "Ratelimit":
               projects[project] = "Ratelimit"

    keys = list(projects.keys())
    for idx in range(len(keys)):
        if not idx%500:
            print("STATUS! Remaining Request Number: ", g.get_rate_limit(), "Progress: ", idx / len(keys), "%")
        project = keys[idx]
        try:
            repo = g.get_repo(project)
            # Repositories Stars
            stars = repo.stargazers_count
            project_stars[project] = stars
            # Repositories Languages
            languages = repo.get_languages()
            project_languages[project] = languages
            # Repositories Timerange
            created = repo.created_at.year
            for year in range(2020, 2011, -1):
                commits = repo.get_commits(since=datetime.datetime(year, 1, 1, 0, 0, 0))
                if commits.totalCount:
                    if created > year:
                        year = created
                    project_timespan[project] = (created, year)
                    break

        except RateLimitExceededException:
            next_reset = g.get_rate_limit().core.reset
            current_time = datetime.datetime.utcnow()
            to_sleep = next_reset - current_time
            print("\n------------------------------------------------------------\n")
            print("Progress in Dataset: ", idx / len(keys), '%')
            print("Seconds to wait: ", to_sleep.seconds)
            print("Start Sleeping (UTC): ", current_time)
            sleep(to_sleep.seconds + 10)
            print("Done Sleeping (UTC): ", datetime.datetime.utcnow())
            print("\n------------------------------------------------------------\n")
            project_stars[project] = "Ratelimit"
            project_languages[project] = "Ratelimit"
            project_timespan[project] = "Ratelimit"
        except:
            pass
    return project_stars, project_languages, project_timespan


def write_characteristics(characteristic, descr):
    """
    Save project - characteristics mapping as json file.

    :param characteristic: dict, mapping of project to characteristic (either stars, topics or timespan)
    :param descr: string, name of characteristics
    :return: None
    """
    with open('../results/01.crawling/05.characteristics/{}.json'.format(descr), 'w') as outfile:
        json.dump(characteristic, outfile)


def main():
    g = authenticate("YOUR-TOKEN") #TODO: Add your personal github access token

    # 1. Run
    projects = load_projects()
    stars, languages, timespan = crawl_characteristics(g, projects)

    # 2. Run to crawl for those skipped due to Ratelimit
    sleep(3610)
    stars, languages, timespan = crawl_characteristics(g, projects, stars, languages, timespan, missing=True) 

    write_characteristics(stars, 'project_stars')
    write_characteristics(timespan, 'project_timespan')
    write_characteristics(languages, 'project_languages')


if __name__ == "__main__":
    main()
