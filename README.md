# metroxinmin
### dependence
* scrapy

### debug or run with pycharm
* add start.py in folder same as scrapy.cfg (alerady added)
* in pycharm under "run-> edit configure" add a new configure of python,
script path as start.py, working directory as folder of start.py

### todo list
* process duplicated news in all get news,
some news may belong to multiple sub-news. also need to filter out dulicated news already
got in your database with same datetime.
* save out result into db or file
* get latest news datetime from already got news to filter only newer news

