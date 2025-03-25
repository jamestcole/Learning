from pylibrarycore.datatypes.lambda_context import LambdaContext
from pylibrarycore.logging.logger_utils import setup_logging, with_lambda_logging_context, get_logger

setup_logging()
logger = get_logger(__name__)


# TODO: decorator (from logger_utils) needs to be typed
@with_lambda_logging_context
def lambda_handler(_0: dict[str, str], _1: LambdaContext) -> dict[str, str]:
    try:
        return {"generate": "service versions page"}
    except Exception as error:
        logger.exception("Failed")
        raise error
