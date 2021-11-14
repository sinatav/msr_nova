import json
import requests
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np

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



