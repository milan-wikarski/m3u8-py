import re
from m3u8.variant_stream import M3U8_VariantStream
from m3u8.media_sequence import M3U8_MediaSequence
from m3u8.util import Iterator
from m3u8.attribute_list import M3U8_AttributeListFactory


class M3U8_Parsed:
	def __init__(self):
		self.ext_x_version = None

class M3U8_Parsed_Master(M3U8_Parsed):
	def __init__(self):
		super(M3U8_Parsed_Master, self).__init__()
		self.variant_streams = []

	def __str__(self):
		res = [
			'EXT-X-VERSION',
			f'  {self.ext_x_version}',
			'',
			'VARIANT STREAMS',
		]

		res += [stream.__str__() + '\n\n' for stream in self.variant_streams]

		return '\n'.join(res)


class M3U8_Parsed_Media(M3U8_Parsed):
	def __init__(self):
		super(M3U8_Parsed_Media, self).__init__()
		self.ext_x_targetduration = None
		self.ext_x_media_sequence = 0
		self.ext_x_media_discontinuity_sequence = 0
		self.ext_x_endlist = False
		self.ext_x_playlist_type = None
		self.ext_x_i_frames_only = False
		self.media_segments = []


class M3U8:
	PLAYLIST_TYPE_MASTER = 0
	PLAYLIST_TYPE_MEDIA = 1

	@staticmethod
	def parse(src, playlist_type):
		if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
			parsed = M3U8_Parsed_Master()
		elif (playlist_type == M3U8.PLAYLIST_TYPE_MEDIA):
			parsed = M3U8_Parsed_Media()
		else:
			raise Exception(f'{playlist_type} is not valid playlist type')

		first_line = True

		lines = []
		for line in re.split('(\n|\r\n)', src):
			if (line != '' and line != '\n' and line != '\n\r'):
				lines.append(line)

		iterator = Iterator(lines)

		while (not iterator.done):
			line = iterator.next()
			
			# 1: First line - must be EXTM3U (https://tools.ietf.org/html/rfc8216#section-4.3.1.1)
			if (first_line):
				if (line != '#EXTM3U'):
					raise Exception('First line has to start with #EXTM3U')
				first_line = False

			# 2: Lines starts with #
			elif (line[0] == '#'):
				# This line is a comment
				if (line[1:4] != 'EXT'):
					continue

				if (':' in line):
					key, value = line.split(':')
				else:
					key = line

				# EXT-X-VERSION (https://tools.ietf.org/html/rfc8216#section-4.3.1.2)
				if (key == '#EXT-X-VERSION'):
					if (parsed.ext_x_version is not None):
						raise Exception('Multiple lines with #EXT-X-VERSION')
					parsed.ext_x_version = value
				
				#
				# Master Playlist tags
				#

				# EXT-X-STREAM-INF (https://tools.ietf.org/html/rfc8216#section-4.3.4.2)
				elif (key == '#EXT-X-STREAM-INF'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MEDIA):
						raise Exception('#EXT-X-STREAM-INF not valid in media playlist')
					attr_list = M3U8_AttributeListFactory.create(value)
					uri = iterator.next()
					variant_stream = M3U8_VariantStream(attr_list, uri)
					parsed.variant_streams.append(variant_stream)

				#
				# Media Playlist tags
				#

				# EXT-X-TARGETDURATION (https://tools.ietf.org/html/rfc8216#section-4.3.3.1)
				elif (key == '#EXT-X-TARGETDURATION'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-TARGETDURATION not valid in master playlist')
					parsed.ext_x_targetduration = int(value)

				# EXT-X-MEDIA-SEQUENCE (https://tools.ietf.org/html/rfc8216#section-4.3.3.2)
				elif (key == '#EXT-X-MEDIA-SEQUENCE'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-MEDIA-SEQUENCE not valid in master playlist')
					if (len(parsed.media_segments) > 0):
						raise Exception('#EXT-X-MEDIA-SEQUENCE has to appear before the first media segment')
					parsed.ext_x_media_sequence = int(value)

				# EXT-X-DISCONTINUITY-SEQUENCE (https://tools.ietf.org/html/rfc8216#section-4.3.3.3)
				elif (key == '#EXT-X-DISCONTINUITY-SEQUENCE'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-DISCONTINUITY-SEQUENCE not valid in master playlist')
					if (len(parsed.media_segments) > 0):
						raise Exception('#EXT-X-DISCONTINUITY-SEQUENCE has to appear before the first media segment')
					parsed.ext_x_media_discontinuity_sequence = int(value)

				# EXT-X-ENDLIST (https://tools.ietf.org/html/rfc8216#section-4.3.3)
				elif (key == '#EXT-X-ENDLIST'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-ENDLIST not valid in master playlist')
					parsed.ext_x_endlist = True

				# EXT-X-PLAYLIST-TYPE (https://tools.ietf.org/html/rfc8216#section-4.3.3.5)
				elif (key == '#EXT-X-PLAYLIST-TYPE'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-PLAYLIST-TYPE is not valid in master playlist')
					if (value != 'EVENT' and value != 'VOD'):
						raise Exception(f'{value} is not a valid value of #EXT-X-PLAYLIST-TYPE')
					parsed.ext_x_playlist_type = value

				# EXT-X-I-FRAMES-ONLY (https://tools.ietf.org/html/rfc8216#section-4.3.3.6)
				elif (key == '#EXT-X-I-FRAMES-ONLY'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXT-X-I-FRAMES-ONLY is not valid in master playlist')
					parsed.ext_x_i_frames_only = True

				#
				# Media Sequence tags
				#

				# EXTINF (https://tools.ietf.org/html/rfc8216#section-4.3.2.1)
				elif (key == '#EXTINF'):
					if (playlist_type == M3U8.PLAYLIST_TYPE_MASTER):
						raise Exception('#EXTINF not valid in master playlist')
					duration, title = value.split(',')
					duration = float(duration)



		return parsed
