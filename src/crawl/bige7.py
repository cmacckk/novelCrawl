from urllib.parse import urljoin, urlparse, quote
import time
import base64
import os
import json
from concurrent.futures import ThreadPoolExecutor
import requests
from ebooklib import epub
from lxml import etree
from rich.progress import Progress
from selenium import webdriver
from DrissionPage import WebPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import By
from src.log import LOGGER
from src.request.request import make_request_with_retries
from src.utils.config import DEFAULT_DOWNLOAD_PATH_NAME, WIN_CHROME_DRIVER_PATH, WIN_CHROME_EXECUTABLE_PATH, TIMEOUT
from src.utils.get_user_agent import generate_random_user_agent

class Bige7:
    """ Content from www.bqg70.com """
    def search_by_drission_page(self, book_name):
        """ Use DrissionPage func to crawl book information """
        LOGGER.info("Search book %s", book_name)
        chromium_options = ChromiumOptions()
        chromium_options.set_argument('--headless')
        page = WebPage(driver_or_options=chromium_options)
        page.get('https://www.bqg70.com/')
        page.ele('@name=q').input(book_name)
        page.ele('@type=submit').click()
        loop = 5
        page.wait.load_start()
        try:
            for index in range(loop):
                div = page.ele('@class=hots', timeout=4)
                if div.text == '加载中……':
                    LOGGER.info('Loading search result, wait 2s, try %s', index + 1)
                    time.sleep(2)
                else:
                    break
            if div.text == '暂无':
                return '暂时无法使用搜索功能'
        except ElementNotFoundError:
            LOGGER.info('Loading over...')

        authors_loc = (By.XPATH, '//div[@class="author"]')
        book_names_loc = (By.XPATH, '//h4[@class="bookname"]/a')

        authors = page.eles(authors_loc)
        book_names = page.eles(book_names_loc)

        book_info = []
        for index, name in enumerate(book_names):
            book_info.append(
                {'book': name.text,
                'book_id': name.link.split('/')[-2],
                'author': authors[index].text.split('：')[-1],
                'source': 'bqg70'}
            )
        page.close_driver()
        return book_info

    def search_book_api(self, book):
        """ search book by requests

            Returns:
                book_info: list[{'book': 'book name',
                                 'book_id': 'book id',
                                 'author': 'author',
                                 'source': 'source'}]
        """
        LOGGER.info("Search book %s", book)

        response = make_request_with_retries(
            'https://www.bqg70.com/user/search.html?q=' + quote(book))

        html_content = response.content.decode('utf-8')

        book_info = []
        if html_content == '1':
            # site interface return fail
            LOGGER.warning('Request bqg70.com search book interface failed!')
            return
        # site interface return success
        LOGGER.info('Request bqg70.com search book interface success')
        info_json = json.loads(html_content)

        try:
            # return book info
            for _, data in enumerate(info_json):
                if data['url_list'].endswith('/'):
                    book_id = urlparse(data['url_list']).path.split('/')[-2]
                else:
                    book_id = urlparse(data['url_list']).path.split('/')[-1]
                book_info.append(
                    {
                        'book': f"《{data['articlename']}》",
                        'book_id': book_id,
                        'author': data['author'],
                        'source': 'bqg70'
                    }
                )
            return book_info
        except TypeError as error:
            LOGGER.error(error)
            return

    def search_book_selenium(self, book, OS='Windows'):
        """ search book by selenium (Develop)"""
        if OS == 'Windows':
            webdriver_options = webdriver.ChromeOptions()
            webdriver_options.binary_location = WIN_CHROME_EXECUTABLE_PATH
            webdriver_options.executable_path = WIN_CHROME_DRIVER_PATH
            driver = webdriver.Chrome(options=webdriver_options)
            # webdriver_options.add_argument('--headless')
            # webdriver_options.add_argument('--disable-gpu')
            driver.get('https://m.bqgso.cc/s?q=' + quote(book))

    def get_novel_chapter_urls(self, book_url):
        """ Get novel all chapter urls """
        parsed = urlparse(book_url)
        url = parsed.scheme + "://" + parsed.netloc

        response = make_request_with_retries(book_url)
        if response is None:
            LOGGER.error('Request %s failed', book_url)
            return None, None, None, None

        html_content = response.content.decode('utf-8')
        xml = etree.HTML(html_content)
        book_name = xml.xpath('//span[@class="title"]/text()')
        author = xml.xpath('//div[@class="small"]/span[1]/text()')[0].split('：')[1]
        cover_url = xml.xpath('//div[@class="cover"]/img/@src')
        file_extension = self.download_cover(cover_url[0])
        book_chapter_url_path = xml.xpath('//dd/a/@href')

        book_chapter_url_list = []

        for path in book_chapter_url_path:
            if "book" in path:
                book_chapter_url_list.append(urljoin(url, path))
        return book_name, book_chapter_url_list, author, file_extension

    @staticmethod
    def download_cover(url):
        """ from bqg70 download cover """
        filename = os.path.basename(url)
        file_extension = os.path.splitext(filename)[1]
        save_path = f'./img/cover.{file_extension}'
        response = requests.get(
                                url,
                                headers={
                                "User-Agent": generate_random_user_agent()},
                                timeout=TIMEOUT
                                )
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            return file_extension
        else:
            return

    @staticmethod
    def get_single_chapter_title_and_content(url):
        """ From crawl url to get single chapter title and content """
        result = ""
        response = make_request_with_retries(url)
        if response is None:
            LOGGER.error('Request %s failed', url)
            return {'title': 'Request failed', 'content': 'Request failed'}
        html_content = response.content.decode('utf-8')
        xml = etree.HTML(html_content)
        title = xml.xpath('//span[@class="title"]/text()')
        content = xml.xpath('//div[@id="chaptercontent"]/text()')
        for data in content:
            result += data.replace("\u3000", "") + '\n'

        return {
            "title": title[0].split('_')[0],
            "content": result.rstrip()
        }

    def craw_book(self, book_url, thread=10, path='./'):
        """ crawl single book
            default save to current directory ./
            output format is epub
        """
        book, chapter_urls_list, author, file_extension = self.get_novel_chapter_urls(book_url)
        if book is None or chapter_urls_list is None:
            LOGGER.error('Get book %s chapter urls failed', book_url)
            return
        LOGGER.info('Crawl book %s, use %s thread', book[0], thread)
        LOGGER.debug('Crawl book url is %s', book_url)
        # Create ThreadPoolExecutor as thread pool
        executor = ThreadPoolExecutor(max_workers=thread)

        futures = [executor.submit(
            self.get_single_chapter_title_and_content, url) for url in chapter_urls_list[:-10]]

        # Create progress object as context manager
        with Progress() as progress:
            # add task
            task_length = len(chapter_urls_list[:-10])
            task_bar = progress.add_task(
                f'[red]Crawl 《{book[0]}》', total=task_length)

            # Use thread pool execute task
            while not all(future.done() for future in futures):
                progress.update(task_bar, completed=sum(
                    1 for future in futures if future.done()))

            # Create epub object
            epub_book =  epub.EpubBook()
            epub_book.set_title(book[0])
            epub_book.set_language('zh')
            epub_book.add_author(author)

            # 设置封面图片（base64 编码）
            cover_image_path = f"./img/cover.{file_extension}"  # 替换为你的封面图片路径
            with open(cover_image_path, "rb") as cover_image_file:
                cover_image_data = cover_image_file.read()
                cover_image_base64 = base64.b64encode(cover_image_data).decode("utf-8")

            cover_page = epub.EpubHtml(title="Cover Page", file_name="cover.xhtml", lang="zh")
            cover_page.content = f'<img style="width: 100%;height: 100%;" src="data:image/jpeg;base64,{cover_image_base64}" alt="Cover">'
            epub_book.add_item(cover_page)

            if not os.path.exists(os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_PATH_NAME)):
                # Create output directory
                LOGGER.info(
                    'Current directory "%s" not exist "download" directory, create it', os.getcwd())
                os.makedirs(os.path.join(
                    os.getcwd(), DEFAULT_DOWNLOAD_PATH_NAME))

            for future in futures:
                chapter_json = future.result()
                # Create chapter object
                chapter = epub.EpubHtml(title=chapter_json["title"], file_name=f"{chapter_json['title']}.xhtml", lang="zh")

                content_list = chapter_json['content'].split('\n')

                filtered_list = [item for item in content_list if item != ""]

                content = ""

                for item in filtered_list:
                    content += f"<p>{item}</p>"

                # 将自定义内容设置为章节的内容
                chapter.content = f"{content}"

                # 将章节添加到书籍
                epub_book.add_item(chapter)

            # 设置书籍的内容
            epub_book.spine = [chapter for chapter in epub_book.items if isinstance(chapter, epub.EpubHtml)]
            # 生成EPUB文件
            book_path = os.path.join(path, book[0])
            epub.write_epub(book_path + ".epub", epub_book, {})

        LOGGER.info('Crawl %s success, book write to %s',
                    book[0], os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_PATH_NAME) + '\\' + book[0] + '.epub')
