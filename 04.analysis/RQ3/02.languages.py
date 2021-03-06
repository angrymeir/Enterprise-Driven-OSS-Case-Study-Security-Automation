import json
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud

with open('../../results/03.tools_usage_detection/all_projects_security.json', 'r') as infile:
    sec = json.load(infile)

with open('../../results/01.crawling/05.characteristics/project_languages.json', 'r') as infile:
    languages = json.load(infile)

with open('../../resources/security_patterns.json', 'r') as infile:
    sec_patterns = json.load(infile)


def act_per_project(sec, sec_patterns):
    """
    Map security activities to project.

    :param sec: mapping of projects to security tools
    :param sec_patterns: mapping of security activities to security tools
    :return: dict, mapping projects to security activities.
    """
    mapping = defaultdict(set)
    for proj, tools in sec.items():
        for tool in tools:
            for activity, ts in sec_patterns.items():
                if tool in ts:
                    mapping[proj].add(activity)
        if not len(tools):
            mapping[proj].add("No Security")
    return mapping


m_pr_act = act_per_project(sec, sec_patterns)


def normalize_languages(languages):
    """
    Normalize language usage. Divide the number of bytes programmed in a language by number of all bytes programmed in that projects.
    
    :param languages: dict, language to number of bytes programmed in language mapping
    :return: dict, language to normalized number of bytes programmed in language mapping
    """
    total = sum(languages.values())
    return {key: value/total for key,value in languages.items()}


def lang_to_act(lang, m_pr_act):
    """
    Map security activities to languages and their respective usage in the security activity.

    :param lang: dict, project, to languages and languages usage mapping
    :param m_pr_act: dict, security activity to language and languages usage mapping
    """
    mapping = defaultdict(lambda: defaultdict(float))
    for project, acts in m_pr_act.items():
        languages = lang[project]
        norm_languages = normalize_languages(languages)
        for act in acts:
            for language, norm_count in norm_languages.items():
                mapping[act][language] += norm_count
    return mapping


m_lang_act = lang_to_act(languages, m_pr_act)


def visualize_lang(m_lang_act):
    """
    Visualize language usage per security activity in wordcloud.

    :param m_lang_act: dict, security activity to language and languages usage mapping
    """
    for act, languages in m_lang_act.items():
        wc = WordCloud(background_color="white", min_font_size=8, width=1600, height=800, margin=0).generate_from_frequencies(languages)
        plt.title(act)
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.savefig('../../results/visualization/{}-wordcloud.png'.format(act.replace("/","-").replace(" ", "_")), format='png', dpi=500, bbox_inches='tight')


visualize_lang(m_lang_act)
