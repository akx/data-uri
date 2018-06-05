#!/usr/bin/env python3

import argparse
import base64
import io
import sys
import urllib.parse as up

assert sys.version_info[0] >= 3


def decode_data_uri(input, output):
    header, data = input.read().split(',', 1)
    assert header.startswith('data:')
    data = up.unquote(data)
    if header.endswith(';base64'):
        data = base64.b64decode(data)
    out = getattr(output, 'buffer', output)
    out.write(data)


def encode_data_uri(input, output, type, strip):
    if not type and hasattr(input, 'name'):
        import mimetypes
        g_type, encoding = mimetypes.guess_type(input.name)
        if g_type:
            type = g_type

    data = getattr(input, 'buffer', input).read()

    if isinstance(data, str):
        data = data.encode()

    if strip:
        data = data.strip()

    use_base64 = not all(48 <= c <= 127 for c in data)
    if use_base64:
        data = base64.b64encode(data)
    output.write('data:%s%s,' % (type, ';base64' if use_base64 else ''))
    output.write(up.quote(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data', nargs='?')
    ap.add_argument('-d', '--decode', dest='mode', action='store_const', const='decode')
    ap.add_argument('-e', '--encode', dest='mode', action='store_const', const='encode')
    ap.add_argument('-t', '--type', metavar='MIME', default='')
    ap.add_argument('-s', '--strip', action='store_true', default=False)
    ap.add_argument('-i', '--input', metavar='FILE', default=sys.stdin, type=argparse.FileType('rb'))
    ap.add_argument('-o', '--output', metavar='FILE', default=sys.stdout, type=argparse.FileType('wb'))
    args = ap.parse_args()
    args.mode = (args.mode or 'encode')
    if args.data:
        args.input = io.BytesIO(args.data.encode())
    del args.data
    if args.mode == 'decode':
        decode_data_uri(args.input, args.output)
    else:
        encode_data_uri(args.input, args.output, args.type, args.strip)


if __name__ == '__main__':
    main()