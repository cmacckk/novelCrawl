""" Show book info with prettytable """

from prettytable import PrettyTable, ALL
from rich.table import Table
from rich.console import Console


def prettytable_show_book(book_info):
    """使用表格形式输出书籍信息

    Args:
        bookInfo (list): 书籍信息
    """
    # Init table
    table = PrettyTable(field_names=['书名', '作者', '书籍号', '来源'])

    # Setting the alignment of the columns
    table.align['书名'] = 'c'
    table.align['作者'] = 'c'

    # Insert data to table
    for info in book_info:
        table.add_row([
                    info['book'],
                    info['author'],
                    info['book_id'],
                    info['source']
                    ])

    # Print table
    print(table.get_string(hrules=ALL))


def rich_show_book(book_info):
    """ Use rich to show book info """
    # Init table
    table = Table(show_header=True, header_style="bold magenta")

    # Add table header
    table.add_column("书名", justify='center')
    table.add_column("作者", justify='center')
    table.add_column("书籍号", justify='center')
    table.add_column("来源", justify='center')

    # Insert data to table
    for info in book_info:
        table.add_row(
            info['book'],
            info['author'],
            info['book_id'],
            info['source']
        )

    # Create console project and print table
    console = Console()
    console.print(table)
