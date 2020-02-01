from m3u8.util import URIValidator
from m3u8.parser.parser import M3U8_Parser
from requests import request
import shutil


class M3U8_Downloader:
  def __init__(self, base_uri, master_playlist_uri):
    if (not URIValidator.is_valid(base_uri)):
      raise Exception(f'{base_uri} is not a valid URI')

    self.base_uri = base_uri
    self.master_playlist_uri = master_playlist_uri
    self.master_playlist = None

  @property
  def variant_streams(self):
    return self.master_playlist.variant_streams

  @property
  def current_stream(self):
    return len(self.variant_streams) - 2

  def init(self):
    self.master_playlist = M3U8_Parser.parse(
      src=self.base_uri + self.master_playlist_uri,
      playlist_type=M3U8_Parser.PLAYLIST_TYPE_MASTER
    )

  def run(self):
    if (self.master_playlist is None):
      raise Exception('Instance has not been initialized before calling run')

    stream = self.variant_streams[self.current_stream] 

    media_playlist = M3U8_Parser.parse(
      src=self.base_uri + stream.uri,
      playlist_type=M3U8_Parser.PLAYLIST_TYPE_MEDIA
    )

    for i in range(5):
      uri = self.base_uri + media_playlist.media_segments[media_playlist.ext_x_media_sequence + i].uri
      response = request('GET', uri, stream=True)
      with open(f'out/{i}.ts', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)