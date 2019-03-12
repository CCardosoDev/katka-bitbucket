import mock
import pytest
from bitbucket.exceptions import BitbucketBaseAPIException
from bitbucket.tags import BitbucketTags


class TestBitbucketTags:

    @mock.patch('bitbucket.tags.BitbucketService.get')
    def test_get_tags(self, mock_service_response):
        mock_service_response.return_value = {
            'values': []
        }

        assert BitbucketTags().get_tags()['values'] == []

    @mock.patch('bitbucket.tags.BitbucketService.get')
    def test_get_tags_with_exception(self, mock_get_request):
        mock_get_request.side_effect = BitbucketBaseAPIException
        repos_service = BitbucketTags(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            filter_text='filter_me'
        )
        with pytest.raises(BitbucketBaseAPIException):
            repos_service.get_tags()

    def test_get_request_params(self):
        bitbucket_service = BitbucketTags(
            credentials_provider=mock.Mock(), limit=2, start=4, filter_text='filter_it', order_by='MODIFICATION'
        )

        assert bitbucket_service._get_request_params(params={'limit': 1}) == {
            'limit': 1,
            'start': 4,
            'filterText': 'filter_it',
            'orderBy': 'MODIFICATION'
        }
