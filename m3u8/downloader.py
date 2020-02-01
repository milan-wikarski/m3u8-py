from m3u8.util import URLValidator, Iterator
from m3u8.parser.parser import M3U8_Parser
from requests import request
from urllib.parse import urlparse
import shutil
import subprocess
import re


class M3U8_Downloader:
  def __init__(self, url):
    if (not URLValidator.is_valid(url)):
      raise Exception(f'{url} is not a valid URL')

    url = urlparse(url)
    self.base_url = f'{url.scheme}://{url.netloc}'
    self.master_playlist_path = '/'.join(url.path.split('/')[:-1]) + '/'
    self.master_playlist_file = url.path.split('/')[-1]
    self.master_playlist_full_url = self.base_url + self.master_playlist_path + self.master_playlist_file

    self.master_playlist = None

  def init(self):
    self.master_playlist = M3U8_Parser.parse(
      src=self.master_playlist_full_url,
      playlist_type=M3U8_Parser.PLAYLIST_TYPE_MASTER
    )

  def run(self, stream):
    if (self.master_playlist is None):
      raise Exception('Instance has not been initialized before calling run')

    parts = []
    stream = self.master_playlist.variant_streams[stream]

    while (True):
      url = URLValidator.locate_resource(
        base=self.base_url,
        path=self.master_playlist_path,
        resource=stream.url
      )

      media_playlist = M3U8_Parser.parse(
        src=url,
        playlist_type=M3U8_Parser.PLAYLIST_TYPE_MEDIA
      )

      n_segments = len(media_playlist.media_segments)

      print(f'Media playlist consists of {n_segments} segments')
      if (media_playlist.ext_x_endlist):
        print('Media playlist contains #EXT-X-ENDLIST tag', end='\n\n')
      else:
        print('Media playlist has not ended yet', end='\n\n')

      for sequence_number in media_playlist.media_segments:
        segment = media_playlist.media_segments[sequence_number]

        url = URLValidator.locate_resource(
          base=self.base_url,
          path=self.master_playlist_path,
          resource=segment.url
        )

        print(f'Downloading segment #{sequence_number}/{n_segments} from {url}')

        subprocess.run([
          'ffmpeg',
          '-y',
          '-loglevel', 'panic',
          '-i', url,
          '-c:v', 'copy',
          '-c:a', 'copy',
          f'temp/part-{sequence_number}.ts'
        ])

        parts.append(f'file \'part-{sequence_number}.ts\'')

      if (media_playlist.ext_x_endlist):
        break

    with open('temp/parts.txt', 'w') as f:
      f.write('\n'.join(parts))

    print(f'All {n_segments} downloaded. Initiating the merging process...', end='\n\n')

    subprocess.run([
      'ffmpeg',
      '-y',
      '-loglevel', 'panic',
      '-f', 'concat',
      '-safe', '0',
      '-i', 'temp/parts.txt',
      '-c', 'copy',
      'out/merged.mp4'
    ])

    subprocess.run(['rm', '-rf', 'temp'])
    subprocess.run(['mkdir', 'temp'])

    print('Mergin process finished. All temp files were removed.', end='\n\n')