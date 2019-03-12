import mock
import pytest
from bitbucket import constants
from bitbucket.commits import BitbucketCommits
from bitbucket.exceptions import BitbucketBaseAPIException, NoTagsCouldBeFetchedException
from rest_framework.exceptions import APIException


class TestBitbucketRepos:
    def test_get_request_params(self):
        bitbucket_service = BitbucketCommits(
            credentials_provider=mock.Mock(), limit=2, start=4, include_counts=False
        )

        assert bitbucket_service._get_request_params(params={'limit': 1}) == {
            'limit': 1,
            'start': 4,
            'includeCounts': False,
        }

    @mock.patch('bitbucket.commits.BitbucketCommits._enrich_commit_history_with_tags')
    @mock.patch('bitbucket.service.BitbucketService.get')
    def test_get_commits(self, mock_get_request, mock_commits_enrichment):
        mock_get_request.return_value = {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ]
        }

        repos_service = BitbucketCommits(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            since='7c3d7a55b847f234249936c229bd974626b08a99', merges=constants.MERGE_ONLY
        )

        assert repos_service.get_commits() == {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ]
        }  # asserting that tags are not added
        mock_get_request.assert_called_once_with(
            params={'merges': 'only'},
            path='projects/the_wasp/repos/winsome/commits'
        )
        mock_commits_enrichment.assert_not_called()

    @mock.patch('bitbucket.service.BitbucketService.get')
    def test_get_commits_with_exception(self, mock_get_request):
        mock_get_request.side_effect = BitbucketBaseAPIException
        repos_service = BitbucketCommits(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            since='7c3d7a55b847f234249936c229bd974626b08a99', merges=constants.MERGE_INCLUDE
        )

        with pytest.raises(BitbucketBaseAPIException):
            repos_service.get_commits()

    @mock.patch('bitbucket.commits.BitbucketCommits._enrich_commit_history_with_tags')
    @mock.patch('bitbucket.service.BitbucketService.get')
    def test_get_commits_tags_enriched(self, mock_get_request, mock_commits_enrichment):
        mock_get_request.return_value = {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ]
        }
        mock_commits_enrichment.return_value = [
            {'id': 'some_id', 'tags': ['1.0.0', '2.0.0']},
            {'id': 'some_id2', 'tags': []}
        ]

        repos_service = BitbucketCommits(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            since='7c3d7a55b847f234249936c229bd974626b08a99', merges=constants.MERGE_ONLY, include_tags=True
        )

        assert repos_service.get_commits() == {
            'values': [
                {'id': 'some_id', 'tags': ['1.0.0', '2.0.0']},
                {'id': 'some_id2', 'tags': []}
            ]
        }
        mock_commits_enrichment.assert_called_once()

    @mock.patch('bitbucket.commits.BitbucketCommits._enrich_commit_history_with_tags')
    @mock.patch('bitbucket.service.BitbucketService.get')
    def test_get_commits_enriched_with_exception(self, mock_get_request, mock_commits_enrichment):
        """ Tests if no exception is thrown when NoTagsCouldBeFetchedException is raised fetching tags """
        mock_get_request.return_value = {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ]
        }
        mock_commits_enrichment.side_effect = NoTagsCouldBeFetchedException
        repos_service = BitbucketCommits(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            since='7c3d7a55b847f234249936c229bd974626b08a99', merges=constants.MERGE_ONLY, include_tags=True
        )
        assert repos_service.get_commits() == {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ],
            'message': constants.RESPONSE_ERROR_FETCHING_TAGS
        }  # asserting that tags are not added
        mock_get_request.assert_called_once_with(
            params={'merges': 'only'},
            path='projects/the_wasp/repos/winsome/commits'
        )
        mock_commits_enrichment.assert_called_once()

    @mock.patch('bitbucket.commits.BitbucketCommits._enrich_commit_history_with_tags')
    @mock.patch('bitbucket.service.BitbucketService.get')
    def test_get_commits_enriched_with_exception_thrown(self, mock_get_request, mock_commits_enrichment):
        """
        Tests if an exception is thrown when an exception different from
        NoTagsCouldBeFetchedException is raised fetching tags
        """
        mock_get_request.return_value = {
            'values': [
                {'id': 'some_id'},
                {'id': 'some_id2', 'tags': []}
            ]
        }
        mock_commits_enrichment.side_effect = Exception
        repos_service = BitbucketCommits(
            credentials_provider=mock.Mock(), project_key='the_wasp', repository_name='winsome',
            since='7c3d7a55b847f234249936c229bd974626b08a99', merges=constants.MERGE_ONLY, include_tags=True
        )

        with pytest.raises(Exception):
            repos_service.get_commits()

    @pytest.mark.parametrize(
        'commits, tags, expected_commits',
        (
            ([], {}, []),
            (
                [{'id': 'some_id'}, {'id': 'some_id2', 'tags': []}, {'id': 'some_id3'}],  # commits
                {
                    'values': [
                        {'latestCommit': 'some_id', 'displayId': '1.0.0'},
                        {'latestCommit': 'some_id', 'displayId': '2.0.0'},
                        {'latestCommit': 'some_id2', 'displayId': '0.0.0'},
                        {'latestCommit': 'some_id_no_commit', 'displayId': '0.0.1'}
                    ]
                },  # tags
                [
                    {'id': 'some_id', 'tags': ['1.0.0', '2.0.0']},
                    {'id': 'some_id2', 'tags': ['0.0.0']},
                    {'id': 'some_id3', 'tags': []}
                ]  # expected_commits
            ),
            (
                [{'id': 'some_id'}, {'id': 'some_id2', 'tags': []}, {'id': 'some_id3'}],  # commits
                {},  # tags
                [
                    {'id': 'some_id'},
                    {'id': 'some_id2', 'tags': []},
                    {'id': 'some_id3'}
                ]  # expected_commits
            ),
        )
    )
    @mock.patch('bitbucket.commits.BitbucketTags.get_tags')
    def test_enrich_commit_history_with_tags(self, mock_get_tags, commits, tags, expected_commits):
        mock_get_tags.return_value = tags

        bitbucket_service = BitbucketCommits()

        assert list(bitbucket_service._enrich_commit_history_with_tags(commits)) == expected_commits

    @pytest.mark.parametrize(
        'exception, expected_thrown_exception',
        (
            (APIException, NoTagsCouldBeFetchedException),
            (BitbucketBaseAPIException, NoTagsCouldBeFetchedException),
            (IOError, IOError),  # any other type of exceptions different from APIException
        )
    )
    @mock.patch('bitbucket.commits.BitbucketTags.get_tags')
    def test_enrich_commit_history_with_tags_exception(self, mock_get_tags, exception, expected_thrown_exception):
        mock_get_tags.side_effect = exception

        bitbucket_service = BitbucketCommits()

        with pytest.raises(expected_thrown_exception):
            bitbucket_service._enrich_commit_history_with_tags(
                commits=[{'id': 'some_id'}, {'id': 'some_id2', 'tags': []}, {'id': 'some_id3'}]
            )
