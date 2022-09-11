# 小说爬取

数据来源https://www.bqg70.com/

支持python3

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 搜索小说

```bash
python3 crawl.py -s 我家娘子
```

## 爬取小说

```bash
python3 crawl.py -b [上方搜索出来的书籍号]
python3 crawl.py -b [上方搜索出来的书籍号] -t [线程数]
```

小说爬取完成后会在当前目录下生成`小说名.txt`

我一般是用手机在服务器中爬取后，使用sftp下载到手机

最后使用掌阅阅读