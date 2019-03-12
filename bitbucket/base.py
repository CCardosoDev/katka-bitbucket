from dataclasses import dataclass

import requests
from bitbucket.exceptions import http_request_exception_to_api


@dataclass
class KatkaService:
    bearer_token: str = None  # the bearer token to be used on Authorization header

    @property
    def client(self) -> requests.sessions.Session:
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'katka',
        })

        # add bearer token if it exists
        if self.bearer_token:
            session.headers['Authorization'] = f'Bearer {self.bearer_token}'

        return session

    def get(self, url: str, params: dict = None) -> requests.models.Response:
        """
        Sends a http GET request handling the exceptions.

        Args:
            url(str): the url to send the request to.
            params(dict): the get request params.

        Returns:
            requests.models.Response: The response to the http GET request.

        Raises:
            BitbucketBaseAPIException: in case there is any expected exception.
        """
        with http_request_exception_to_api():
            return self.client.get(url, params=params)
