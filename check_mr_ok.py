import json
import re
import sys
from typing import List

import gitlab
from colorama import Fore, Back, Style

__inner_separator_string = "---" * 10
__outer_separator_string = "---" * 20


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def check_label_string(label_string: str, to_check: str):
    """
    Check if label string is equal to to_check
    Args:
        label_string: gitlab issue label string
        to_check: to check with required label string

    Returns:
        True if label string is equal to to_check
    """
    if "::" not in label_string:
        return label_string.lower() == to_check.lower()
    return label_string.split("::")[-1].lower() == to_check.lower()


def contains_label_string(label_list: List[str], to_check: str):
    """
    Check if label list contains label string
    Args:
        label_list: gitlab issue label list
        to_check: to check with required label string

    Returns:
        True if label list contains label string
    """
    return any((check_label_string(label, to_check) for label in label_list))


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


def needs_draft_color(mr):
    if mr.work_in_progress:
        return Fore.YELLOW + Back.WHITE
    return ""


def get_approvals_from_mr(merge_request) -> List[str]:
    approvals = [approval["user"] for approval in merge_request.approvals.get().approved_by]
    return approvals


config = load_config()
PAT = config["PAT"]
gl = gitlab.Gitlab(private_token=PAT)
gl.auth()

# load the project
project_id = config["project_id"]
project_obj = gl.projects.get(project_id)

print("Project: %s" % project_obj.name)

# get all mr created by the user
user_name = sys.argv[1]

# get the user
user = gl.users.list(username=user_name)[0]
print(f"User: {user.name}")
user_id = user.id


def find_all_user_mrs():
    merge_requests = project_obj.mergerequests.list(
        author_id=user_id, state="opened", get_all=True
    )
    return merge_requests


def main() -> None:
    # get all merge requests created by the user
    merge_requests = find_all_user_mrs()  # function takes user_id from global scope

    # find all merge requests that have related issues
    for mr in merge_requests:
        print(f"MR: {needs_draft_color(mr)}{mr.title}{Style.RESET_ALL}")
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
                    if contains_label_string(labels, "qa testing"):
                        print(
                            f"  {Fore.GREEN + Back.WHITE}Issue is labeled for QA Testing{Style.RESET_ALL}"
                        )
                else:
                    print(f"  {Fore.YELLOW + Back.WHITE}MR is not merged{Style.RESET_ALL}")

                    approvers = get_approvals_from_mr(mr)

                    milestone_string = f"{Fore.RED + Back.WHITE}No milestone found{Style.RESET_ALL}"
                    if mr.milestone:
                        milestone_string = mr.milestone.get('title')

                    print(f"  Milestone: {milestone_string}")
                    print(f"  Approver(s): {len(approvers)}")
                    if len(approvers) == 0:
                        print(
                            f"  {Fore.RED + Back.WHITE}No approves found{Style.RESET_ALL}"
                        )
                    else:
                        for approver in approvers:
                            print(f"\t{approver}")

                    # check if issue is labeled for integration
                    labels = issue.labels
                    if contains_label_string(labels, "integration"):
                        print(
                            f"  {Fore.GREEN + Back.WHITE}Issue is labeled for Integration{Style.RESET_ALL}"
                        )
                    else:
                        print(
                            f"  {Fore.RED + Back.WHITE}Issue is not labeled for Integration{Style.RESET_ALL}"
                        )

            print(__inner_separator_string.center(60))  # separator

        print(__outer_separator_string.center(60, '-'))  # separator


if __name__ == '__main__':
    main()
