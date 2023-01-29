import argparse
from ast import arg
import logging
from src.bige5200.bige5200 import BiQuGe5200Net
from src.bige7.bige7 import Bige7
from src.ibiquge.ibiquge_org import IBiQuGeOrg
from utils.book_show import table_show_book

FORMAT = "[%(asctime)s] [%(levelname)s] %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def argparse_deal():
    """命令行参数
    """
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
        table_show_book(Bige7().search_book(args.search)
                        + IBiQuGeOrg().search_book(args.search)
                        + BiQuGe5200Net().search_book(args.search))
    elif args.id and args.ibiquge:
        logging.info("使用ibiquge爬取")
        if args.thread:
            if args.path:
                IBiQuGeOrg().craw_book(args.id, thread=args.thread, path=args.path)
            else:
                IBiQuGeOrg().craw_book(args.id, thread=args.thread)
        else:
            IBiQuGeOrg().craw_book(args.id)
    elif args.id and args.bqg7:
        logging.info("使用bqg7爬取")
        if args.thread:
            if args.path:
                Bige7().craw_book("https://www.bqg70.com/book/" +
                                  args.id + '/', thread=args.thread, path=args.path)
            else:
                Bige7().craw_book("https://www.bqg70.com/book/" + args.id + '/', thread=args.thread)
        else:
            Bige7().craw_book("https://www.bqg70.com/book/" + args.id + '/')

    elif args.id and args.biqu5200:
        logging.info("使用biqu5200爬取")
        if args.thread:
            if args.path:
                BiQuGe5200Net().craw_book(args.id, thread=args.thread, path=args.path)
            else:
                BiQuGe5200Net().craw_book(args.id, thread=args.thread)
        else:
            BiQuGe5200Net().craw_book(args.id)
    else:
        logging.info("参数错误")
