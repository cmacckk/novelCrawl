import requests
from urllib import parse
from lxml import etree
from urllib.parse import urljoin
from multiprocessing import Pool
from tqdm import tqdm
from utils.get_user_agent import get_random_user_agent


class IBiQuGeOrg:
    """爬取`http://www.ibiqu.org/`小说内容
    """

    def __init__(self) -> None:
        self.index_url = "http://www.ibiqu.org/"
        self.search_url = "http://www.ibiqu.org/modules/article/search.php?searchkey="
        self.book_url = "http://www.ibiqu.org/book/"

    def search_book(self, book):
        """搜索书籍

        Args:
            book (str): 书籍名称

        Returns:
            str: 书名   作者名  书籍URL
        """
        book_infos = []
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

        for i, _ in enumerate(books):
            book_infos.append({
                'book': books[i],
                'book_id': hrefs[i].split('/')[3],
                'author': authors[i],
                'source': 'ibiquge'
            })


        return book_infos

    def crawl_book_chapter_urls(self, book_id):
        """爬取书籍所有章节的URL

        Args:
            book_id (str): 书籍ID

        Returns:
            book (str): 书名
            chapter_urls (list): 所有章节URL
        """
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
        """爬取单章标题及内容

        Args:
            chapter_url (str): 章节URL

        Returns:
            dict: 标题及内容
        """
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

    def craw_book(self, book_id, thread=10, path='./'):
        """爬取整本书

        Args:
            book_id (str): 书籍ID
            thread (int, optional): 线程数. Defaults to 10.
        """
        book, chapter_urls = self.crawl_book_chapter_urls(book_id)

        with Pool(thread) as p:
            chapters = list(tqdm(p.imap(self.crawl_chapter_title_content,
                                        chapter_urls), total=len(chapter_urls)))

        with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in chapters:
                # if '：' in chapter['title'].strip():
                #     if chapter['title'].strip().split(' ')[0].startswith('第') and chapter['title'].strip().split(' ')[0].endswith('章'):
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')


if __name__ == "__main__":
    # infos = BiQuGe5200().search_book("大明第一臣")
    # print(infos)
    # print(BiQuGe5200().crawl_book_chapter_urls("154288"))
    IBiQuGeOrg().crawl_chapter_title_content(
        'http://www.ibiqu.org/book/154288/184608739.htm')
    # BiQuGe5200().craw_book("154288")
