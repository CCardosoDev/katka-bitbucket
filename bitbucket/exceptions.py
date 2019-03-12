import logging
from contextlib import contextmanager
from json import JSONDecodeError

from requests import HTTPError, RequestException
from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, NotFound, PermissionDenied

from . import constants


class BitbucketBaseAPIException(APIException):
    pass


class ProjectNotFoundAPIException(NotFound):
    default_detail = 'Project not found.'


class BadRequestAPIException(BitbucketBaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'
    default_code = 'bad_request'


class NoTagsCouldBeFetchedException(Exception):
    code = constants.RESPONSE_ERROR_FETCHING_TAGS


@contextmanager
def http_request_exception_to_api():
    try:
        yield
    except (IOError, RequestException) as ex:
        logging.exception(ex)
        raise BitbucketBaseAPIException()


@contextmanager
def bitbucket_service_exception_to_api():
    try:
        yield
    except HTTPError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise AuthenticationFailed()

        if ex.response.status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied()

        errors = ex.response.json().get('errors') if ex.response.content else None

        if errors and errors[0].get('exceptionName') == 'com.atlassian.bitbucket.project.NoSuchProjectException':
            logging.warning(errors[0].get('message'))
            raise ProjectNotFoundAPIException()

        if errors:
            logging.error(f'Unexpected Bitbucket exception: {errors[0].get("message")}')
        else:
            logging.error(f'Unexpected Bitbucket exception: {str(ex)}')

        if ex.response.status_code == status.HTTP_400_BAD_REQUEST:
            raise BadRequestAPIException()

        if ex.response.status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound()

        raise BitbucketBaseAPIException()
    except JSONDecodeError as ex:
        logging.exception(ex)

        raise BitbucketBaseAPIException()


@contextmanager
def katka_service_exception_to_api():
    try:
        yield
    except HTTPError as ex:
        if 400 <= ex.response.status_code < 500:
            logging.warning(f'A permission error has occurred while trying to access Katka services: {str(ex)}')
            raise PermissionDenied()

        if 500 <= ex.response.status_code < 600:
            logging.error(f'An error has occurred while accessing Katka services: {str(ex)}')

        raise BitbucketBaseAPIException()
    except JSONDecodeError as ex:
        logging.exception(ex)

        raise BitbucketBaseAPIException()
