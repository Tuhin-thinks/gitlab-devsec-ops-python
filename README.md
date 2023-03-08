# gitlab-devsec-ops-python
Set of automation scripts to find out useful information about gitlab project and automate actions.

## Requirements
___
**Python version 3.7 or higher**

### Python Packages
___
**Gitlab** - https://python-gitlab.readthedocs.io/en/stable/
\
**colorama** - https://pypi.org/project/colorama/


INSTALLATION
```
pip install python-gitlab
pip install colorama
```

### ⚠ Important: Config file
___
create a config.json file on the project root folder.

_JSON file contents_
```json
{
    "project_id": <project-id>,
    "PAT": "<gitlab-personal-access-token>"
}
```

## Usage
___
### 1. check_approves.py
This script will check if the merge request has the minimum number of approves.

### 2. check_mr_ok.py
This script will check, if all open merge requests for a particular user (username provided by user) is in correct label or not.

### 3. find_resolved_issues.py
This script will scan through all assigned issues for a particular user (username provided by user) and find out 
whether all the issues and their related merge requests are in correct label or not.