from importlib.resources import path
from urllib.parse import urlencode
import requests
from urllib import parse
import random
from lxml import etree
from urllib.parse import urljoin
from multiprocessing import Pool
from tqdm import tqdm

# 随机获得ua


def get_random_user_agent():
    """获取随机UA头

    Returns:
        str: 随机UA头
    """
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


class BiQuGe5200:
    def __init__(self) -> None:
        self.index_url = "http://www.ibiqu.org/"
        self.search_url = "http://www.ibiqu.org/modules/article/search.php?searchkey="
        self.book_url = "http://www.ibiqu.org/book/"

    def search_book(self, book):
        response = requests.get(url=self.search_url + parse.quote(book),
                                headers={"User-Agent": get_random_user_agent()})
        response_text = response.content.decode("gbk")
        xml = etree.HTML(response_text)
        books = xml.xpath('//td[@class="odd"]/a/text()')
        odd_infos = xml.xpath('//td[@class="odd"]/text()')
        authors = [odd_infos[i] for i in range(0, len(odd_infos), 2)]
        hrefs = xml.xpath('//td[@class="odd"]/a/@href')
        url_hrefs = [urljoin(self.index_url, href) for href in hrefs]

        # print(odd_infos)
        # print(hrefs)

        # print(books)
        # print(authors)
        # print(url_hrefs)

        infos = ''

        for i in range(len(books)):
            infos += f"{books[i]}\t{authors[i]}\t{url_hrefs[i]}\n"

        return infos.strip()

    def crawl_book_chapter_urls(self, book_id):
        response = requests.get(url=urljoin(self.book_url, book_id) + '/',
                                headers={"User-Agent": get_random_user_agent()})
        response_text = response.content.decode("gbk")
        # print(response_text)
        xml = etree.HTML(response_text)
        chapter_paths = xml.xpath('//div[@id="list"]/dl/dd/a/@href')
        book = xml.xpath('//*[@id="info"]/h1/text()')
        # print(len(chapter_paths))
        chapter_urls = [urljoin(self.index_url, x) for x in chapter_paths]
        # print(chapter_urls)
        return book, chapter_urls

    def crawl_chapter_title_content(self, chapter_url):
        try:
            response = requests.get(url=chapter_url,
                                    headers={"User-Agent": get_random_user_agent()})
            response_text = response.content.decode("gbk")
            xml = etree.HTML(response_text)
            title = xml.xpath('//div[@class="bookname"]/h1/text()')
            contents = xml.xpath('//div[@id="content"]/p/text()')
            content = '\n'.join([x.strip().replace("\u3000", '')
                                for x in contents])
            # print(title)
            # print(content)

            return {
                "title": title[0],
                "content": content
            }
        except:
            return {
                "title": "Error title",
                "content": "Content Error"
            }

    def craw_book(self, book_id, thread=10):
        book, chapter_urls = self.crawl_book_chapter_urls(book_id)

        with Pool(thread) as p:
            chapters = list(tqdm(p.imap(self.crawl_chapter_title_content,
                                        chapter_urls), total=len(chapter_urls)))

        with open('./' + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in chapters:
                # if '：' in chapter['title'].strip():
                #     if chapter['title'].strip().split(' ')[0].startswith('第') and chapter['title'].strip().split(' ')[0].endswith('章'):
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')


if __name__ == "__main__":
    # infos = BiQuGe5200().search_book("大明第一臣")
    # print(infos)
    # print(BiQuGe5200().crawl_book_chapter_urls("154288"))
    BiQuGe5200().crawl_chapter_title_content(
        'http://www.ibiqu.org/book/154288/184608739.htm')
    # BiQuGe5200().craw_book("154288")
