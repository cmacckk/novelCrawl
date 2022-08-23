import requests
from urllib.parse import urlparse, urljoin
from lxml import etree
from multiprocessing import Pool
from tqdm import tqdm
from urllib.parse import quote
from prettytable import PrettyTable, ALL
import argparse
import random


# 搜索书籍
class SearchBook:
    def __init__(self, book):
        self.book = book

# 随机获得ua
def getUserAgent():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua

# 获取随机UA头
ua = getUserAgent


# 获取书籍名及对应章节地址
def get_crawl_urls(bookUrl):
    parsed = urlparse(bookUrl)
    url = parsed.scheme + "://" + parsed.netloc

    response = requests.get(bookUrl, headers={"User-Agent": ua})

    htmlContent = response.content.decode('utf-8')
    xml = etree.HTML(htmlContent)
    bookName = xml.xpath('//span[@class="title"]/text()')
    bookChapterUrlPath = xml.xpath('//dd/a/@href')

    bookChapterUrlList = []

    for path in bookChapterUrlPath:
        if "book" in path:
            bookChapterUrlList.append(urljoin(url, path))
    return bookName, bookChapterUrlList
    

# 获取章节标题及内容
def get_chapter(url):
    result = ""
    response = requests.get(url, headers={"User-Agent": ua})
    htmlContent = response.content.decode('utf-8')
    xml = etree.HTML(htmlContent)
    title = xml.xpath('//span[@class="title"]/text()')
    content = xml.xpath('//div[@id="chaptercontent"]/text()')
    for data in content:
        result += data.replace("\u3000", "") + '\n'
        
    # print(title)
    
    return {
        "title": title[0].split('_')[0],
        "content": result.rstrip()
    }


# 爬取单本书籍
def crawl_single_book(bookUrl, thread=10, verbose=True, path='./'):
    book, bookChapterUrlList = get_crawl_urls(bookUrl)

    if verbose:
        print("[INFO] 爬取《" + book[0] + "》")

    with Pool(thread) as p:
        allChapterContent = list(tqdm(p.imap(get_chapter, bookChapterUrlList[:-10]), total=len(bookChapterUrlList[:-10])))
    
    if verbose:
        print("[INFO] {}共有".format('《' + book[0] + '》') + str(len(allChapterContent)) + "章")
        
    
    # print(allChapterContent[1:3])
    # print(len(allChapterContent))

    with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
        for chapter in allChapterContent:
            file.write(chapter['title'] + '\n\n' + chapter['content'] + '\n')
            if chapter['title'].split(' ')[0].startswith('第') and chapter['title'].split(' ')[0].endswith('章'):
                file.write(chapter['title'] + '\n\n' + chapter['content'] + '\n')
            elif len(chapter['title'].split('：')) == 2:
                file.write("第" + chapter['title'].split('：')[0] + "章 " + chapter['title'].split('：')[1] + '\n\n' + chapter['content'] + '\n')
    if verbose:
        print("[INFO] 爬取《" + book[0] + "》完成")


# 获取笔趣阁查询的书籍信息
def get_book_info(bookName):
    response = requests.get("https://www.bige7.com/s?q=" + quote(bookName), headers={"User-Agent": ua})
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
                'imgUrl': imgList[i]
            }
        )
    return bookInfo


# 使用表格形式输出书籍信息
def table_show_book(bookInfo):
    table = PrettyTable(field_names=['书名', '作者', '书籍号'])
    table.align['书名'] = 'c'
    table.align['作者'] = 'c'

    for info in bookInfo:
        table.add_row(['《' + info['bookName'] + '》', info['author'].split('：')[1], info['bookUrl'].split('/')[-2]])

    print(table.get_string(hrules=ALL))


# 处理命令行参数
def argparse_deal():
    parser = argparse.ArgumentParser(description='爬取笔趣阁的小说')
    parser.add_argument('-s', '--search', help='搜索小说,可以使用书名和作者名')
    parser.add_argument('-b', '--book', help='指定书籍号,如59')
    parser.add_argument('-t', '--thread', help='线程数,默认为10', default=10, type=int)
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息,默认为True', default=True)
    parser.add_argument('-p', '--path', help='指定保存路径,默认为当前路径,格式为:/home/test/book/', default='./')
    args = parser.parse_args()

    if args.search:
        table_show_book(get_book_info(args.search))
    elif args.book:
        crawl_single_book(urljoin("https://www.bige7.com/book/", args.book), args.thread, args.verbose, args.path)
    else:
        print('[ERROR] 请输入参数')
    

if __name__ == "__main__":
    argparse_deal()