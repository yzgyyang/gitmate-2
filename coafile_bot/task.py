import json

from coafile_bot.utils import post_comment
from coafile_bot.utils import create_pr
from coala_online.config import COALA_ONLINE_IMAGE

from gitmate.celery import app as celery
from gitmate.utils import run_in_container
from gitmate_hooks import ExceptionLoggerTask


@celery.task(base=ExceptionLoggerTask)
def handle_thread(thread):
    """
    Handler for notification thread

    :param thread: Thread object of where coafile mention is made
    :return: coafile string
    """
    clone_url = 'https://github.com/{}/.git'.format(
        thread.data['repository']['full_name'])
    req = {'mode': 'bears', 'url': clone_url}
    response = json.loads(run_in_container(COALA_ONLINE_IMAGE,
                                           'python3', 'run.py',
                                           json.dumps(req)))
    coafile = response['coafile']
    coafile_pre = '```' + coafile + '```'
    post_comment(thread, coafile_pre)
    pr = create_pr(thread, coafile)

    if not pr:
        post_comment(
            thread, "Oops! Looks like I've already made a coafile PR!")
    else:
        completion_message = 'coafile creation process Successful! :tada: :tada: :tada:' \
            + '\n\n\n Next Steps: ' \
            + '\n\n Step 1: Merge the Pull Request ' + str(pr.data['html_url']) + ' having the .coafile.' \
            + '\n Step 2: Turn on [GitMate](https://gitmate.io) Integration on this repository.' \
            + '\n Step 3: Turn on code analysis for automated code reviews on your PRs.' \
            + '\n\n Happy Linting! :tada:'
        post_comment(thread, completion_message)
