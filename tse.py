import base64
import gzip
import io
import sys
from typing import Union


def decode_base64_gzip(data: Union[str, bytes]) -> bytes:
	"""Decode base64-encoded data then gunzip it.

	Accepts a str or bytes. Returns raw decompressed bytes.
	Raises ValueError on bad input or gzip errors.
	"""
	if isinstance(data, str):
		data = data.strip().encode('ascii')
	if not isinstance(data, (bytes, bytearray)):
		raise TypeError('data must be str or bytes')

	try:
		decoded = base64.b64decode(data)
	except Exception as e:
		raise ValueError(f'base64 decode failed: {e}') from e

	try:
		with gzip.GzipFile(fileobj=io.BytesIO(decoded)) as gz:
			return gz.read()
	except Exception as e:
		raise ValueError(f'gzip decompress failed: {e}') from e


def _self_test() -> None:
	"""Run a quick round-trip test and print result to stdout."""
	original = b"Hello from tse.py self-test\n"
	buf = io.BytesIO()
	with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
		gz.write(original)
	b64 = base64.b64encode(buf.getvalue()).decode('ascii')

	out = decode_base64_gzip(b64)
	if out == original:
		print('self-test: OK')
	else:
		print('self-test: FAILED')
		print('expected:', original)
		print('got     :', out)
		sys.exit(2)


