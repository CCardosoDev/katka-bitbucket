from dataclasses import dataclass

from .service import BitbucketService


@dataclass
class BitbucketTags(BitbucketService):
    project_key: str = None
    repository_name: str = None

    filter_text: str = None
    order_by: str = None  # default is MODIFICATION (last update)

    SERVICE_KEY_MAP = BitbucketService.SERVICE_KEY_MAP + (
        ('filter_text', 'filterText'),
        ('order_by', 'orderBy')
    )

    def get_tags(self, params: dict = None) -> dict:
        path = f'projects/{self.project_key}/repos/{self.repository_name}/tags'

        return self.get(path=path, params=params)
