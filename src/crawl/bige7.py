import requests
from urllib import parse
from lxml import etree
from urllib.parse import urljoin, urlparse, quote
from multiprocessing import Pool
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress
from utils.get_user_agent import generate_random_user_agent
import json
from src.log import LOGGER
from utils.config import TIMEOUT


class Bige7:
    """ Content from www.bqg70.com """

    def search_book(self, book):
        """ search book

            Returns:
                book_info: list[{'book': 'book name',
                                 'book_id': 'book id',
                                 'author': 'author',
                                 'source': 'source'}]
        """
        # Define default request headers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/114.0.0.0 Safari/537.36',
                   }

        LOGGER.info("Search book %s", book)

        response = requests.get(url='https://www.bqg70.com/user/search.html?q=' + quote(book),
                                headers=headers,
                                timeout=TIMEOUT)

        LOGGER.debug('bqg70.com response content is: %s', response.text)

        html_content = response.content.decode('utf-8')

        book_info = []
        if html_content == '1':
            # site interface return fail
            LOGGER.warning('Request bqg70.com search book interface failed!')
            book_info.append(
                        {
                            'book': '暂无',
                            'book_id': '暂无',
                            'author': '暂无',
                            'source': 'bqg70'
                        }
                            )
            return book_info
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

    def get_novel_chapter_urls(self, book_url):
        """ Get novel all chapter urls """
        parsed = urlparse(book_url)
        url = parsed.scheme + "://" + parsed.netloc

        response = requests.get(url=book_url,
                                headers={"User-Agent": generate_random_user_agent()},
                                timeout=TIMEOUT)

        html_content = response.content.decode('utf-8')
        xml = etree.HTML(html_content)
        book_name = xml.xpath('//span[@class="title"]/text()')
        book_chapter_url_path = xml.xpath('//dd/a/@href')

        book_chapter_url_list = []

        for path in book_chapter_url_path:
            if "book" in path:
                book_chapter_url_list.append(urljoin(url, path))
        return book_name, book_chapter_url_list

    @staticmethod
    def get_single_chapter_title_and_content(url):
        """ Get single chapter title and content """
        result = ""
        response = requests.get(url,
                                headers={"User-Agent": generate_random_user_agent()},
                                timeout=TIMEOUT)
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

    def thread_pool_running(self, task_id, chapter_urls, progress):
        result = []
        for _, chapter_url in enumerate(chapter_urls):
            # Get chapter title and content (Dict)
            result = Bige7.get_single_chapter_title_and_content(chapter_url)
            # Update progress rate
            progress.update(task_id, advance=1)
            # get the result

    def craw_book(self, book_url, thread=10, path='./'):
        """ crawl single book
            default save to current directory ./
        """
        book, chapter_urls_list = self.get_novel_chapter_urls(book_url)

        # Create ThreadPoolExecutor as thread pool
        executor = ThreadPoolExecutor(max_workers=5)

        # Create progress object as context manager
        with Progress() as progress:
            # add task
            task_length = len(chapter_urls_list[:-10])
            task = progress.add_task('[red]Crawl task', total=task_length)

            # Use thread pool execute task
            future = executor.submit(self.get_single_chapter_title_and_content, task, chapter_urls_list[:-10], progress)

        # with Pool(thread) as pool:
        #     all_chapter_content = list(
        #         tqdm(
        #             pool.imap(self.get_single_chapter_title_and_content,
        #                     book_chapter_url_list[:-10]),
        #                     total=len(book_chapter_url_list[:-10])
        #             )
        #         )

        # with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
        #     for chapter in all_chapter_content:
        #         file.write(chapter['title'] + '\n\n' +
        #                    chapter['content'] + '\n')
