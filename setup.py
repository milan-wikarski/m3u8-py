from m3u8.parser.parser import M3U8_Parser
from m3u8.downloader import M3U8_Downloader
from requests import request

# url = 'https://media.cdn.adultswim.com/streams/archive/casualFridaypt3_20200131/stream.m3u8'

url = 'https://hls.ted.com/talks/57063.m3u8'

downloader = M3U8_Downloader(url)
downloader.init()
downloader.run(5)
