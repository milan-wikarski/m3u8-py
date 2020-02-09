from argparse import ArgumentParser
from m3u8.downloader.downloader import M3U8_Downloader

parser = ArgumentParser(description='m3u8 Parser and downloader')
parser.add_argument('command', choices=['parse', 'download'], help='Command to execute')
parser.add_argument('-i', help='m3u8 url', required=True)
parser.add_argument('-o', help='Output file', required=True)

args = parser.parse_args()

M3U8_Downloader.run(url=args.i, out_file=args.o)
