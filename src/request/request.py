import os
import time
import requests
from utils.get_user_agent import generate_random_user_agent
from utils.config import TIMEOUT
from src.log import LOGGER


def make_request_with_retries(url, retries=5, delay=4):
    """ When get response fail, loop to get response """
    for retry in range(retries):
        try:
            response = requests.get(
                                    url,
                                    headers={
                                    "User-Agent": generate_random_user_agent()},
                                    timeout=TIMEOUT
                                    )
            return response  # If successful response, return it
        except requests.RequestException as error:
            LOGGER.debug("Request %s failed: %s", url, error)
            if retry < retries - 1:  # If not the last retry
                LOGGER.debug("Retrying in %s seconds...", delay)
                time.sleep(delay)

    LOGGER.error("Request failed after %s retries.", retries)
    return None



