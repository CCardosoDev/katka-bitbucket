from dataclasses import dataclass

from rest_framework.exceptions import APIException

from . import constants
from .exceptions import NoTagsCouldBeFetchedException
from .service import BitbucketService
from .tags import BitbucketTags


@dataclass
class BitbucketCommits(BitbucketService):
    tags_provider: BitbucketTags = None

    project_key: str = None
    repository_name: str = None

    merges: str = None
    since: str = None
    until: str = None
    include_counts: bool = None
    include_tags: bool = False

    SERVICE_KEY_MAP = BitbucketService.SERVICE_KEY_MAP + (
        ('merges', 'merges'),
        ('since', 'since'),
        ('until', 'until'),
        ('include_counts', 'includeCounts'),
    )

    def __post_init__(self):
        self.tags_provider = self.tags_provider or BitbucketTags(
            start=self.start,
            limit=self.limit or constants.DEFAULT_COMMIT_HISTORY_TAGS_LIMIT,
            project_key=self.project_key,
            repository_name=self.repository_name,
        )
        super().__post_init__()

    def _enrich_commit_history_with_tags(self, commits: list = ()):
        """
        Enriches the commit history with respective tags.

        Args:
            commits: raw commits list

        Returns:
            list: the tags enriched list of commits

        Raises:
            NoTagsCouldBeFetchedException: if an error occurs while fetching tags
        """
        if not commits:
            return commits

        try:
            tags = self.tags_provider.get_tags()
        except APIException:
            raise NoTagsCouldBeFetchedException()

        if not tags or not tags.get('values'):
            return commits

        # index commits by it's hash
        hash_commits = {}
        for commit in commits:
            commit['tags'] = []
            hash_commits[commit['id']] = commit

        # enrich commits with tags
        for tag in tags['values']:
            commit = hash_commits.get(tag['latestCommit'])

            if not commit:
                continue

            commit['tags'].append(tag.get('displayId'))

        return hash_commits.values()

    def get_commits(self) -> dict:
        path = f'projects/{self.project_key}/repos/{self.repository_name}/commits'

        # translate service specific request params value
        merges = constants.BITBUCKET_MERGES_CONTROL_SERVICE_MAP.get(self.merges) if self.merges else None

        commits = self.get(path=path, params={'merges': merges})

        if not self.include_tags or not commits or not commits.get('values'):
            return commits

        try:
            commits['values'] = self._enrich_commit_history_with_tags(commits['values'])
        except NoTagsCouldBeFetchedException as ex:
            commits['message'] = ex.code

        return commits
