import logging
from dataclasses import dataclass

from .service import BitbucketService

log = logging.getLogger(__name__)


@dataclass
class BitbucketProjects(BitbucketService):
    name: str = None
    permission: str = None

    def get_projects(self, params: dict = None) -> dict:
        params = params or {}

        if self.name:
            params['name'] = self.name
        if self.permission:
            params['permission'] = self.permission

        return self.get(path='projects', params=params)
