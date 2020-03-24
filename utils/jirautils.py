# coding=utf-8
import os
from jira import JIRA

from .domain import *
from .models import *

# *** JIRA ***
BASE_URL = os.getenv('_JIRA_URL')
LOGIN = os.getenv('_JIRA_LOGIN')
PASSWORD = os.getenv('_JIRA_PASSWORD')


def create_issues_link(ids):
    quary = ",".join(map(str, [i for i in ids if i] ))
    return "https://devjira.skyeng.ru/issues/?jql=issue in ({})".format(quary)


def fill_report_stub(git_raw):
    row = []
    for raw in git_raw:
        row.append(ReportItem(raw.id, raw.comment, TASK_TYPE_OTHER))

    # row.append(ReportItem("MP-1", "Merge pull request #1377 from skyeng/adults/lea/MOB-7021", TASK_TYPE_OTHER))
    # row.append(ReportItem("MP-3", "tmp", TASK_TYPE_OTHER))
    # row.append(ReportItem("MP-2", "Merge pull request #1362 from skyeng/adults/lea/MP-183", TASK_TYPE_OTHER))
    # row.append(ReportItem("MP-4", "TASK_TYPE_BUG 1", TASK_TYPE_BUG))
    # row.append(ReportItem("MP-5", "TASK_TYPE_REFACTOR", TASK_TYPE_REFACTOR))
    # row.append(ReportItem("MP-6", "TASK_TYPE_REFACTOR 2", TASK_TYPE_REFACTOR))
    # row.append(ReportItem("MP-7", "TASK_TYPE_TASK", TASK_TYPE_TASK))

    row2 = []
    for item in row:
        if is_valid_git_comment(item.summary, item.issuetype):
            row2.append(item)

    return row2


def fill_report(issues_id):
    jira_options = {'server': BASE_URL}
    jira = JIRA(options=jira_options, basic_auth=(LOGIN, PASSWORD))

    row = []
    for raw in issues_id:
        id = raw.id
        try:
            issue = jira.issue(id)

            type = type_as_emoji(issue.fields.issuetype)
            summary = __get_summery(type, raw, issue)

            if is_valid_git_comment(summary, type):
                row.append(ReportItem(id, summary, type))

        except Exception as e:
            if is_valid_git_comment(raw.comment, TASK_TYPE_OTHER):
                row.append(ReportItem(id, raw.comment, TASK_TYPE_OTHER))

    return row

    #
    # issue = jira.issue("MP-324")
    # print(issue.fields.status)
    # print(issue.fields.issuetype)


def __get_summery(type, raw, issue):
    comment = ""
    if type == TASK_TYPE_OTHER:
        comment = raw.comment
    else:
        comment = issue.fields.summary

    return filter_git_comment(comment).strip()
