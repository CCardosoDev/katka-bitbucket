import logging
from dataclasses import dataclass

from .service import BitbucketService

log = logging.getLogger(__name__)


@dataclass
class BitbucketRepos(BitbucketService):
    project_key: str = None

    def get_repos(self, params: dict = None) -> dict:
        path = f'projects/{self.project_key}/repos'

        return self.get(path=path, params=params)