def stream_decode_b64_gzip(infile, outfile, read_size: int = 8192) -> None:
	"""Stream base64 text from infile, gzip-decompress and write raw bytes to outfile.

	infile: file-like object opened in text or binary mode (read())
	outfile: file-like object opened in binary mode (write())
	"""
	import binascii
	import zlib

	decomp = zlib.decompressobj(16 + zlib.MAX_WBITS)  # gzip header auto-detect
	pending = b''

	while True:
		chunk = infile.read(read_size)
		if not chunk:
			break
		if isinstance(chunk, str):
			chunk = chunk.encode('ascii')
		pending += chunk

		# process multiples of 4 bytes for base64
		n = (len(pending) // 4) * 4
		if n == 0:
			continue
		to_decode, pending = pending[:n], pending[n:]
		try:
			decoded = binascii.a2b_base64(to_decode)
		except Exception as e:
			raise ValueError(f'base64 decoding failed during stream: {e}')
		out = decomp.decompress(decoded)
		if out:
			outfile.write(out)

	# final leftover
	if pending:
		try:
			decoded = binascii.a2b_base64(pending)
			outfile.write(decomp.decompress(decoded))
		except Exception as e:
			raise ValueError(f'final base64 decode failed: {e}')

	outfile.write(decomp.flush())


def stream_gzip_base64(infile, outfile, read_size: int = 8192) -> None:
	"""Stream binary infile -> gzip compress -> base64 encode -> write text to outfile.

	infile: binary file-like (read())
	outfile: text file-like (write())
	"""
	import zlib

	comp = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)  # gzip wrapper
	buf = b''
	while True:
		chunk = infile.read(read_size)
		if not chunk:
			break
		compressed = comp.compress(chunk)
		if compressed:
			buf += compressed
			# encode in multiples of 3 bytes to avoid mid-stream padding
			n = (len(buf) // 3) * 3
			if n:
				to_enc, buf = buf[:n], buf[n:]
				outfile.write(base64.b64encode(to_enc).decode('ascii'))

	tail = comp.flush()
	if tail:
		buf += tail

	if buf:
		outfile.write(base64.b64encode(buf).decode('ascii'))


def _main(argv: list[str]) -> int:
	import argparse

	p = argparse.ArgumentParser(description='Decode base64 + gzip data')
	p.add_argument('input', nargs='?', help='Base64 string to decode; if omitted read stdin')
	p.add_argument('--output', '-o', help='Write output to file (bytes).')
	p.add_argument('--encoding', '-e', help='If set, decode bytes to text using this encoding (e.g. utf-8)')
	p.add_argument('--stream', action='store_true', help='Use streaming base64->gzip decoding (low memory)')
	p.add_argument('--infile', help='Read base64 text from a file instead of stdin or positional input')
	p.add_argument('--encode', action='store_true', help='Compress input with gzip then base64-encode (reverse operation)')
	p.add_argument('--self-test', action='store_true', help='Run a built-in self-test')
	args = p.parse_args(argv)

	if args.self_test:
		_self_test()
		# streaming self-test with a larger payload (~100KB raw) to ensure stream path
		big = (b"The quick brown fox jumps over the lazy dog. " * 2500)[:100000]
		buf = io.BytesIO()
		with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
			gz.write(big)
		b64 = base64.b64encode(buf.getvalue()).decode('ascii')

		# test streaming path
		inf = io.StringIO(b64)
		outf = io.BytesIO()
		stream_decode_b64_gzip(inf, outf)
		if outf.getvalue() != big:
			print('stream self-test: FAILED', file=sys.stderr)
			return 5
		print('stream self-test: OK')
		# encode->decode roundtrip test (streaming)
		big2 = b'A' * 200000
		inb = io.BytesIO(big2)
		outb64 = io.StringIO()
		stream_gzip_base64(inb, outb64)
		outb64.seek(0)
		roundbin = io.BytesIO()
		stream_decode_b64_gzip(outb64, roundbin)
		if roundbin.getvalue() != big2:
			print('encode->decode stream self-test: FAILED', file=sys.stderr)
			return 6
		print('encode->decode stream self-test: OK')
		return 0

	# determine input source
	input_file_obj = None
	if args.infile:
		input_file_obj = open(args.infile, 'rb')
	elif args.input:
		# positional input provided
		input_file_obj = io.StringIO(args.input)
	else:
		# read from stdin (binary or text depending on mode)
		if args.stream:
			# for streaming we want text-like interface (base64) -> read from text wrapper
			try:
				input_file_obj = io.TextIOWrapper(sys.stdin.buffer, encoding='ascii')
			except Exception:
				input_file_obj = sys.stdin
		else:
			# non-streaming path reads raw bytes from stdin
			input_file_obj = sys.stdin.buffer if not sys.stdin.isatty() else io.BytesIO(b'')

	try:
		if args.encode:
			# encoding path: read binary input and write base64 text
			in_obj = open(args.infile, 'rb') if args.infile else sys.stdin.buffer
			out_obj = open(args.output, 'w', encoding='ascii') if args.output else sys.stdout
			if args.stream:
				stream_gzip_base64(in_obj, out_obj)
			else:
				# non-streaming: read full, compress, then base64
				data = in_obj.read()
				buf = io.BytesIO()
				with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
					gz.write(data)
				out_obj.write(base64.b64encode(buf.getvalue()).decode('ascii'))
			if args.infile:
				in_obj.close()
			if args.output and out_obj is not sys.stdout:
				out_obj.close()
		elif args.stream:
			# streaming decode directly to file or stdout
			out_obj = open(args.output, 'wb') if args.output else sys.stdout.buffer
			stream_decode_b64_gzip(input_file_obj, out_obj)
			if args.output:
				out_obj.close()
		else:
			# read entire input then decode in-memory
			data = input_file_obj.read()
			result = decode_base64_gzip(data)

			if args.output:
				with open(args.output, 'wb') as f:
					f.write(result)
			else:
				if args.encoding:
					try:
						text = result.decode(args.encoding)
					except Exception as e:
						print('decode to text failed:', e, file=sys.stderr)
						return 4
					sys.stdout.write(text)
				else:
					sys.stdout.buffer.write(result)
	except Exception as e:
		print('Error:', e, file=sys.stderr)
		return 3
	finally:
		if args.infile and input_file_obj:
			input_file_obj.close()

	return 0


if __name__ == '__main__':
	raise SystemExit(_main(sys.argv[1:]))

