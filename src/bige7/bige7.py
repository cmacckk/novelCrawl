import requests
from urllib import parse
from lxml import etree
from urllib.parse import urljoin, urlparse
from multiprocessing import Pool
from tqdm import tqdm
from utils.get_user_agent import get_random_user_agent


class Bige7:
    def search_book(self, book):
        response = requests.get("https://www.bqg70.com/s?q=" +
                                parse.quote(book), headers={"User-Agent": get_random_user_agent()})
        html_content = response.content.decode('utf-8')
        xml = etree.HTML(html_content)

        book_info = []

        book_list = xml.xpath('//h4[@class="bookname"]/a/text()')
        book_url_list = xml.xpath('//h4[@class="bookname"]/a/@href')
        author_list = xml.xpath('//div[@class="author"]/text()')
        # introduce_list = xml.xpath('//div[@class="uptime"]/text()')
        # img_list = xml.xpath('//div[@class="bookimg"]/a/img/@src')

        for i, _ in enumerate(book_list):
            book_info.append(
                {
                    'book': book_list[i],
                    'book_id': book_url_list[i].split('/')[2],
                    'author': author_list[i].split('：')[1],
                    # 'introduce': introduceList[i],
                    # 'imgUrl': imgList[i],
                    'source': 'bqg70'
                }
            )
        return book_info

    # 获取bqg70.com中章节的Urls
    def getBiGe7CrawlUrls(self, book_url):
        parsed = urlparse(book_url)
        url = parsed.scheme + "://" + parsed.netloc

        response = requests.get(book_url, headers={
                                "User-Agent": get_random_user_agent()})

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
            url, headers={"User-Agent": get_random_user_agent()})
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
    def craw_book(self, book_url, thread=10, path='./'):
        book, bookChapterUrlList = self.getBiGe7CrawlUrls(book_url)

        with Pool(thread) as p:
            allChapterContent = list(tqdm(p.imap(self.getBiGe7SpotSingleChapterTitleContent,
                                     bookChapterUrlList[:-10]), total=len(bookChapterUrlList[:-10])))

        with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in allChapterContent:
                # if '：' in chapter['title'].strip():
                #     if chapter['title'].strip().split(' ')[0].startswith('第') and chapter['title'].strip().split(' ')[0].endswith('章'):
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')
                # if len(chapter['title'].strip().split("：")) == 2:
                #     file.write("第" + chapter['title'].split('：')[0] + "章 " + chapter['title'].split('：')[1] + '\n\n' + chapter['content'] + '\n')
