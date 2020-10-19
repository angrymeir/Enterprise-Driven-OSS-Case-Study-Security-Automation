import json
import glob


def load_remove_patterns():
    """
    Load chunks that need to be removed from log files.
    Each chunk contains the starting and ending command.

    :return: dict, mapping of project to chunk that needs to be removed
    """
    with open('../results/02.preprocessing/patterns_in_files.json', 'r') as infile:
        to_remove = json.load(infile)
    return to_remove


def log_files_project(project):
    """
    Get all logs files we crawled for the respective project

    :param project: string with project name
    :return: list of filenames
    """
    files = glob.glob('../results/01.crawling/03.logs/travis/{}/*/*.txt'.format(project))
    return files


def remove_pattern(old_content, pattern):
    """
    Remove all lines between start command in pattern and stop command in pattern.
    Example:
    old_content = ["command 1", "brew update", "ansible\ttrufflehog", "command 2"]
    patterns = {"start": "brew update", "end": "command 2"}

    content = ["command 1", "command 2"]

    :param old_content: list of log lines
    :param pattern: dict containing start and end that need to be removed
    :return: list of log lines
    """
    content = []
    start = pattern['start']
    end = pattern['end'] if 'end' in pattern else ''
    alt_end = pattern['alternative end'] if 'alternative end' in pattern else ''

    add = True
    for command in old_content:
        if start in command:
            add = False
        elif add:
            content.append(command)
        elif not add and end and end in command:
            add = True
            content.append(command)
        elif not add and alt_end and alt_end in command:
            add = True
            content.append(command)
        else:
            pass

    return content


def save_cleaned_file(log, content):
    """
    Save cleaned log files.

    :param log: filename of logfile
    :param content: list of filtered log lines
    :return: None
    """
    with open(log.replace('.txt', '.cleaned'), 'w') as infile:
        infile.write('\n'.join(content))


def filter_proj(patt_in_file):
    """
    Filter out chunks from log files.

    :param patt_in_file: dict, mapping of project to chunks that need to be removed.
    :return: None
    """
    counter = 0
    for project, patterns in patt_in_file.items():
        if not counter % 100:
            print("Progress: {:.2%}".format(counter / len(patt_in_file)))
        counter += 1
        logs = log_files_project(project)
        
        for log in logs:
            with open(log, 'r') as infile:
                content = [line.rstrip('\n') for line in infile.readlines()]

            for pattern in patterns:
                content = remove_pattern(content, pattern)
            save_cleaned_file(log, content)


def main():
    patterns = load_remove_patterns()
    filter_proj(patterns)


if __name__ == "__main__":
    main()
