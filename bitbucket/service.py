import logging
from dataclasses import asdict, dataclass

from .base import KatkaService
from .conf import settings
from .credentials import CredentialsProvider
from .exceptions import bitbucket_service_exception_to_api

log = logging.getLogger(__name__)


@dataclass
class BitbucketService(KatkaService):
    credentials_provider: CredentialsProvider = None
    base_url: str = None

    start: int = None
    limit: int = None

    SERVICE_KEY_MAP = (
        ('start', 'start'),
        ('limit', 'limit'),
    )

    def __post_init__(self):
        """
        Raises:
            bitbucket.models.KatkaProject.DoesNotExist: in case the given id for the katka project does not exist
        """
        self.base_url = self.base_url or settings.DEFAULT_BITBUCKET_SERVICE_LOCATION
        self.base_url = self.base_url.rstrip('/')
        self.base_path = 'rest/api/1.0'
        self.bearer_token = self.credentials_provider.access_token if self.credentials_provider else None

    def _get_request_params(self, params: dict = None) -> dict:
        """
        Translates not None params (request specific and class instance params) to
        downstream (bitbucket service) request params. Noting that `params` has precedence over instance attributes in
        case the same param is in both.

        Args:
            params(dict): the request specific params

        Returns:
            dict: the final request params with keys translated to service specific names
        """
        request_params = {}
        raw_request_params = asdict(self)

        if params:
            raw_request_params.update(params)

        for original_key, service_key in self.SERVICE_KEY_MAP:
            if raw_request_params.get(original_key) is not None:
                request_params[service_key] = raw_request_params[original_key]

        return request_params

    def get(self, path: str = '', params: dict = None) -> dict:
        """
        HTTP GET request

        Args:
            path(str): the specific path to get the resource from
            params(dict): the params for query string

        Returns:
            dict: the http response body

        Raises:
            requests.exceptions.HTTPError: in case there is a HTTP error during the request

        Notes:
            `params` has precedence over instance attributes in case the same param is in both.
        """
        url = f'{self.base_url}/{self.base_path}/{path}'
        resp = super().get(url, params=self._get_request_params(params))

        with bitbucket_service_exception_to_api():
            resp.raise_for_status()
            return resp.json()
