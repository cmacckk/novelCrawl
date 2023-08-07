from prettytable import PrettyTable, ALL


def table_show_book(book_info):
    """使用表格形式输出书籍信息

    Args:
        bookInfo (list): 书籍信息
    """
    table = PrettyTable(field_names=['书名', '作者', '书籍号', '来源'])
    table.align['书名'] = 'c'
    table.align['作者'] = 'c'

    for info in book_info:
        table.add_row([info['book'],
                      info['author'],
                      info['book_id'],
                      info['source']
                       ])

    print(table.get_string(hrules=ALL))
