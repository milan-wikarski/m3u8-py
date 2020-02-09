from m3u8.util.url_validator import URLValidator
from m3u8.util.iterator import Iterator
from m3u8.parser.parser import M3U8_Parser
from urllib.parse import urlparse
from pathlib import Path
from PyInquirer import prompt
import shutil
import subprocess
import pycurl
import os
import sys


class M3U8_Downloader:
  @staticmethod
  def run(
    url,
    stream=None,
    video=None,
    audio=None,
    subtitles=None,
    closed_captions=None,
    ignore_autoselect=False,
    out_file='out/merged.mp4'
  ):
    if (not URLValidator.is_valid(url)):
      raise Exception(f'{url} is not a valid URL')

    # Wipe all data from temp folder and initiate temp files
    temp_dir = Path('temp')
    if (temp_dir.is_dir()):
      shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    temp_video_path = temp_dir / 'video.ts'
    temp_video = open(temp_video_path, 'ba')

    # Initiate curl
    curl = pycurl.Curl()

    # Parse the URL
    url = urlparse(url)
    base_url = f'{url.scheme}://{url.netloc}'
    master_playlist_path = '/'.join(url.path.split('/')[:-1]) + '/'
    master_playlist_file = url.path.split('/')[-1]
    master_playlist_full_url = base_url + master_playlist_path + master_playlist_file

    # Fetch and parse master playlist
    master_playlist = M3U8_Parser.parse(master_playlist_full_url)

    # Parse sources
    sources = {
      'video': None,
      'audio': None,
      'subtitles': None
    }

    # ANCHOR Stream variant (VIDEO)
    variant_streams = master_playlist.variant_streams

    if (stream is None):
      choices = []
      for i, variant_stream in enumerate(variant_streams):
        choice = f'{i+1}) ' + '; '.join([
          f'Bandwidth: {variant_stream.bandwidth}',
          f'Resolution: {variant_stream.resolution}'
        ])
        choices.append({ 'value': i, 'name': choice })

      stream = prompt([{
        'type': 'list',
        'name': 'stream',
        'message': 'Please select a variant stream to download',
        'choices': choices
      }])['stream']

    stream = variant_streams[stream]

    sources['video'] = URLValidator.locate_resource(
      base=base_url,
      path=master_playlist_path,
      resource=stream.url
    )

    # ANCHOR Audio alternative rendition
    if (audio != -1 and stream.audio is not None):
      renditions = master_playlist.alternative_renditions[stream.audio]

      if (audio is None):
        choices = []
        for i, rendition in enumerate(renditions):
          choice = f'{i+1}) ' + '; '.join([
            f'Name: {rendition.name}',
            f'Language: {rendition.language}'
          ])
          choices.append({ 'value': i, 'name': choice })
        choices.append({ 'value': -1, 'name': f'{i+2}) No audio' })

        audio = prompt([{
          'type': 'list',
          'name': 'audio',
          'message': 'Please select an audio rendition',
          'choices': choices    
        }])['audio']
      
      if (audio != -1):      
        sources['audio'] = URLValidator.locate_resource(
          base=base_url,
          path=master_playlist_path,
          resource=renditions[audio].url
        )

    # ANCHOR Subtitles alternative rendition
    if (subtitles != -1 and stream.subtitles is not None):
      renditions = master_playlist.alternative_renditions[stream.subtitles]

      if (subtitles is None):
        choices = []
        for i, rendition in enumerate(renditions):
          choice = f'{i+1}) ' + '; '.join([
            f'Name: {rendition.name}',
            f'Language: {rendition.language}'
          ])
          choices.append({ 'value': i, 'name': choice })
        choices.append({ 'value': -1, 'name': f'{i+2}) No subtitles' })

        subtitles = prompt([{
          'type': 'list',
          'name': 'subtitles',
          'message': 'Please select a subtitles rendition',
          'choices': choices
        }])['subtitles']

      if (subtitles != -1):
        sources['subtitles'] = URLValidator.locate_resource(
          base=base_url,
          path=master_playlist_path,
          resource=renditions[i].url
        )

    # Init Iterators
    # Data for each media is stored in dict where key is media type
    iterators = dict()
    segments_count_total = dict()
    segments_count_downloaded = dict()
    for type in sources:
      if (sources[type] is not None):
        playlist = M3U8_Parser.parse(
          src=sources[type],
          master_playlist=master_playlist
        )

        iterator = Iterator(list(playlist.media_segments.items()))

        iterators[type] = iterator
        segments_count_total[type] = len(iterator)
        segments_count_downloaded[type] = 0
      else:
        iterators[type] = Iterator([])
        segments_count_total[type] = None
        segments_count_downloaded[type] = None

    # Download all segments in all media playlists
    while (
      (not iterators['video'].done) or
      (not iterators['audio'].done) or
      (not iterators['subtitles'].done)
    ):
      if (not iterators['video'].done):
        media = 'video'
        temp_file = temp_video
      elif (not iterators['audio'].done):
        media = 'audio'
        break # TODO
      else:
        media = 'subtitles'
        break # TODO

      sequence_number, segment = iterators[media].next()

      # Get segment URL
      url = URLValidator.locate_resource(
        base=base_url,
        path=master_playlist_path,
        resource=segment.url
      )

      # Generate headers
      headers = []
      if (segment.byterange is not None):
        # Add Range if EXT-X-BYTERANGE is present
        headers.append(f'Range: bytes={segment.byterange_offset}-{segment.byterange_offset + segment.byterange}')

      # Download the .ts file and save it to temp folder
      curl.setopt(curl.WRITEDATA, temp_file)
      curl.setopt(curl.URL, url)
      curl.setopt(curl.HTTPHEADER, headers)
      curl.perform()

      # Print progress
      segments_count_downloaded[media] += 1
      to_print = []
      for key in segments_count_total:
        total = segments_count_total[key]
        downloaded = segments_count_downloaded[key]
        if (total is not None and downloaded is not None):
          to_print.append(f'{key:>10}: {round((downloaded / total) * 100)}%')

      print('\n'.join(to_print))
      sys.stdout.write('\033[F' * len(to_print))

    # Remove line moves from console
    print('\n' * len(to_print), end='')

    # Close files and cURL
    temp_video.close()
    curl.close()

    # Merge media by ffmpeg
    command = [
      'ffmpeg',
      '-y',
      '-i', str(temp_video_path.absolute())
    ]

    command += [
      '-c', 'copy',
      out_file
    ]

    response = subprocess.run(command)

    # Remove temp files
    os.remove(temp_video_path)