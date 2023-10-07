import pytest

from src.crawl.bige7 import Bige7

class TestBige7:
    """ Test Bige7(bqg70.com) class """
    Bige7().search_by_drission_page('武侠')

if __name__ == '__main__':
    pytest.main(['-v', '-s', 'test_bige7.py'])