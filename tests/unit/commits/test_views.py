from django.urls import reverse

import mock
from bitbucket import constants
from bitbucket.exceptions import ProjectNotFoundAPIException


class TestGetBitbucketCommitsView:
    @mock.patch('bitbucket.views.BitbucketCommits')
    def test_get_existing_projects(self, mock_bitbucket_commits, client, settings):
        settings.TIME_ZONE = 'UTC'
        result = mock.Mock()
        result.get_commits.return_value = {
            'start': 0,
            'limit': 15,
            'size': 1,
            'isLastPage': True,
            'nextPageStart': 1,
            'values': [
                {
                    'id': '891aaefc6de4f83334c3d2630fc80f928a142630',
                    'displayId': '891aaefc6de',
                    'message': 'Some commit message',
                    'committerTimestamp': 1540213395000,
                    'author': {
                        'emailAddress': 'captain.america@kpn.com',
                        'name': 'captain.america@kpn.com',
                        'slug': 'cc501',
                        'displayName': 'America, Captain'
                    }
                }
            ],
            'some_not_valid_param': 'some_not_important_value'
        }
        mock_bitbucket_commits.return_value = result

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_woman'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={
                'credential': 'bead677e-c414-4954-85eb-67ef09ca99f7',
                'limit': 10, 'start': 2
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'start': 0,
            'limit': 15,
            'size': 1,
            'is_last_page': True,
            'next_page_start': 1,
            'values': [
                {
                    'id': '891aaefc6de4f83334c3d2630fc80f928a142630',
                    'display_id': '891aaefc6de',
                    'message': 'Some commit message',
                    'date': '2018-10-22T13:03:15Z',
                    'author': {
                        'email_address': 'captain.america@kpn.com',
                        'name': 'captain.america@kpn.com',
                        'slug': 'cc501',
                        'display_name': 'America, Captain'
                    },
                    'tags': []
                }
            ],
            'message': constants.RESPONSE_OK
        }

    @mock.patch('bitbucket.views.BitbucketCommits')
    def test_empty_commits_list(self, mock_bitbucket_commits, client):
        result = mock.Mock()
        result.get_commits.return_value = {}
        mock_bitbucket_commits.return_value = result

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_commits'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'credential': 'bead677e-c414-4954-85eb-67ef09ca99f7'}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0
        assert response.data.get('start') is None

    @mock.patch('bitbucket.views.BitbucketCommits')
    def test_bitbucket_project_not_found(self, mock_bitbucket_commits, client):
        result = mock.Mock()
        result.get_commits.side_effect = ProjectNotFoundAPIException
        mock_bitbucket_commits.return_value = result

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_woman'})
        response = client.get(
            endpoint,
            content_type='application/json'
        )

        assert response.status_code == 404
