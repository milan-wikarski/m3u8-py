from m3u8.util import URLValidator, Iterator
from m3u8.parser.parser import M3U8_Parser
from urllib.parse import urlparse
import shutil
import subprocess
import re
import requests
import os
from pathlib import Path


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
      src=self.master_playlist_full_url
    )

  def run(self, stream):
    if (self.master_playlist is None):
      raise Exception('Instance has not been initialized before calling run')
    
    # Create temp dir if not exists
    temp_dir = Path('temp')
    if (not (temp_dir.exists() and temp_dir.is_dir())):
      temp_dir.mkdir()

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
        master_playlist=self.master_playlist
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

        headers = {}
        if (segment.byterange is not None):
          headers['Range'] = f'bytes={segment.byterange_offset}-{segment.byterange_offset + segment.byterange}'

        print(f'Downloading segment #{sequence_number}/{n_segments} from {url} with headers {headers}', end='\n\n')

        response = requests.get(url, headers=headers, stream=True)
        temp_current_part = Path(f'temp/part-{sequence_number}.ts')
        with open(temp_current_part, 'wb') as out_file:
          shutil.copyfileobj(response.raw, out_file)

        subprocess.run([
          'ffmpeg',
          '-y',
          '-loglevel', 'panic',
          '-i', url,
          '-c:v', 'copy',
          '-c:a', 'copy',
          f'temp/part-{sequence_number}.ts'
        ])

        parts.append(f'part-{sequence_number}.ts')

      if (media_playlist.ext_x_endlist):
        break

    temp_parts = Path('temp/parts.txt')
    with temp_parts.open('w') as f:
      f.write('\n'.join([f'file \'{part}\'' for part in parts]))

    print(f'All {n_segments} downloaded. Initiating the merging process...', end='\n\n')

    response = subprocess.run([
      'ffmpeg',
      '-y',
      '-i', 'temp/merged.ts',
      '-c', 'copy',
      'out/merged.mp4'
    ])

    shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    print('Mergin process finished. All temp files were removed.', end='\n\n')