from bitbucket.fields import KatkaDateTimeField
from rest_framework import serializers

from . import constants
from .conf import settings


class BitbucketRequest(serializers.Serializer):
    credential = serializers.UUIDField(required=False)  # the credential id used to fetch the actual credential value
    base_url = serializers.URLField(required=False,
                                    default=settings.DEFAULT_BITBUCKET_SERVICE_LOCATION)  # the bitbucket base url
    start = serializers.IntegerField(min_value=0, required=False)  # first element index of the response list
    limit = serializers.IntegerField(min_value=0, required=False)  # max number of elements to be retrieved


class BitbucketResponse(serializers.Serializer):
    start = serializers.IntegerField(required=False)  # first element index of the response list
    limit = serializers.IntegerField(required=False)  # max number of elements to be retrieved
    size = serializers.IntegerField(required=False)  # the number of retrieved elements
    is_last_page = serializers.BooleanField(required=False, source='isLastPage')
    next_page_start = serializers.IntegerField(
        required=False, source='nextPageStart'
    )  # the index of the first element of the next page
    message = serializers.CharField(required=False, default=constants.RESPONSE_OK)


# Projects

class BitbucketProjectsRequest(BitbucketRequest):
    name_filter = serializers.CharField(required=False)  # filter for project name
    permission = serializers.ChoiceField(required=False, choices=constants.BITBUCKET_PROJECT_PERMISSIONS,
                                         default=constants.PROJECT_READ)


class BitbucketProjectDetails(serializers.Serializer):
    key = serializers.CharField(required=False)  # example AT (for a project named Atlassian)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)


class BitbucketProjectsResponse(BitbucketResponse):
    values = serializers.ListField(child=BitbucketProjectDetails(), required=False, default=list())


# Repos

class BitbucketReposRequest(BitbucketRequest):
    project_key = serializers.CharField(required=True, allow_null=False, allow_blank=False)


class BitbucketRepoDetails(serializers.Serializer):
    slug = serializers.CharField(required=False)
    name = serializers.CharField(required=False)


class BitbucketReposResponse(BitbucketResponse):
    values = serializers.ListField(child=BitbucketRepoDetails(), required=False, default=list())


# Commits

class BitbucketCommitsRequest(BitbucketRequest):
    project_key = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    repository_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    merges = serializers.ChoiceField(
        required=False, choices=constants.BITBUCKET_MERGES_CONTROL
    )  # if present, controls how merge commits should be filtered. Can be either exclude,
    # to exclude merge commits, include, to include both merge commits and non-merge
    # #commits or only, to only return merge commits.
    since = serializers.CharField(
        required=False, allow_null=False, allow_blank=False
    )  # the commit ID or ref (exclusively) to retrieve commits after
    until = serializers.CharField(
        required=False, allow_null=False, allow_blank=False
    )  # the commit ID or ref (inclusively) to retrieve commits before
    include_counts = serializers.BooleanField(
        required=False
    )  # optionally include the total number of commits and total number of unique authors
    include_tags = serializers.BooleanField(
        required=False, default=False
    )  # optionally include tags on commits history


class Author(serializers.Serializer):
    name = serializers.CharField(required=False)
    slug = serializers.CharField(required=False)
    display_name = serializers.CharField(required=False, source='displayName')
    email_address = serializers.EmailField(required=False, source='emailAddress')


class BitbucketCommitDetails(serializers.Serializer):
    id = serializers.CharField(required=False)  # the commit ID (SHA1)
    display_id = serializers.CharField(required=False, source='displayId')
    date = KatkaDateTimeField(required=False, source='committerTimestamp')
    message = serializers.CharField(required=False)
    author = Author(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list())


class BitbucketCommitsResponse(BitbucketResponse):
    values = serializers.ListField(child=BitbucketCommitDetails(), required=False, default=list())
