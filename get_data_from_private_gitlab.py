# -*- coding: utf-8 -*-
"""Get_data_from_private_GITLAB.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RPqlBdwN3Om8AoFwr3Z-rTQzgTKN-WOr
"""

pip install XlsxWriter

import requests
import xlsxwriter
import pandas as pd
import warnings

# Personal Information
token = ''
owner = ''
repo_name = ''

# Authorization
headers = {
    'Authorization': f'token {token}'
}


# Commits!
# GET request to GitHub API to get commit history
commits_url = f'https://api.gitlab.com/repos/{owner}/{repo_name}/commits'

response = requests.get(commits_url, headers=headers)

# Checking the status of a response
if response.status_code == 200:
    # Get JSON-data
    commits_data = response.json()

    commits_df = pd.DataFrame()

    for commit in commits_data:
        commit_sha = commit['sha']
        commit_message = commit['commit']['message']
        commit_author = commit['commit']['author']['name']
        commit_date = commit['commit']['author']['date']
        commit_comment_count = commit['commit']['comment_count']
        commit_committer_login = commit['committer']['login']

        commits_df = commits_df.append({'commit_sha':commit_sha,
                                        'commit_message':commit_message,
                                        'commit_author':commit_author,
                                        'commit_date':commit_date,
                                        'commit_comment_count':commit_comment_count,
                                        'commit_committer_login':commit_committer_login
                                      }, ignore_index=True)

# Change data type
commits_df['commit_date'] = pd.to_datetime(commits_df['commit_date']).dt.date

# Count of actions performed by each user by all the time
if len(commits_df) != 0:
  df_commits_count = commits_df.groupby('commit_author').agg({'commit_date':'count'}).rename(columns={'commit_date':'commit_count'}).reset_index().sort_values('commit_count', ascending=False)

# Count of actions performed by each user per date
if len(commits_df) != 0:
  df_commits_all_data_count = commits_df.groupby(['commit_author', 'commit_date']).agg({'commit_date':'count'}).rename(columns={'commit_date':'commit_count'}).reset_index().sort_values('commit_date')

# Mean time per user
result_data_commits = []

# Unique authors
authors = commits_df['commit_author'].unique()

for author in authors:
    author_data = commits_df[commits_df['commit_author'] == author]
    author_data = author_data.sort_values('commit_date')
    author_data['delta'] = author_data['commit_date'].diff().fillna(pd.Timedelta(seconds=0))
    average_delta = author_data['delta'].mean()
    result_data_commits.append(pd.Series({'commit_author': author, 'average_delta': average_delta}))

result_df_commits = pd.concat(result_data_commits, axis=1).T
result_df_commits = result_df_commits.reset_index(drop=True)

result_df_commits['delta_seconds'] = result_df_commits['average_delta'].dt.total_seconds()
mean_delta_per_user = result_df_commits[result_df_commits['delta_seconds'] > 0][['commit_author', 'average_delta']]
mean_commit_delta_per_user = mean_delta_per_user.rename(columns={'average_delta':'average_delta_days'}).sort_values('average_delta_days', ascending=False)



# Pull Requests!
# GET request to GitHub API to get pull request history
pulls_url = f'https://api.github.com/repos/{owner}/{repo_name}/events'

response = requests.get(pulls_url, headers=headers)

# Checking the status of a response
if response.status_code == 200:
    pulls_data = response.json()

    pulls_df = pd.DataFrame()

    for pull in pulls_data:
        pull_id = pull['id']
        pull_type = pull['type']
        pull_actor = pull['actor']['login']
        pull_created_at = pull['created_at']


        pulls_df = pulls_df.append({'id':pull_id,
                                    'pull_type':pull_type,
                                    'pull_actor':pull_actor,
                                    'pull_created_at':pull_created_at
                                      }, ignore_index=True)

# Change data type
pulls_df['pull_created_at'] = pd.to_datetime(pulls_df['pull_created_at']).dt.date


# Count of actions performed by each user by all the time
if len(pulls_df) != 0:
  df_pulls_count = pulls_df.groupby('pull_actor').agg({'pull_created_at':'count'}).rename(columns={'pull_created_at':'pulls_count'}).reset_index().sort_values('pulls_count', ascending=False)

# Count of actions performed by each user per date
if len(pulls_df) != 0:
  df_pulls_all_data_count = pulls_df.groupby(['pull_actor', 'pull_created_at']).agg({'pull_created_at':'count'}).rename(columns={'pull_created_at':'pulls_count'}).reset_index().sort_values('pull_created_at')


# Mean time per user
if len(pulls_df['pull_actor'].unique()) != 0:

  result_data_pulls = []

  # Unique authors
  authors = pulls_df['pull_actor'].unique()

  for author in authors:
      author_data = pulls_df[pulls_df['pull_actor'] == author]
      author_data = author_data.sort_values('pull_created_at')
      author_data['delta'] = author_data['pull_created_at'].diff().fillna(pd.Timedelta(seconds=0))
      average_delta = author_data['delta'].mean()
      result_data_pulls.append(pd.Series({'pull_actor': author, 'average_delta': average_delta}))

  result_df_pulls = pd.concat(result_data_pulls, axis=1).T
  result_df_pulls = result_df_pulls.reset_index(drop=True)

  result_df_pulls['delta_seconds'] = result_df_pulls['average_delta'].dt.total_seconds()
  mean_delta_per_user = result_df_pulls[result_df_pulls['delta_seconds'] > 0][['pull_actor', 'average_delta']]
  mean_pull_delta_per_user = mean_delta_per_user.rename(columns={'average_delta':'average_delta_days'}).sort_values('average_delta_days', ascending=False)


# Events per users (without commits!)
all_events_df_gr = pulls_df.groupby(['pull_type', 'pull_actor']).agg({'id':'count'}).reset_index().sort_values(['pull_actor', 'pull_type']).rename(columns={'id':'count_values'})

# Pull Request only
pull_request_df = pulls_df[pulls_df['pull_type'] =='PullRequestEvent']
pull_request_df = pull_request_df.sort_values('pull_created_at')

warnings.filterwarnings('ignore')

# Writing to Excel
writer = pd.ExcelWriter('Commit_Pull_Data.xlsx', engine='xlsxwriter')

commits_df.to_excel(writer, sheet_name='All commit data', index = False)
df_commits_count.to_excel(writer, sheet_name='Count commits per user', index = False)
df_commits_all_data_count.to_excel(writer, sheet_name='Count commits per user by date', index = False)
mean_commit_delta_per_user.to_excel(writer, sheet_name='Commits mean delta time', index = False)

pulls_df.to_excel(writer, sheet_name='All pulls data', index = False)
df_pulls_count.to_excel(writer, sheet_name='Count pulls per user', index = False)
df_pulls_all_data_count.to_excel(writer, sheet_name='Count pulls per user by date', index = False)
mean_pull_delta_per_user.to_excel(writer, sheet_name='Pulls mean delta time', index = False)

all_events_df_gr.to_excel(writer, sheet_name='All events per user', index = False)
pull_request_df.to_excel(writer, sheet_name='Pull only', index = False)

writer.close()

