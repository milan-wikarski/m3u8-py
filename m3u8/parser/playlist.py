class M3U8_Playlist:
	def __init__(self):
		self.raw = None
		self.ext_x_version = None
		self.ext_x_independent_segments = False
		self.ext_x_start = None


class M3U8_Playlist_Master(M3U8_Playlist):
	def __init__(self):
		super(M3U8_Playlist_Master, self).__init__()
		self.variant_streams = []
		self.alternative_renditions = dict()

	def __str__(self):
		res = [
			'EXT-X-VERSION',
			f'  {self.ext_x_version}',
			'',
			'VARIANT STREAMS',
		]

		res += [f'[{i}]\n{stream.__str__()}\n\n' for i, stream in enumerate(self.variant_streams)]

		res += ['', 'ALTERNATIVE RENDITIONS']

		for key in self.alternative_renditions:
			res.append(f'[{key}]')
			for i, rendition in enumerate(self.alternative_renditions[key]):
				res += [f'[{key}][{i}]', rendition.__str__(), '']
			res.append('')

		return '\n'.join(res)

	def add_stream(self, stream):
		self.variant_streams.append(stream)

	def add_rendition(self, rendition):
		if (not rendition.group_id in self.alternative_renditions):
			self.alternative_renditions[rendition.group_id] = []

		self.alternative_renditions[rendition.group_id].append(rendition)


class M3U8_Playlist_Media(M3U8_Playlist):
	def __init__(self):
		super(M3U8_Playlist_Media, self).__init__()
		self.ext_x_targetduration = None
		self.ext_x_media_sequence = 0
		self.ext_x_media_discontinuity_sequence = 0
		self.ext_x_endlist = False
		self.ext_x_playlist_type = None
		self.ext_x_i_frames_only = False
		self.media_segments = dict()

	def __str__(self):
		res = [
			'EXT-X-VERSION',
			f'  {self.ext_x_version}',
			'',
			'MEDIA SEGMENTS',
		]

		res += [f'{key}\n{self.media_segments[key].__str__()}\n' for key in self.media_segments]

		return '\n'.join(res)

	def add_segment(self, segment):
		sequence = self.ext_x_media_sequence + len(self.media_segments)
		self.media_segments[sequence] = segment

