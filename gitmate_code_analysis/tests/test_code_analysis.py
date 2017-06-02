from collections import namedtuple
import json
import subprocess
from unittest.mock import patch

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt import GitHub
from IGitt.GitHub.GitHubCommit import GitHubCommit
from rest_framework.status import HTTP_200_OK


class StreamMock:
    def __init__(self, value):
        self.value = value

    def read(self):
        return self.value.encode()

    def write(self, value):
        assert self.value == value.decode()

    def close(self):
        pass


PopenResult = namedtuple('ret', 'stdout stdin wait')


def popen_coala():
    return PopenResult(
        StreamMock('{"file_dicts": {}, "results": {}}'),
        StreamMock(''),
        lambda: None
    )


class TestCodeAnalysis(GitmateTestCase):

    BOUNCER_INPUT = '{"old_files": {}, "new_files": {}, ' \
                    '"old_results": {}, "new_results": {}}'

    def setUp(self):
        self.setUpWithPlugin('code_analysis')

        def fake_fetch_github(req_type: str, token: str, url: str,
                              data: dict = None):
            if '/commits/' in url:
                return {
                    'sha': 'deadbeef',
                }
            elif '/commits' in url:
                return [{
                    'sha': 'deadbeef',
                }]
            elif '/pulls/' in url:
                return {
                    'head': {
                        'sha': 'deadbeef',
                    },
                    'base': {
                        'sha': 'deadbeef',
                    }
                }
            else:
                return {
                    'full_name': self.repo.full_name,
                    'clone_url': 'somewhere'
                }

        self.old_fetch_github = GitHub._fetch_all_github
        GitHub._fetch_all_github = fake_fetch_github

        self.data = {
            'repository': {'full_name': self.repo.full_name},
            'pull_request': {'number': 0},
            'action': 'opened'
        }

        self.old_popen = subprocess.Popen

    def tearDown(self):
        subprocess.Popen = self.old_popen
        GitHub._fetch_all_github = self.old_fetch_github

    @patch.object(GitHubCommit, 'comment')
    def test_pr_analysis_no_issues(self, comment_mock, pr_based=False):
        self.repo.set_plugin_settings([
            {
                'name': 'code_analysis',
                'settings': {
                    'pr_based_analysis': pr_based,
                }
            }
        ])

        def popen_bouncer():
            return PopenResult(
                StreamMock('{}'),
                StreamMock(self.BOUNCER_INPUT),
                lambda: None
            )

        def fake_popen(cmd, **kwargs):
            if 'bouncer.py' in cmd:
                return popen_bouncer()

            assert 'run.py' in cmd
            return popen_coala()

        subprocess.Popen = fake_popen

        response = self.simulate_github_webhook_call('pull_request', self.data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        comment_mock.assert_not_called()

    def test_pr_analysis_no_issues_pr_based(self):
        return self.test_pr_analysis_no_issues(pr_based=True)

    @patch.object(GitHubCommit, 'comment')
    def test_pr_analysis_issues(self, comment_mock):
        def fake_popen(cmd, **kwargs):
            if 'bouncer.py' in cmd:
                return popen_bouncer()

            assert 'run.py' in cmd
            return popen_coala()

        def popen_bouncer():
            return PopenResult(
                StreamMock(
                    json.dumps({
                        'section': [
                            {
                                'message': 'a message',
                                'origin': 'I come from here',
                                'diffs': None,
                            },
                            {
                                'message': 'a message',
                                'origin': 'I come from here',
                                'affected_code': [
                                    {
                                        'start': {
                                            'file': 'filename',
                                            'line': 1
                                        }
                                    },
                                ],
                                'diffs': {
                                    'filename': 'unified diff here',
                                },
                            }
                        ]
                    })
                ),
                StreamMock(self.BOUNCER_INPUT),
                lambda: None
            )

        subprocess.Popen = fake_popen
        response = self.simulate_github_webhook_call('pull_request', self.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

        assert comment_mock.call_count == 2

    @patch.object(GitHubCommit, 'comment')
    def test_pr_analysis_many_issues(self, comment_mock):
        self.repo.set_plugin_settings([
            {
                'name': 'code_analysis',
                'settings': {
                    'pr_based_analysis': False,
                }
            }
        ])

        def fake_popen(cmd, **kwargs):
            if 'bouncer.py' in cmd:
                return popen_bouncer()

            assert 'run.py' in cmd
            return popen_coala()

        def popen_bouncer():
            return PopenResult(
                StreamMock(
                    json.dumps({
                        'too_many': [
                            {
                                'message': 'message ' + str(i),
                                'origin': 'I come from here'
                            }
                            for i in range(4)
                        ]
                    })
                ),
                StreamMock(self.BOUNCER_INPUT),
                lambda: None
            )

        subprocess.Popen = fake_popen
        response = self.simulate_github_webhook_call('pull_request', self.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

        # More than three results, one summary comment
        comment_mock.assert_called_once()