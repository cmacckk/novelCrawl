# Author: CMACCKK <emailforgty@163.com>


""" Crawl novel command-line interface

    use to search and download novel

    in home directory use command to search book:
        python3 novel_crawl.py -s 武侠
        or python3 novel_crawl.py --search 武侠

    the result is search novel name contains "武侠"
"""


import argparse
from src.log import LOGGER
from src.crawl.bige7 import Bige7
from utils.book_show import table_show_book


def argparse_deal():
    """ Command-line interface arguments """
    parser = argparse.ArgumentParser(description='爬取笔趣阁的小说')
    parser.add_argument('-s', '--search', help='搜索小说,可以使用书名和作者名')
    parser.add_argument('-i', '--id', help='指定书籍号,如59')
    parser.add_argument('-t', '--thread', help='线程数,默认为10',
                        default=10, type=int)
    parser.add_argument('-g', '--ibiquge', help='使用ibiquge来源', action="store_true")
    parser.add_argument('-e', '--bqg7', help='使用bqg70来源', action="store_true")
    parser.add_argument('-f', '--biqu5200', help='使用biqu5200来源', action="store_true")
    parser.add_argument(
        '-p', '--path', help='指定保存路径,默认为当前路径,格式为:/home/test/book/', default='./download/')
    args = parser.parse_args()

    if args.search:
        table_show_book(Bige7().search_book(args.search))
    elif args.id and args.bqg7:
        LOGGER.info("crawl bqg70.com")
        if args.thread:
            if args.path:
                Bige7().craw_book("https://www.bqg70.com/book/" +
                                  args.id + '/', thread=args.thread, path=args.path)
            else:
                Bige7().craw_book("https://www.bqg70.com/book/" + args.id + '/', thread=args.thread)
        else:
            Bige7().craw_book("https://www.bqg70.com/book/" + args.id + '/')
    else:
        LOGGER.info("参数错误")
