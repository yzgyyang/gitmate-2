from os import environ
import json

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import run_in_container
from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder('rebaser', MergeRequestActions.COMMENTED)
def rebase_merge_request(pr: MergeRequest, comment: Comment):
    """
    Rebases a merge request when a user adds a rebase comment. e.g.
    ``@gitmate-bot rebase`` within the comment body.
    """
    from gitmate_config.models import Repository

    username = Repository.from_igitt_repo(pr.repository).user.username
    body = comment.body.lower()
    if '@{}'.format(username) in body and 'rebase' in body:
        pr.add_comment(
            'Hey! This pull request is being rebased automatically. Please DO '
            'NOT push while rebase is in progress or your changes would be '
            'lost!')
        head_clone_url = pr.source_repository.clone_url
        base_clone_url = pr.target_repository.clone_url
        output = run_in_container(environ['REBASER_IMAGE'],
                                  'python', 'run.py', head_clone_url,
                                  base_clone_url, pr.head_branch_name,
                                  pr.base_branch_name)
        output = json.loads(output)
        if output['status'] == 'success':
            pr.add_comment('Automated rebase was successful!')
        elif 'error' in output:
            # hiding oauth token for safeguarding user privacy
            error = output['error'].replace(head_clone_url,
                                            '<hidden_oauth_token>')
            error = error.replace(base_clone_url, '<hidden_oauth_token>')
            pr.add_comment('Automated rebase failed! Please rebase your pull '
                           'request manually via the command line.\n\nError:\n'
                           '```{}```'.format(error))
