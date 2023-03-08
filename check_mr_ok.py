import sys
import gitlab
from colorama import Fore, Back, Style
import json
import re


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def find_issue_ids_from_desc(desc):
    issue_id_list = []
    issue_id_regex = re.compile(r"#(\d+)")
    issue_id_list = issue_id_regex.findall(desc)
    return issue_id_list


def get_issues_from_ids(issue_id_list):
    issues = []
    for issue_id in issue_id_list:
        issue = mixit_project.issues.get(issue_id)
        issues.append(issue)
    return issues


config = load_config()
PAT = config["PAT"]
gl = gitlab.Gitlab(private_token=PAT)
gl.auth()

# load the mixit project
mixit_project_id = config["mixit_project_id"]
mixit_project = gl.projects.get(mixit_project_id)

print("Project: %s" % mixit_project.name)

# get all mr created by the user
user_name = sys.argv[1]

# get the user
user = gl.users.list(username=user_name)[0]
print(f"User: {user.name}")
user_id = user.id

# get all merge requests created by the user
merge_requests = mixit_project.mergerequests.list(
    author_id=user_id, state="opened", get_all=True
)

# find all merge requests that have related issues
for mr in merge_requests:
    print(f"MR: {mr.title}")
    print(f"URL: {mr.web_url}")
    issues = get_issues_from_ids(find_issue_ids_from_desc(mr.description))
    print(f"Issues: {len(issues)}")

    if len(issues) == 0:
        print(f"  {Fore.RED + Back.WHITE}No related issues found{Style.RESET_ALL}")

    for issue in issues:
        if issue.state == "opened":
            print("  Issue Opened")
            print(f"  URL: {issue.web_url}")
            print(f"  Created at: {issue.created_at}")

            # check if the merge request was merged but the issue is still open, issue label should be QA Testing
            if mr.state == "merged":
                print(f"  {Fore.YELLOW + Back.WHITE}MR is merged{Style.RESET_ALL}")
                labels = issue.labels
                if any(
                    (
                        (label.split("::")[-1].lower() == "qa testing")
                        for label in labels
                    )
                ):
                    print(
                        f"  {Fore.GREEN + Back.WHITE}Issue is labeled for QA Testing{Style.RESET_ALL}"
                    )
            else:
                print(f"  {Fore.YELLOW + Back.WHITE}MR is not merged{Style.RESET_ALL}")

                # check if issue is labeled for integration
                labels = issue.labels
                if any(
                    (
                        (label.split("::")[-1].lower() == "integration")
                        for label in labels
                    )
                ):
                    print(
                        f"  {Fore.GREEN + Back.WHITE}Issue is labeled for Integration{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"  {Fore.RED + Back.WHITE}Issue is not labeled for Integration{Style.RESET_ALL}"
                    )
