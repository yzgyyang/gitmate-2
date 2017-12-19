from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabUser import GitLabUser


class TestIssuePRSync(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_pr_sync')
        self.gh_user = GitHubUser(self.repo.token, 'gitmate-test-user')
        self.gh_user_2 = GitHubUser(self.repo.token, 'gitmate-test-user-2')
        self.gl_user = GitLabUser(self.gl_repo.token, 1)
        self.gl_user_2 = GitLabUser(self.gl_repo.token, 2)

    @patch.object(GitHubMergeRequest, 'assignees', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'closes_issues',
                  new_callable=PropertyMock)
    def test_github_fresh_pr_with_issues(
            self, m_cl_iss, m_labels, m_assignees
    ):
        # setting the assignees & labels
        m_cl_iss.return_value = {
            GitHubIssue(self.repo.token, self.repo.full_name, 0)}
        GitHubIssue.labels = {'a', 'b'}
        m_labels.return_value = set()
        GitHubIssue.assignees = {self.gh_user}
        m_assignees.return_value = set()

        # testing updated pull requests
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 110},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called_with({'a', 'b'})
        m_assignees.assert_called_with({self.gh_user})

        # testing updated issue assignees
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'issue': {'number': 0},
            'action': 'updated'
        }
        GitHubIssue.assignees = {self.gh_user_2}
        m_assignees.return_value = {self.gh_user}

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_assignees.assert_called_with({self.gh_user, self.gh_user_2})

        # testing LABELED event
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'issue': {'number': 0},
            'action': 'labeled',
            'label': {'name': 'type/bug'}
        }
        m_labels.return_value = set()
        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_labels.assert_called_with({'type/bug'})

        # testing UNLABELED event
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'issue': {'number': 0},
            'action': 'unlabeled',
            'label': {'name': 'type/bug'}
        }
        m_labels.return_value = {'type/bug', 'good first issue'}
        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_labels.assert_called_with({'good first issue'})


    @patch.object(GitLabMergeRequest, 'assignees', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'closes_issues',
                  new_callable=PropertyMock)
    def test_gitlab_fresh_pr_with_issues(
            self, m_cl_iss, m_labels, m_assignees
    ):
        # setting the assignees & labels
        m_cl_iss.return_value = {
            GitLabIssue(self.gl_repo.token, self.gl_repo.full_name, 0)}
        GitLabIssue.labels = {'a', 'b'}
        m_labels.return_value = set()
        GitLabIssue.assignees = {self.gl_user}
        m_assignees.return_value = set()

        # testing updated pull requests
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 25
            }
        }
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called_with({'a', 'b'})
        m_assignees.assert_called_with({self.gl_user})

        # testing updated issue assignees
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'iid': 0
            },
            'changes': []
        }
        GitLabIssue.assignees = {self.gl_user_2}
        m_assignees.return_value = {self.gl_user}

        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_assignees.assert_called_with({self.gl_user, self.gl_user_2})

        # testing LABELED event
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'iid': 0
            },
            'changes': {
                'labels': {
                    'previous': [],
                    'current': [{'title': 'type/bug'}]
                }
            }
        }
        m_labels.return_value = set()
        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_labels.assert_called_with({'type/bug'})

        # testing UNLABELED event
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'iid': 0
            },
            'changes': {
                'labels': {
                    'previous': [{'title': 'type/bug'}, {'title': 'first'}],
                    'current': [{'title': 'first'}]
                }
            }
        }
        m_labels.return_value = {'type/bug', 'first'}
        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_labels.assert_called_with({'first'})
