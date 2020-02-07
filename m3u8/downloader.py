from m3u8.util import URLValidator, Iterator
from m3u8.parser.parser import M3U8_Parser
from urllib.parse import urlparse
import shutil
import subprocess
import pycurl
import os
import requests
from pathlib import Path
from m3u8.util import int_input


class M3U8_Downloader:
  def __init__(self, url):
    if (not URLValidator.is_valid(url)):
      raise Exception(f'{url} is not a valid URL')

    # Parse the URL
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

  def run(self, stream=None, video=None, audio=None, subtitles=None, closed_captions=None, ignore_autoselect=False):
    if (self.master_playlist is None):
      raise Exception('Instance has not been initialized before calling run')

    curl = pycurl.Curl()
    
    # Wipe all data from temp.ts
    temp_file_path = Path(f'temp.ts')
    temp_file = open(temp_file_path, 'bw')
    temp_file.close()

    variant_streams = self.master_playlist.variant_streams

    # User has to chose variant stream if it was not specified
    if (stream is None):
      print('Please select a variant stream to download:')
      for i, variant_stream in enumerate(variant_streams):
        print(f'[{i}]', end=' ')
        print('; '.join([
          f'Bandwidth: {variant_stream.bandwidth}',
          f'Resolution: {variant_stream.resolution}'
        ]))

      stream = int_input(0, len(variant_streams))

    stream = variant_streams[stream]

    # Audio alternative rendition
    if (audio != -1 and stream.audio is not None):
      renditions = self.master_playlist.alternative_renditions[stream.audio]

      if (audio is None):
        for i, rendition in enumerate(renditions):
          if (not ignore_autoselect and rendition.autoselect):
            audio = i
            break

      audio_src = URLValidator.locate_resource(
        base=self.base_url,
        path=self.master_playlist_path,
        resource=renditions[i].url
      )

      audio = requests.get(audio_src).text
    else:
      audio = None

    # Subtitles alternative rendition
    if (subtitles != -1 and stream.subtitles is not None):
      renditions = self.master_playlist.alternative_renditions[stream.subtitles]

      if (subtitles is None):
        for i, rendition in enumerate(renditions):
          if (not ignore_autoselect and rendition.autoselect):
            subtitles = i
            break

      subtitles_src = URLValidator.locate_resource(
        base=self.base_url,
        path=self.master_playlist_path,
        resource=renditions[i].url
      )

      subtitles = requests.get(subtitles_src).text
    else:
      subtitles = None

    # Open temp file and start downloading
    with open(temp_file_path, 'ba') as temp_file:
      curl.setopt(curl.WRITEDATA, temp_file)
      
      while (True):
        # Get media playlist URL
        url = URLValidator.locate_resource(
          base=self.base_url,
          path=self.master_playlist_path,
          resource=stream.url
        )

        # Fetch and parse media playlist
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

        # Download all segments in media playlist
        for sequence_number in media_playlist.media_segments:
          segment = media_playlist.media_segments[sequence_number]

          # Get segment URL
          url = URLValidator.locate_resource(
            base=self.base_url,
            path=self.master_playlist_path,
            resource=segment.url
          )

          # Generate headers
          headers = []
          if (segment.byterange is not None):
            # Add Range if EXT-X-BYTERANGE is present
            headers.append(f'Range: bytes={segment.byterange_offset}-{segment.byterange_offset + segment.byterange}')

          print(f'Downloading segment #{sequence_number}/{n_segments} from {url} with headers {headers}', end='\n\n')

          # Download the .ts file and save it to temp folder
          curl.setopt(curl.URL, url)
          curl.setopt(curl.HTTPHEADER, headers)
          curl.perform()

        # End if EXT-X-ENDLIST was found
        if (media_playlist.ext_x_endlist):
          break

    # Merge the segments by ffmpeg
    response = subprocess.run([
      'ffmpeg',
      '-y',
      '-i', str(temp_file_path.absolute()),
      '-c', 'copy',
      'out/merged.mp4'
    ])

    os.remove(temp_file_path)

    print('Mergin process finished. All temp files were removed.', end='\n\n')