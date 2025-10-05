from enum import Enum


class Crawl(Enum):
    RECURSIVE = 1
    ITERATIVE = 2

class FileTypes(Enum):
    CSV = 1
    XLSX = 2
    JSON = 3


class AssetTypes(Enum):
    LINK = "link"
    SCRIPT = "script"
    CSS = "css"
    BEACON = "beacon"
    IFRAME = "iframe"
    IMG = "img"
    WEBP = "webp"
    XML_HTTP_REQUEST = "xmlhttprequest"
    OTHER = "other"


class UserAgents(Enum):  # https://useragentstring.com/pages/Browserlist/
    MOZILLA = "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201"
    FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"
    EDGE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    CHROME = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"
    SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
    OPERA = "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16.2"
    ANDROID_WEBKIT_BROWSER = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
