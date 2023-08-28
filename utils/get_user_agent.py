# Author: CMACCKK <emailforgty@163.com>

""" Generate a random user agent """

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


def generate_random_user_agent():
    """ Generate a random user agent

        returns:
            user_agent (str): A random user agent
    """
    software_names = [SoftwareName.CHROME.value,
                      SoftwareName.FIREFOX.value, SoftwareName.EDGE.value]
    operating_systems = [OperatingSystem.WINDOWS.value,
                         OperatingSystem.LINUX.value]

    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=1)

    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
