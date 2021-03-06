from m3u8.util.url_validator import URLValidator
from m3u8.util.iterator import Iterator, IteratorsDict
from m3u8.util.path_file import PathFile
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

    # Wipe all data from temp folder
    temp_dir = Path('temp')
    if (temp_dir.is_dir()):
      shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    # Store temp file in dict where key is media type
    # Value is PathFile
    temp_files = {
      'video': None,
      'audio': None,
      'subtitles': None
    }

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

    temp_files['video'] = PathFile(temp_dir / 'video.ts', 'ba')

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

        temp_files['audio'] = PathFile(temp_dir / 'audio.aac', 'ba')

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

        temp_files['subtitles'] = PathFile(temp_dir / 'subtitles.srt', 'ba')

    # Init Iterators for each media type
    # Stored in dict where media type is key
    iterators = IteratorsDict()
    for type in sources:
      if (sources[type] is not None):
        playlist = M3U8_Parser.parse(sources[type], master_playlist)
        iterators[type] = Iterator(list(playlist.media_segments.items()))
      else:
        iterators[type] = Iterator([])

    # Download all segments in all media playlists
    while (not iterators.all_done):
      if (not iterators['video'].done):
        media = 'video'
      elif (not iterators['audio'].done):
        media = 'audio'
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

      curl.setopt(curl.WRITEDATA, temp_files[media].file)
      curl.setopt(curl.URL, url)
      curl.setopt(curl.HTTPHEADER, headers)
      curl.perform()

      # Print progress
      to_print = []
      for media, iterator in iterators.items():
        if (iterator is not None):
          to_print.append(f'{media:>9}: {round((iterator.progress) * 100)}%')

      print('\n'.join(to_print))
      sys.stdout.write('\033[F' * len(to_print))

    # Remove line moves from console
    print('\n' * len(to_print), end='')

    # Merge media by ffmpeg
    command = [
      'ffmpeg',
      '-y',
      '-i', temp_files['video'].abspath
    ]

    # if (temp_files['audio'] is not None):
    #   command += ['-i', temp_files['audio'].abspath]

    command += [
      '-c', 'copy',
      out_file
    ]

    response = subprocess.run(command)

    # Close and remove files and cURL
    for key in temp_files:
      if (temp_files[key] is not None):
        temp_files[key].close()
        # temp_files[key].remove()

    curl.close()