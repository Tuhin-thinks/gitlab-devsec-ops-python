import sys
import gitlab
from colorama import Fore, Back, Style
import json


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


config = load_config()
PAT = config["PAT"]
gl = gitlab.Gitlab(private_token=PAT)
gl.auth()

# load the mixit project
mixit_project_id = config["mixit_project_id"]
mixit_project = gl.projects.get(mixit_project_id)

print("Project: %s" % mixit_project.name)

# get all open issues created by the user
user_name = sys.argv[1]

# get the user
user = gl.users.list(username=user_name)[0]
print(f"User: {user.name}")
user_id = user.id

assigned_issues = mixit_project.issues.list(
    assignee_id=user_id, state="opened", get_all=True
)

# find all issues that have related merge requests
for issue in assigned_issues:
    print(f"Issue: {issue.title}")
    print(f"URL: {issue.web_url}")
    merge_requests = issue.related_merge_requests()
    print(f"Merge Requests: {len(merge_requests)}")

    for mr in merge_requests:
        if mr["state"] == "merged":
            print("  MR Merged")
            print(f"  URL: {mr['web_url']}")
            print(f"  Merged at: {mr['merged_at']}")

            # check if the merge request was merged but the issue is still open, issue label should be QA Testing
            if issue.state == "opened":
                print(
                    f"  {Fore.YELLOW + Back.WHITE}Issue is still open{Style.RESET_ALL}"
                )
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
                    pass
                else:
                    print(
                        f"  {Fore.RED + Back.WHITE}Issue is not labeled for QA Testing{Style.RESET_ALL}"
                    )
            else:
                print(
                    f"  {Fore.GREEN + Back.WHITE}Issue state: {issue.state}{Style.RESET_ALL}"
                )
        else:
            print("  MR not merged")
            print(f"  URL: {mr['web_url']}")
            print(f"  State: {mr['state']}")

            # check if integration is in the issue label
            labels = issue.labels
            if any(
                ((label.split("::")[-1].lower() == "integration") for label in labels)
            ):
                print(
                    f"  {Fore.GREEN + Back.WHITE}Issue is labeled for Integration{Style.RESET_ALL}"
                )
                pass
            else:
                print(
                    f"  {Fore.RED + Back.WHITE}Issue is not labeled for Integration{Style.RESET_ALL}"
                )

    print("----------------------------")
