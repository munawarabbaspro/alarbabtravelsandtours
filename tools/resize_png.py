# Tiny dependency-free PNG downscaler (8-bit RGBA/RGB, non-interlaced). Area-averaging resize.
# usage: py tools/resize_png.py in.png out.png WIDTH [--square SIZE --bg FFFFFF]
import struct, sys, zlib

def read_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, w = 8, b"", None
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4]); typ = data[pos + 4:pos + 8]; body = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (2, 6) and inter == 0, "only 8-bit RGB/RGBA non-interlaced"
        elif typ == b"IDAT":
            idat += body
    bpp = 4 if ctype == 6 else 3
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line); prev = line
    px = [[tuple(r[x * bpp:x * bpp + bpp]) + ((255,) if bpp == 3 else ()) for x in range(w)] for r in rows]
    return w, h, px

def resize(w, h, px, nw, nh):
    out = []
    for y in range(nh):
        y0, y1 = y * h / nh, (y + 1) * h / nh
        row = []
        for x in range(nw):
            x0, x1 = x * w / nw, (x + 1) * w / nw
            acc = [0.0, 0.0, 0.0, 0.0]; area = 0.0
            for yy in range(int(y0), min(h, int(y1 + 0.999))):
                fy = min(y1, yy + 1) - max(y0, yy)
                for xx in range(int(x0), min(w, int(x1 + 0.999))):
                    fx = min(x1, xx + 1) - max(x0, xx); k = fx * fy
                    r, g, b, a = px[yy][xx]; wa = k * a / 255
                    acc[0] += r * wa; acc[1] += g * wa; acc[2] += b * wa; acc[3] += k * a; area += k
            al = acc[3] / area if area else 0
            wsum = acc[3] / 255 or 1
            row.append((round(acc[0] / wsum), round(acc[1] / wsum), round(acc[2] / wsum), round(al)))
        out.append(row)
    return out

def write_png(path, px):
    h, w = len(px), len(px[0])
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    chunk = lambda t, b: struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

if __name__ == "__main__":
    src, dst, nw = sys.argv[1], sys.argv[2], int(sys.argv[3])
    w, h, px = read_png(src)
    if "--square" in sys.argv:                      # padded square icon on a background colour
        size = int(sys.argv[sys.argv.index("--square") + 1]); bg = sys.argv[sys.argv.index("--bg") + 1]
        bgc = tuple(int(bg[i:i + 2], 16) for i in (0, 2, 4))
        nh = round(h * nw / w); small = resize(w, h, px, nw, nh)
        canvas = [[bgc + (255,)] * size for _ in range(size)]
        ox, oy = (size - nw) // 2, (size - nh) // 2
        for y in range(nh):
            for x in range(nw):
                r, g, b, a = small[y][x]; t = a / 255
                canvas[oy + y][ox + x] = tuple(round(c * t + bc * (1 - t)) for c, bc in zip((r, g, b), bgc)) + (255,)
        write_png(dst, canvas)
    else:
        nh = round(h * nw / w)
        write_png(dst, resize(w, h, px, nw, nh))
    print(dst, open(dst, "rb").read()[:4] == b"\x89PNG", len(open(dst, "rb").read()), "bytes")
