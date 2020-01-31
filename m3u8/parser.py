import re
from m3u8.variant_stream import M3U8_VariantStream
from m3u8.util import Iterator
from m3u8.attribute_list import M3U8_AttributeListFactory


class M3U8_Parsed:
	def __init__(self):
		self.ext_x_version = None
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


class M3U8:
	@staticmethod
	def parse_master(src):
		parsed = M3U8_Parsed()

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

				key, value = line.split(':')

				# EXT-X-VERSION (https://tools.ietf.org/html/rfc8216#section-4.3.1.2)
				if (key == '#EXT-X-VERSION'):
					if (parsed.ext_x_version is not None):
						raise Exception('Multiple lines with #EXT-X-VERSION')
					parsed.ext_x_version = value
				
				# EXT-X-STREAM-INF (https://tools.ietf.org/html/rfc8216#section-4.3.4.2)
				elif (key == '#EXT-X-STREAM-INF'):
					attr_list = M3U8_AttributeListFactory.create(value)
					uri = iterator.next()
					variant_stream = M3U8_VariantStream(attr_list, uri)
					parsed.variant_streams.append(variant_stream)

		return parsed
