from m3u8.parser import M3U8
from requests import request

base_url = 'https://media.cdn.adultswim.com/streams/archive/casualFridaypt3_20200131/'

master_playlist = open('examples/master.m3u8', 'r').read()
response = M3U8.parse(master_playlist, M3U8.PLAYLIST_TYPE_MASTER)

print(response)

# for i, stream in enumerate(response.variant_streams):
#   media_playlist = request('GET', base_url + stream.uri)
  
#   if (stream.resolution is not None):
#     playlist_id = f'{stream.resolution[0]}x{stream.resolution[1]}'
#   else:
#     playlist_id = 'audio'
  
#   open(f'examples/media-{playlist_id}.m3u8', 'w').write(media_playlist.text)

media_playlist = open('examples/media-1280x720.m3u8', 'r').read()
response = M3U8.parse(media_playlist, M3U8.PLAYLIST_TYPE_MEDIA)

# for key in response.media_segments:
#   segment = response.media_segments[key]
#   print(f'{key}\n{segment.__str__()}')

# print(base_url + response.media_segments)
# response = request('GET', base_url + response.media_segments[1].uri)
# print(response.text)