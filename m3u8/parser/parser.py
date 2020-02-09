import re
from requests import request
from m3u8.util.iterator import Iterator
from m3u8.util.url_validator import URLValidator
from m3u8.parser.variant_stream import M3U8_VariantStream
from m3u8.parser.alternative_rendition import M3U8_AlternativeRendition
from m3u8.parser.media_segment import M3U8_MediaSegment
from m3u8.parser.attribute_list import M3U8_AttributeListFactory
from m3u8.parser.playlist import M3U8_Playlist_Master, M3U8_Playlist_Media
from m3u8.parser.ext_x_start import M3U8_Ext_X_Start

class M3U8_Parser:
	PLAYLIST_TYPE_MASTER = 0
	PLAYLIST_TYPE_MEDIA = 1

	BASIC_TAGS = {
		'#EXTM3U',												 # (4.3.1.1) ✓
		'#EXT-X-VERSION'									 # (4.3.1.2) ✓
	}

	MASTER_PLAYLIST_TAGS = {
		'#EXT-X-MEDIA',                    # (4.3.4.1) ✓
		'#EXT-X-STREAM-INF',               # (4.3.4.2) ✓
		'#EXT-X-I-FRAME-STREAM-INF',       # (4.3.4.3)
		'#EXT-X-SESSION-DATA',             # (4.3.4.4)
		'#EXT-X-SESSION-KEY'               # (4.3.4.5)
	}

	MEDIA_PLAYLIST_TAGS = {
		'#EXT-X-TARGETDURATION',           # (4.3.3.1) ✓
		'#EXT-X-MEDIA-SEQUENCE',           # (4.3.3.2) ✓
		'#EXT-X-DISCONTINUITY-SEQUENCE',   # (4.3.3.3) ✓
		'#EXT-X-ENDLIST',								   # (4.3.3.4) ✓
		'#EXT-X-PLAYLIST-TYPE',					   # (4.3.3.5) ✓
		'#EXT-X-I-FRAMES-ONLY'						 # (4.3.3.6) ✓
	}

	MEDIA_OR_MASTER_PLAYLIST_TAGS = {
		'#EXT-X-INDEPENDENT-SEGMENTS',     # (4.3.5.1) ✓
		'#EXT-X-START'										 # (4.3.5.2) ✓
	}

	MEDIA_SEGMENT_TAGS = {
		'#EXTINF',                         # (4.3.2.1) ✓
		'#EXT-X-BYTERANGE',                # (4.3.2.2) ✓
		'#EXT-X-DISCONTINUITY',            # (4.3.2.3) ✓
		'#EXT-X-KEY',                      # (4.3.2.4)
		'#EXT-X-MAP',                      # (4.3.2.5)
		'#EXT-X-PROGRAM-DATE-TIME',        # (4.3.2.6) ✓
		'#EXT-X-DATERANGE'                 # (4.3.2.7)
	}

	@staticmethod
	def parse(src, master_playlist=None):
		# Check playlist type
		if (master_playlist is None):
			playlist_type = M3U8_Parser.PLAYLIST_TYPE_MASTER
			parsed = M3U8_Playlist_Master()
		else:
			playlist_type = M3U8_Parser.PLAYLIST_TYPE_MEDIA
			parsed = M3U8_Playlist_Media()
			parsed.ext_x_independent_segments = master_playlist.ext_x_independent_segments
			segment = None

		if (URLValidator.is_valid(src)):
			src = request('GET', src).text

		parsed.raw = src

		first_line = True

		# Split document into lines
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

			# 2: Line starts with #
			elif (line[0] == '#'):
				# This line is a comment
				if (line[1:4] != 'EXT'):
					continue

				if (':' in line):
					key, value = line.split(':')
				else:
					key = line

				# #
				# Basic tags
				# (https://tools.ietf.org/html/rfc8216#section-4.3.1)
				#
				if (key in M3U8_Parser.BASIC_TAGS):

					# EXT-X-VERSION (https://tools.ietf.org/html/rfc8216#section-4.3.1.2)
					if (key == '#EXT-X-VERSION'):
						if (parsed.ext_x_version is not None):
							raise Exception('Multiple lines with #EXT-X-VERSION')
						parsed.ext_x_version = int(value)
					
				# #
				# Master Playlist tags
				# (https://tools.ietf.org/html/rfc8216#section-4.3.4)
				#
				elif (key in M3U8_Parser.MASTER_PLAYLIST_TAGS):

					if (playlist_type == M3U8_Parser.PLAYLIST_TYPE_MEDIA):
							raise Exception(f'{key} not valid in media playlist')

					# EXT-X-MEDIA (4.3.4.1)
					if (key == '#EXT-X-MEDIA'):
						attr_list = M3U8_AttributeListFactory.create(value)
						alternative_rendition = M3U8_AlternativeRendition(attr_list)						
						parsed.add_rendition(alternative_rendition)

					# EXT-X-STREAM-INF (4.3.4.2)
					if (key == '#EXT-X-STREAM-INF'):
						attr_list = M3U8_AttributeListFactory.create(value)
						url = iterator.next()
						variant_stream = M3U8_VariantStream(attr_list, url)
						parsed.add_stream(variant_stream)

				# #
				# Media Playlist tags
				# (https://tools.ietf.org/html/rfc8216#section-4.3.3)
				#
				elif (key in M3U8_Parser.MEDIA_PLAYLIST_TAGS):

					if (playlist_type == M3U8_Parser.PLAYLIST_TYPE_MASTER):
						raise Exception(f'{key} is not valid in master playlist')

					# EXT-X-TARGETDURATION (4.3.3.1)
					if (key == '#EXT-X-TARGETDURATION'):
						parsed.ext_x_targetduration = int(value)

					# EXT-X-MEDIA-SEQUENCE (4.3.3.2)
					elif (key == '#EXT-X-MEDIA-SEQUENCE'):
						if (len(parsed.media_segments) > 0):
							raise Exception('#EXT-X-MEDIA-SEQUENCE has to appear before the first media segment')
						parsed.ext_x_media_sequence = int(value)

					# EXT-X-DISCONTINUITY-SEQUENCE (4.3.3.3)
					elif (key == '#EXT-X-DISCONTINUITY-SEQUENCE'):
						if (len(parsed.media_segments) > 0):
							raise Exception('#EXT-X-DISCONTINUITY-SEQUENCE has to appear before the first media segment')
						parsed.ext_x_media_discontinuity_sequence = int(value)

					# EXT-X-ENDLIST (4.3.3.4)
					elif (key == '#EXT-X-ENDLIST'):
						parsed.ext_x_endlist = True

					# EXT-X-PLAYLIST-TYPE (4.3.3.5)
					elif (key == '#EXT-X-PLAYLIST-TYPE'):
						if (value != 'EVENT' and value != 'VOD'):
							raise Exception(f'{value} is not a valid value of #EXT-X-PLAYLIST-TYPE')
						parsed.ext_x_playlist_type = value

					# EXT-X-I-FRAMES-ONLY (4.3.3.6)
					elif (key == '#EXT-X-I-FRAMES-ONLY'):
						parsed.ext_x_i_frames_only = True

				# #
				# Media or Master Playlist tags
				# (https://tools.ietf.org/html/rfc8216#section-4.3.5)
				#
				elif (key in M3U8_Parser.MEDIA_OR_MASTER_PLAYLIST_TAGS):
					
					# EXT-X-INDEPENDENT-SEGMENTS (4.3.5.1)
					if (key == '#EXT-X-INDEPENDENT-SEGMENTS'):
						parsed.ext_x_independent_segments = True

					# EXT-X-START (4.3.5.2)
					elif (key == '#EXT-X-START'):
						attr_list = M3U8_AttributeListFactory.create(value)
						parsed.ext_x_start = M3U8_Ext_X_Start(attr_list)

				# #
				# Media Segment tags
				# (https://tools.ietf.org/html/rfc8216#section-4.3.2)
				# 
				elif (key in M3U8_Parser.MEDIA_SEGMENT_TAGS):

					if (playlist_type == M3U8_Parser.PLAYLIST_TYPE_MASTER):
							raise Exception(f'{key} not valid in master playlist')

					if (segment is None):
						segment = M3U8_MediaSegment()

					# EXTINF (4.3.2.1)
					if (key == '#EXTINF'):
						duration, title = value.split(',')
						segment.duration = float(duration)
						segment.title = title

					# EXT-X-BYTERANGE (4.3.2.2)
					elif (key == '#EXT-X-BYTERANGE'):
						value = value.split('@')
						segment.byterange = int(value[0])
						if (len(value) > 1):
							segment.byterange_offset = int(value[1])
						else:
							prev_segment = parsed.media_segments[-1]
							segment.byterange_offset = prev_segment.byterange_offset + prev_segment.byterange + 1

					# EXT-X-DISCONTINUITY (4.3.2.3)
					elif (key == '#EXT-X-DISCONTINUITY'):
						segment.discontinuity = True

					# EXT-X-PROGRAM-DATE-TIME (4.3.2.6)
					elif (key == '#EXT-X-PROGRAM-DATE-TIME'):
						segment.program_datetime = value

			
			# 3: Line is a URL
			else:
				segment.url = line
				parsed.add_segment(segment)
				segment = None

		return parsed
