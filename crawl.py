import requests
from urllib.parse import urlparse, urljoin
from lxml import etree
from multiprocessing import Pool
from tqdm import tqdm
from urllib.parse import quote
from prettytable import PrettyTable, ALL
import argparse
import random


# 随机获得ua
def getRandomUserAgent():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(
        first_num, third_num, fourth_num)

    user_agent = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return user_agent


# 搜索书籍
class SearchBook:
    def __init__(self, book):
        self.book = book

    # bige7搜索
    def bige7(self):
        response = requests.get("https://www.bqg70.com/s?q=" +
                                quote(self.book), headers={"User-Agent": getRandomUserAgent()})
        htmlContent = response.content.decode('utf-8')
        xml = etree.HTML(htmlContent)

        bookInfo = []

        bookNameList = xml.xpath('//h4[@class="bookname"]/a/text()')
        bookUrlList = xml.xpath('//h4[@class="bookname"]/a/@href')
        authorList = xml.xpath('//div[@class="author"]/text()')
        introduceList = xml.xpath('//div[@class="uptime"]/text()')
        imgList = xml.xpath('//div[@class="bookimg"]/a/img/@src')

        for i in range(len(bookNameList)):
            bookInfo.append(
                {
                    'bookName': bookNameList[i],
                    'bookUrl': bookUrlList[i],
                    'author': authorList[i],
                    'introduce': introduceList[i],
                    'imgUrl': imgList[i],
                    'source': 'bqg70'
                }
            )
        return bookInfo


class CrawlBook:
    def __init__(self, bookUrl):
        self.bookUrl = bookUrl

    # 获取bqg70.com中章节的Urls
    def getBiGe7CrawlUrls(self):
        parsed = urlparse(self.bookUrl)
        url = parsed.scheme + "://" + parsed.netloc

        response = requests.get(self.bookUrl, headers={
                                "User-Agent": getRandomUserAgent()})

        htmlContent = response.content.decode('utf-8')
        xml = etree.HTML(htmlContent)
        bookName = xml.xpath('//span[@class="title"]/text()')
        bookChapterUrlPath = xml.xpath('//dd/a/@href')

        bookChapterUrlList = []

        for path in bookChapterUrlPath:
            if "book" in path:
                bookChapterUrlList.append(urljoin(url, path))
        return bookName, bookChapterUrlList

    # 获取bqg70.com单章节标题及内容

    def getBiGe7SpotSingleChapterTitleContent(self, url):
        result = ""
        response = requests.get(
            url, headers={"User-Agent": getRandomUserAgent()})
        htmlContent = response.content.decode('utf-8')
        xml = etree.HTML(htmlContent)
        title = xml.xpath('//span[@class="title"]/text()')
        content = xml.xpath('//div[@id="chaptercontent"]/text()')
        for data in content:
            result += data.replace("\u3000", "") + '\n'

        return {
            "title": title[0].split('_')[0],
            "content": result.rstrip()
        }

    # 爬取单本书籍
    def crawlBiGe7SingleBook(self, thread=10, verbose=True, path='./'):
        book, bookChapterUrlList = self.getBiGe7CrawlUrls()

        if verbose:
            print("[INFO] 爬取《" + book[0] + "》")

        with Pool(thread) as p:
            allChapterContent = list(tqdm(p.imap(self.getBiGe7SpotSingleChapterTitleContent,
                                     bookChapterUrlList[:-10]), total=len(bookChapterUrlList[:-10])))

        if verbose:
            print("[INFO] {}共有".format('《' + book[0] + '》') +
                  str(len(allChapterContent)) + "章")

        with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in allChapterContent:
                # if '：' in chapter['title'].strip():
                #     if chapter['title'].strip().split(' ')[0].startswith('第') and chapter['title'].strip().split(' ')[0].endswith('章'):
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')
                # if len(chapter['title'].strip().split("：")) == 2:
                #     file.write("第" + chapter['title'].split('：')[0] + "章 " + chapter['title'].split('：')[1] + '\n\n' + chapter['content'] + '\n')
        if verbose:
            print("[INFO] 爬取《" + book[0] + "》完成")


# 使用表格形式输出书籍信息
def tableShowBookInfo(bookInfo):
    table = PrettyTable(field_names=['书名', '作者', '书籍号', '来源'])
    table.align['书名'] = 'c'
    table.align['作者'] = 'c'

    for info in bookInfo:
        table.add_row(['《' + info['bookName'] + '》', info['author'].split('：')
                      [1], info['bookUrl'].split('/')[-2], info['source']])

    print(table.get_string(hrules=ALL))


# 处理命令行参数
def argparse_deal():
    parser = argparse.ArgumentParser(description='爬取笔趣阁的小说')
    parser.add_argument('-s', '--search', help='搜索小说,可以使用书名和作者名(bige7.com)')
    parser.add_argument('-b', '--book', help='指定书籍号,如59')
    parser.add_argument('-t', '--thread', help='线程数,默认为10',
                        default=10, type=int)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='显示详细信息,默认为True', default=True)
    parser.add_argument(
        '-p', '--path', help='指定保存路径,默认为当前路径,格式为:/home/test/book/', default='./')
    args = parser.parse_args()

    if args.search:
        tableShowBookInfo(SearchBook(args.search).bige7())
    elif args.book:
        CrawlBook(urljoin("https://www.bqg70.com/book/", args.book)
                  ).crawlBiGe7SingleBook(args.thread, args.verbose, args.path)
    else:
        print('[ERROR] 请输入参数')


if __name__ == "__main__":
    argparse_deal()
    # result = SearchBook("加一个").bige7()
    # print(result)
    # CrawlBook("https://www.bige7.com/book/777").crawlBiGe7SingleBook()
