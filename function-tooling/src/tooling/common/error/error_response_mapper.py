from typing import Any, Dict

from pylibrarycore.exceptions.exceptions import BaseLambdaException, InternalServerError
from pylibrarycore.logging.logger_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class ErrorResponseMapper:
    def map(self, e: Exception) -> Dict[str, Any]:
        return self.__do_map(
            e if isinstance(e, BaseLambdaException) else InternalServerError("Not handled error", e))

    @staticmethod
    def __do_map(exception: BaseLambdaException) -> Dict[str, Any]:
        logger.exception(f'Returning Error: {exception.message}', extra={"statusCode": str(exception.http_status)})
        return {
            "statusCode": exception.http_status,
            "body": {
                "errorCode": exception.http_status,
                "errorMessage": f'{exception.message}'
            }
        }
