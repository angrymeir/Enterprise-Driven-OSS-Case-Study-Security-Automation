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
    total = sum(languages.values())
    return {key: value/total for key,value in languages.items()}


def lang_to_act(lang, m_pr_act):
    mapping = defaultdict(lambda: defaultdict(float))
    for project, acts in m_pr_act.items():
        languages = lang[project]
        norm_languages = normalize_languages(languages)
        for act in acts:
            for language, norm_count in norm_languages.items():
                mapping[act][language] += norm_count
    return mapping


m_lang_act = lang_to_act(languages, m_pr_act)


for act, languages in m_lang_act.items():
    wc = WordCloud(background_color="white", min_font_size=8, width=1600, height=800, margin=0).generate_from_frequencies(languages)
    plt.title(act)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('../../results/visualization/{}-wordcloud.png'.format(act.replace("/","-").replace(" ", "_")), format='png', dpi=500, bbox_inches='tight')