import re
import gitlab
from colorama import Fore, Back, Style
import json


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
        issue = project_obj.issues.get(issue_id)
        issues.append(issue)
    return issues


def get_milestone_from_issues(issues):
    milestones = []
    for issue in issues:
        milestone = issue.milestone
        if milestone:
            milestones.append(
                milestone.get("title")
            )  # only get the title (1.0.26 etc.)
    return milestones


config = load_config()
PAT = config["PAT"]
gl = gitlab.Gitlab(private_token=PAT)
gl.auth()

# load the project
project_id = config["project_id"]
project_obj = gl.projects.get(project_id)
show_only_1_approval = True
show_all = True
show_drafts = False
store_1_approval = True
store = {}

print("Project: %s" % project_obj.name)

all_user_mrs = project_obj.mergerequests.list(
    state="opened", order_by="updated_at", get_all=True
)

for mr in all_user_mrs:
    mr_user = mr.author
    mr_title = mr.title

    if "sow" in mr_title.lower():
        continue  # skip SOWs

    # check if the MR has any approvals
    approvals = [approval["user"] for approval in mr.approvals.get().approved_by]
    if show_drafts or not mr.work_in_progress:
        print(f"MR: {mr.title}")
        print(f"URL: {mr.web_url}")
        print(f"author: {mr_user['name']}")
    # check if MR is draft
    if mr.work_in_progress and show_drafts:
        print(f"  {Fore.BLUE + Back.WHITE}Draft MR{Style.RESET_ALL}")
        continue

    milestone = mr.milestone.get("title") if mr.milestone else None
    issue_milestone = None
    issues = get_issues_from_ids(find_issue_ids_from_desc(mr.description))
    milestone_from_issue = get_milestone_from_issues(issues)
    if len(milestone_from_issue) > 0:
        issue_milestone = milestone_from_issue[0]

    if milestone is None or issue_milestone is None:
        # show warning if milestone is not set in Mr or issue
        if not milestone:
            print(f"  {Fore.RED + Back.WHITE}No milestone set [MR]{Style.RESET_ALL}")
        if not issue_milestone:
            print(f"  {Fore.RED + Back.WHITE}No milestone set [Issue]{Style.RESET_ALL}")
    else:
        if milestone != issue_milestone:
            print(f"  {Fore.RED + Back.WHITE}Milestone mismatch{Style.RESET_ALL}")
            print(f"  MR: {milestone}")
            print(f"  Issue: {issue_milestone}")

        else:
            print(f"  {Fore.GREEN + Back.WHITE}Milestone OK{Style.RESET_ALL}")
            print(f"  MR: {milestone}")
            print(f"  Issue: {issue_milestone}")

    print("\t-----MILESTONE CHECK DONE-----\n")

    if len(approvals) == 0:
        if show_all:
            print(
                f"{mr_title}\n  {Fore.RED + Back.WHITE}No approvals found{Style.RESET_ALL}"
            )
    elif len(approvals) == 1:
        if store_1_approval:
            store[mr_title] = mr.web_url
        if show_all or show_only_1_approval:
            print(
                f"  {Fore.YELLOW + Back.WHITE}Only one approval found{Style.RESET_ALL}"
            )
    else:
        if show_all:
            print(
                f"  {Fore.GREEN + Back.WHITE}All good, approved by: {len(approvals)}{Style.RESET_ALL}"
            )
    # approved by
    for approval in approvals:
        print(f"    {approval['name']}")
    print("-------------------------------------------------")
# Path: check_approves.py

if store_1_approval:
    with open(".dump/store.json", "w") as f:
        json.dump(store, f, indent=4)
