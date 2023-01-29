# 1. 笔趣阁小说爬取

## 1.1. 数据来源

```
https://www.bqg70.com/
https://www.ibiquge.org/
https://www.biqu5200.net/
```

支持`python3`

## 1.2. 安装

```bash
pip3 install -r requirements.txt
```

## 1.3. 使用

### 1.3.1. 搜索小说

```bash
python3 crawl.py -s 我家娘子
python3 crawl.py --search 我家娘子
```

## 1.4. 爬取小说

### 1.4.1. 参数说明

注意`-g -e -f`参数仅能选其中一项,选择哪个参数需要对应搜索结果，根据下表进行对应

| 参数  | 长参数        | 来源       |
|:---:|:----------:|:--------:|
| -g  | --ibiquge  | ibiquge  |
| -e  | --bqg7     | bqg70    |
| -f  | --biqu5200 | biqu5200 |

### 1.4.2. 实际使用命令

```bash
# 第一行为说明,其余为实际使用
python3 novel_crawl.py -i [上方搜索出来的书籍号] -[上方搜索后对应数据ID来源的命令参数，可在1.4.1中对应查看]
python3 novel_crawl.py -i 40153 -e
python3 novel_crawl.py -i 40153 --bqg7
python3 novel_crawl.py --id 40153 -e
python3 novel_crawl.py --id 40153 --bqg7 # 爬取《大明第一臣》
python3 novel_crawl.py --id 154288 -g # 爬取《大明第一臣》
python3 novel_crawl.py --id 154288 --ibiquge # 爬取《大明第一臣》
python3 novel_crawl.py --id 154_154288 -f # 爬取《大明第一臣》
python3 novel_crawl.py --id 154_154288 --biqu5200 # 爬取《大明第一臣》
# 以上命令均将小说下载到当前目录的download目录下,如果要更改目录则使用-p参数
python3 novel_crawl.py -i 40153 -e -p [相对路径或绝对路径]
python3 novel_crawl.py -i 40153 -e -p ./download/
# 正常爬取小说时使用10个线程数,如果需要更改线程数，则使用-t参数
python3 novel_crawl.py -i 40153 -e -p ./download/ -t [线程数]
python3 novel_crawl.py -i 40153 -e -p ./download/ -t 20
```

## 1.5. 后记
小说爬取完成后会在`./download/`下生成`小说名.txt`

我一般是用手机在服务器中爬取后，使用sftp下载到手机

最后使用掌阅阅读