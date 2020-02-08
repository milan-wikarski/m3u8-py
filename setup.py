from argparse import ArgumentParser
from m3u8.parser.parser import M3U8_Parser
from m3u8.downloader.downloader import M3U8_Downloader
from requests import request

parser = ArgumentParser(description='m3u8 Parser and downloader')
parser.add_argument('command', choices=['parse', 'download'], help='Command to execute')
parser.add_argument('-i', help='m3u8 url', required=True)
parser.add_argument('-o', help='Output file', required=True)

args = parser.parse_args()

# if (args['command'])

# print(args)
# exit()

# url = 'https://media.cdn.adultswim.com/streams/archive/casualFridaypt3_20200131/stream.m3u8'

# url = 'https://hls.ted.com/talks/57063.m3u8'

downloader = M3U8_Downloader(url=args.i)
downloader.init()
# print(downloader.master_playlist)
downloader.run(out_file=args.o)
