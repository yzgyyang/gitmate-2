from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Issue import Issue

from gitmate.utils import lock_igitt_object
from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.responder('issue_labeller', IssueActions.OPENED)
def add_labels_to_issue(
    issue: Issue,
    keywords: dict() = 'Keywords that trigger respective labels',
    label_texts_as_keywords: bool = 'Apply mentioned labels automatically',
):
    issue_summary = issue.title.lower() + ' ' + issue.description.lower()
    new_labels = {
        label
        for label, l_keywords in keywords.items()
        for keyword in l_keywords.split(',')
        if keyword.strip() and keyword in issue_summary
    }

    if label_texts_as_keywords:
        new_labels |= {
            label
            for label in issue.available_labels
            if label.lower() in issue_summary
        }

    with lock_igitt_object('label issue', issue):
        issue.labels = new_labels.union(issue.labels)
