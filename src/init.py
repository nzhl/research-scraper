import subprocess
import sys


subprocess.Popen(
    ["scrapy","crawl", "author",
     "-a", "url=%s" % sys.argv[1],
     "-a", "author_id=%s" % sys.argv[2]])


