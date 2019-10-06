import os
import io
import zlib
from modfile_exceptions import ModFileException

class ModFile:

	def __init__(self, path):
		self.path = path

	def _read_string(self, stream):
		return stream.read(int.from_bytes(stream.read(1), byteorder = "little")).decode("utf-8")

	def _read_int(self, stream):
		return int.from_bytes(stream.read(4), byteorder = "little")

	def _save_file(self, file_name, file_buffer):

		# Create the directory
		save_location = "{mod_name}_unpacked/{file_name}".format(mod_name = self.mod_name, file_name = file_name)
		os.makedirs(os.path.dirname(save_location), exist_ok = True)

		with open(save_location, "wb+") as write_stream:
			write_stream.write(file_buffer)

	def _unpack_old(self, stream):
		
		deflated = io.BytesIO(zlib.decompress(stream.read(), -zlib.MAX_WBITS))

		# Mod name, mod version, mod files count
		self.mod_name		= self._read_string(deflated)
		self.mod_version	= self._read_string(deflated)
		self.mod_files		= self._read_int(deflated)

		if not self.mod_files:
			raise ModFileException("This mod has no files included!")

		for _ in range(self.mod_files):

			file_name	= self._read_string(deflated)
			file_size	= self._read_int(deflated)

			self._save_file(file_name, deflated.read(file_size))

	def _unpack_new(self, stream):

		# Mod name, mod version, mod files count
		self.mod_name		= self._read_string(stream)
		self.mod_version	= self._read_string(stream)
		self.mod_files		= self._read_int(stream)

		if not self.mod_files:
			raise ModFileException("This mod has no files included!")

		files = { }

		for _ in range(self.mod_files):

			name			= self._read_string(stream)
			size			= self._read_int(stream)
			compressed_size	= self._read_int(stream)

			files[name] = {
				"size"				: size,
				"compressed_size"	: compressed_size,
			}

		for file_name, file_data in files.items():

			size			= file_data["size"]
			compressed_size	= file_data["compressed_size"]
				
			# File is compressed
			if size != compressed_size:
				deflated = io.BytesIO(zlib.decompress(stream.read(compressed_size), -zlib.MAX_WBITS))
				self._save_file(file_name, deflated.read())

			else:
				self._save_file(file_name, stream.read(size))

	def unpack(self):

		with open(self.path, "rb") as mod_file:

			if mod_file.read(4) != b"TMOD":
				raise ModFileException("This file has invalid TMOD header!")

			# TModLoader version, mod hash, signature
			self.loader_version = self._read_string(mod_file)
			self.mod_hash       = mod_file.read(20).hex()
			self.signature      = mod_file.read(256)

			# Skip int32 (data length)
			mod_file.read(4)

			self.minor_version = int(self.loader_version.split(".")[1])

			if self.minor_version < 11:
				self._unpack_old(mod_file)
				return

			self._unpack_new(mod_file)