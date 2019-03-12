from django.urls import reverse

import mock
from bitbucket.exceptions import BitbucketBaseAPIException
from requests import HTTPError
from rest_framework.exceptions import PermissionDenied


@mock.patch('bitbucket.commits.BitbucketCommits.get')
@mock.patch('bitbucket.credentials.KatkaCredentialsService.client')
class TestGetCommits:
    @mock.patch('bitbucket.tags.BitbucketTags.get')
    def test_existing_commits(self, mock_bitbucket_tags_request, mock_credentials_client,
                              mock_bitbucket_commits_request, load_json_fixture, client, settings):
        settings.TIME_ZONE = 'CET'
        mock_credentials_client.return_value = mock.PropertyMock()
        credentials_response = mock.Mock()
        credentials_response.json.return_value = load_json_fixture('katka_credentials.json')
        mock_credentials_client.get.return_value = credentials_response

        mock_bitbucket_commits_request.return_value = load_json_fixture('bitbucket_commits.json')

        mock_bitbucket_tags_request.return_value = load_json_fixture('bitbucket_tags.json')

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_woman'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={
                'credential': '3617e084-950c-4a44-aa6d-b4aeba1db428',
                'limit': 10, 'start': 2, 'merges': 'INCLUDE', 'include_tags': True
            }
        )
        response = response.json()

        assert len(response['values']) == 2
        assert response['values'][0]['author']['slug'] == 'ca501'
        assert response['values'][0]['author']['display_name'] == 'America, Captain'
        assert response['values'][0]['tags'] == ['0.14.1', '0.14.0']
        assert response['values'][1]['author']['name'] == 'Spider Man'
        assert response['values'][1]['author']['email_address'] == 'spider.man@gmail.com'
        assert response['values'][1]['id'] == '3a905ec92162dd4ba45c6eaaa6027febf51a5ee9'
        assert response['values'][1]['display_id'] == '3a905ec9216'
        assert response['values'][1]['date'] == '2019-02-04T11:21:27+01:00'
        assert len(response['values'][1]['tags']) == 0

    def test_no_commits(self, mock_credentials_client, mock_bitbucket_commits_request, load_json_fixture, client):
        mock_credentials_client.return_value = mock.PropertyMock()
        credentials_response = mock.Mock()
        credentials_response.json.return_value = load_json_fixture('katka_credentials.json')
        mock_credentials_client.get.return_value = credentials_response

        mock_bitbucket_commits_request.return_value = load_json_fixture('bitbucket_no_commits.json')

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_commits'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'credential': '3617e084-950c-4a44-aa6d-b4aeba1db428', 'limit': 10, 'start': 2}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0
        assert response.data['start'] == 0
        assert response.data['limit'] == 0
        assert response.data['size'] == 0
        assert response.data['is_last_page'] is True
        assert response.data['next_page_start'] == 0

    def test_bitbucket_exception(self, mock_credentials_client, mock_bitbucket_commits_request,
                                 load_json_fixture, client):
        """ If the token is not valid bitbucket will retrieve an empty list of projects """
        mock_credentials_client.return_value = mock.PropertyMock()
        credentials_response = mock.Mock()
        credentials_response.json.return_value = load_json_fixture('katka_credentials.json')
        mock_credentials_client.get.return_value = credentials_response

        mock_bitbucket_commits_request.side_effect = BitbucketBaseAPIException()

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_woman'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'credential': '4cb432f5-0def-48b6-ad05-f1c082b1f1b9', 'limit': 10, 'start': 2}
        )

        assert response.status_code == BitbucketBaseAPIException.status_code


class TestGetProjectsNoCredentials:
    @mock.patch('requests.sessions.Session.request')
    def test_no_credential(self, mock_bitbucket_request, load_json_fixture, client):
        bitbucket_response = mock.Mock()
        bitbucket_response.json.return_value = load_json_fixture('bitbucket_no_commits.json')
        mock_bitbucket_request.return_value = bitbucket_response

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_commits'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'limit': 10, 'start': 2}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0

    @mock.patch('bitbucket.credentials.KatkaCredentialsService.client')
    def test_no_credential_found(self, mock_credentials_client, load_json_fixture, client):
        mock_credentials_client.return_value = mock.PropertyMock()
        credentials_response = mock.Mock()
        credentials_response.raise_for_status.side_effect = HTTPError(
            'test exception', response=mock.Mock(content=None, status_code=404)
        )
        mock_credentials_client.get.return_value = credentials_response

        endpoint = reverse('commits', kwargs={'project_key': 'msap', 'repository_name': 'invisible_woman'})
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'credential': '4cb432f5-0def-48b6-ad05-f1c082b1f1b9', 'limit': 10, 'start': 2}
        )

        assert response.status_code == PermissionDenied.status_code
