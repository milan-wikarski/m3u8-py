from m3u8.parser.parser import M3U8_Parser
from m3u8.downloader import M3U8_Downloader
from requests import request

url = 'https://media.cdn.adultswim.com/streams/archive/casualFridaypt3_20200131/stream.m3u8'

# base_uri = 'https://hls.ted.com'
# master_playlist_uri = '/talks/57063.m3u8'

downloader = M3U8_Downloader(url)
downloader.init()
downloader.run(5)
