import csv
import requests

from pandas.io.json import json_normalize
import pandas as pd

github_api = "https://api.github.com"

# Change...
GITHUB_USERNAME = "sinatav"
GITHUB_TOKEN = "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"
repo = 'openstack'
owner = 'nova'

gh_session = requests.Session()
gh_session.auth = (GITHUB_USERNAME, GITHUB_TOKEN)

is_next = True
page = 1
commits = []
while is_next:
    url = github_api + '/repos/{}/{}/commits?page={}&per_page=100'.format(repo, owner, page)
    commit_pg = gh_session.get(url=url)
    commit_pg_list = [dict(item, **{'repo_name': '{}'.format(repo)}) for item in commit_pg.json()]
    commit_pg_list = [dict(item, **{'owner': '{}'.format(owner)}) for item in commit_pg_list]
    commits = commits + commit_pg_list
    if 'Link' in commit_pg.headers:
        if 'rel="next"' not in commit_pg.headers['Link']:
            is_next = False
    page += 1

commits_df = json_normalize(commits)
commits_df['date'] = pd.to_datetime(commits_df['commit.committer.date'])
commits_df['date'] = pd.to_datetime(commits_df['date'], utc=True)
commits_df['commit_date'] = commits_df['date'].dt.date
commits_df['commit_year'] = commits_df['date'].dt.year
commits_df['commit_month'] = commits_df['date'].dt.month
commits_df['commit_day'] = commits_df['date'].dt.day

is_2021 = commits_df['commit_year'] == 2021
commits_2021 = commits_df[is_2021]
is_after_april = commits_2021['commit_month'] >= 5
commits_after_april = commits_2021[is_after_april]
shas = [sha for sha in commits_after_april['sha']]

stats = []
for sha in shas:
    insp = gh_session.get(github_api + '/repos/openstack/nova/commits/' + sha).json()
    for files in insp['files']:
        stats.append([files['filename'], files['changes']])

modules = []
for stat in stats:
    if stat[0].endswith('.py'):
        modules.append(stat)

changes = {}
for module in modules:
    if module[0] in list(changes.keys()):
        changes[module[0]] += module[1]
    else:
        changes[module[0]] = module[1]
changes_sorted = {k: v for k, v in sorted(changes.items(), key=lambda item: item[1], reverse=True)}
commits_per_file = {file_name: 0 for file_name in list(changes.keys())}
for module in modules:
    commits_per_file[module[0]] += 1
commits_per_file_sorted = {k: v for k, v in sorted(commits_per_file.items(), key=lambda item: item[1], reverse=True)}
churn_top_12 = {k: v for k, v in sorted(changes.items(), key=lambda item: item[1], reverse=True)[:12]}
num_commits_top_12 = {k: v for k, v in sorted(commits_per_file.items(), key=lambda item: item[1], reverse=True)[:12]}

for i in churn_top_12:
    print(i)

for i in num_commits_top_12:
    print(i)

with open('ind1.csv', 'w') as f:
    for key in num_commits_top_12.keys():
        f.write("%s,%s\n" % (key, num_commits_top_12[key]))

with open('ind2.csv', 'w') as f:
    for key in churn_top_12.keys():
        f.write("%s,%s\n" % (key, churn_top_12[key]))
