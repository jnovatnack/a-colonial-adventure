import numpy as np
from PIL import Image
from scipy import ndimage

OUT = (28, 20, 30)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def bayer_tile(h, w):
    return np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


# ---------------------------------------------------------------- sprites
def region_sprite(rows, mats, details=(), outline=OUT):
    """Flat region art -> auto shaded sprite with outline (light from top-left)."""
    h = len(rows)
    w = len(rows[0])
    for r in rows:
        assert len(r) == w, (r, len(r), w)
    g = [['.'] * (w + 2)] + [['.'] + list(r) + ['.'] for r in rows] + [['.'] * (w + 2)]
    H, W = h + 2, w + 2
    img = np.zeros((H, W, 4), np.uint8)

    def nb(y, x, k):
        if not (0 <= y < H and 0 <= x < W):
            return '.'
        n = g[y][x]
        return k if (n in details and n != '.') else n

    for y in range(H):
        for x in range(W):
            k = g[y][x]
            if k == '.':
                ns = [g[yy][xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                      if 0 <= yy < H and 0 <= xx < W]
                if any(n != '.' for n in ns):
                    img[y, x] = (*outline, 255)
                continue
            m = mats[k]
            if len(m) == 1:
                col = m[0]
            else:
                hi, base, sh = m
                if nb(y + 1, x, k) != k or nb(y, x + 1, k) != k:
                    col = sh
                elif nb(y - 1, x, k) != k or nb(y, x - 1, k) != k:
                    col = hi
                else:
                    col = base
            img[y, x] = (*col, 255)
    return img


def add_outline(spr, outline=OUT):
    a = spr[..., 3] > 0
    p = np.pad(a, 1)
    s = np.pad(spr, ((1, 1), (1, 1), (0, 0)))
    ring = ndimage.binary_dilation(p, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~p
    s[ring] = (*outline, 255)
    return s


def mirror(spr):
    return spr[:, ::-1].copy()


def save(spr, path, scale=1):
    im = Image.fromarray(spr if spr.shape[2] == 4 else spr.astype(np.uint8))
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


# ---------------------------------------------------------------- masks
def erode(m, n=1):
    for _ in range(n):
        p = np.pad(m, 1, mode='edge')
        m = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return m


def dilate(m, n=1):
    for _ in range(n):
        p = np.pad(m, 1, mode='edge')
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def above(m):  # value of the pixel above
    a = np.zeros_like(m)
    a[1:] = m[:-1]
    return a


def below(m):
    a = np.zeros_like(m)
    a[:-1] = m[1:]
    return a


def thick_path(shape, pts, r, rng, wob=1.2):
    h, w = shape
    m = np.zeros(shape, bool)
    yy, xx = np.mgrid[0:h, 0:w]
    pts = [np.array(p, float) for p in pts]
    # catmull-rom
    P = [pts[0]] + pts + [pts[-1]]
    samples = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        L = int(np.linalg.norm(p2 - p1)) + 1
        for t in np.linspace(0, 1, L * 2):
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            samples.append(q)
    ph = rng.uniform(0, 6.28)
    for i, q in enumerate(samples):
        rr = r + wob * np.sin(i * 0.07 + ph) + 0.6 * np.sin(i * 0.23 + ph * 2)
        x0, x1 = int(q[0] - rr - 1), int(q[0] + rr + 2)
        y0, y1 = int(q[1] - rr - 1), int(q[1] + rr + 2)
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, w), min(y1, h)
        if x0 >= x1 or y0 >= y1:
            continue
        sub = (xx[y0:y1, x0:x1] - q[0]) ** 2 + (yy[y0:y1, x0:x1] - q[1]) ** 2 <= rr * rr
        m[y0:y1, x0:x1] |= sub
    return m


def ellipse(shape, cx, cy, rx, ry):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1


def value_noise(h, w, cell, rng):
    gh, gw = h // cell + 3, w // cell + 3
    g = rng.random((gh, gw))
    yy, xx = np.mgrid[0:h, 0:w] / cell
    x0 = xx.astype(int)
    y0 = yy.astype(int)
    fx = xx - x0
    fy = yy - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


# ---------------------------------------------------------------- scene
class Scene:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = np.zeros((h, w, 3), float)
        self.objs = []
        self.shape = (h, w)

    def fill(self, mask, col):
        self.img[mask] = col

    def put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img[y, x] = col

    def darken(self, mask, f=(0.62, 0.66, 0.80)):
        self.img[mask] *= np.array(f)

    def blit(self, spr, x, y):
        h, w = spr.shape[:2]
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        dx1, dy1 = min(self.w, x + w), min(self.h, y + h)
        if dx0 >= dx1 or dy0 >= dy1:
            return
        sub = spr[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
        m = sub[..., 3] > 0
        self.img[dy0:dy1, dx0:dx1][m] = sub[..., :3][m]

    def shadow_of(self, spr, x, y, dx, dy, f=(0.62, 0.66, 0.80)):
        h, w = spr.shape[:2]
        m = np.zeros(self.shape, bool)
        a = spr[..., 3] > 0
        for yy in range(h):
            ty = y + yy + dy
            if not (0 <= ty < self.h):
                continue
            for xx in range(w):
                tx = x + xx + dx
                if a[yy, xx] and 0 <= tx < self.w:
                    m[ty, tx] = True
        self.darken(m, f)

    def foot_shadow(self, cx, cy, rx, ry, f=(0.62, 0.66, 0.80)):
        self.darken(ellipse(self.shape, cx, cy, rx, ry), f)

    def add(self, spr, x, y, key=None):
        self.objs.append((key if key is not None else y + spr.shape[0], len(self.objs), spr, x, y))

    def flush(self):
        for k, _, spr, x, y in sorted(self.objs, key=lambda o: (o[0], o[1])):
            self.blit(spr, x, y)
        self.objs = []

    def to_image(self):
        return np.clip(self.img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- terrain
def grass(sc, tones, rng, density=1.0, flowers=None, leaves=None):
    dk, md, bs, lt, hi = tones
    h, w = sc.shape
    n = value_noise(h, w, 22, rng)
    B = bayer_tile(h, w)
    v = n + (B - 0.5) * 0.28
    sc.img[:] = bs
    sc.img[v < 0.36] = md
    sc.img[v > 0.74] = lt
    # tufts
    step = 7
    for gy in range(0, h, step):
        for gx in range(0, w, step):
            if rng.random() > 0.55 * density:
                continue
            x = gx + rng.integers(0, step)
            y = gy + rng.integers(0, step)
            kind = rng.integers(0, 3)
            if kind == 0:
                for dx, dy, c in ((0, 0, dk), (2, 0, dk), (1, 1, dk), (0, -1, lt), (2, -1, lt)):
                    sc.put(x + dx, y + dy, c)
            elif kind == 1:
                for dx, dy, c in ((0, 0, dk), (1, 1, dk), (2, 0, dk), (3, 1, dk), (4, 0, dk), (2, -1, hi), (0, -1, lt), (4, -1, lt)):
                    sc.put(x + dx, y + dy, c)
            else:
                for dx, dy, c in ((0, 0, md), (1, -1, hi), (2, 0, md)):
                    sc.put(x + dx, y + dy, c)
    if flowers:
        for _ in range(flowers[0]):
            x, y = rng.integers(0, w), rng.integers(0, h)
            col = flowers[1][rng.integers(0, len(flowers[1]))]
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                sc.put(x + dx, y + dy, col)
            sc.put(x, y, (248, 216, 96))
    if leaves:
        for _ in range(leaves[0]):
            x, y = rng.integers(0, w), rng.integers(0, h)
            col = leaves[1][rng.integers(0, len(leaves[1]))]
            sc.put(x, y, col)
            if rng.random() < 0.5:
                sc.put(x + 1, y, col)
            sc.put(x, y + 1, mix(col, (40, 30, 30), 0.45))


def dirt(sc, mask, tones, rng, lip=None, pebbles=60):
    dk, md, bs, lt, hi = tones
    h, w = sc.shape
    n = value_noise(h, w, 9, rng)
    B = bayer_tile(h, w)
    v = n + (B - 0.5) * 0.3
    inner = erode(mask, 2)
    ring2 = erode(mask, 1) & ~inner
    ring1 = mask & ~erode(mask, 1)
    col = np.zeros((h, w, 3))
    col[:] = bs
    col[v > 0.68] = lt
    col[v < 0.25] = md
    sc.img[inner] = col[inner]
    sc.img[ring2] = md
    sc.img[ring1] = dk
    # grass overhang shadow on top edges
    top = mask & ~above(mask)
    top2 = mask & above(top)
    sc.img[top2] = dk
    sc.img[top] = mix(dk, (30, 20, 30), 0.35)
    if lip is not None:
        lipm = ~mask & dilate(mask, 1)
        sc.img[lipm] = lip
    ys, xs = np.nonzero(inner)
    for i in rng.choice(len(ys), size=min(pebbles, len(ys)), replace=False):
        y, x = ys[i], xs[i]
        if inner[min(y + 1, h - 1), x] and inner[y, min(x + 1, w - 1)]:
            sc.put(x, y, hi)
            sc.put(x + 1, y, lt)
            sc.put(x, y + 1, md)
            sc.put(x + 1, y + 1, dk)


def water(sc, mask, tones, rng, bank=None, sparkle=True):
    edge, deep, bs, lt, hi = tones
    h, w = sc.shape
    n = value_noise(h, w, 14, rng)
    B = bayer_tile(h, w)
    v = n + (B - 0.5) * 0.3
    col = np.zeros((h, w, 3))
    col[:] = bs
    col[v < 0.3] = deep
    sc.img[mask] = col[mask]
    d = [mask]
    for i in range(4):
        d.append(erode(d[-1], 1))
    shallow = d[1] & ~d[3]
    sc.img[shallow & ~d[2]] = lt
    sc.img[d[2] & ~d[3]] = mix(lt, bs, 0.5)
    # shadow from bank above
    land_above = mask & ~above(mask)
    s1 = land_above
    s2 = mask & above(s1)
    s3 = mask & above(s2)
    for s in (s1, s2, s3):
        sc.img[s] = deep
    sc.img[mask & ~d[1]] = edge
    if bank is not None:
        b1 = ~mask & dilate(mask, 1)
        b2 = ~mask & dilate(mask, 2) & ~b1
        sc.img[b2] = bank[0]
        sc.img[b1] = bank[1]
    # wave highlights
    inner = d[3]
    for gy in range(0, h, 6):
        for gx in range(0, w, 11):
            x = gx + rng.integers(0, 9)
            y = gy + rng.integers(0, 4)
            L = rng.integers(3, 6)
            if all(0 <= x + k < w and 0 <= y < h and inner[y, x + k] for k in range(L)):
                for k in range(L):
                    sc.put(x + k, y, lt)
                sc.put(x + 1, y - 1 if y > 0 else y, lt)
                if sparkle and rng.random() < 0.35:
                    sc.put(x + L // 2, y, hi)


# ---------------------------------------------------------------- trees
def make_tree(R, tones, rng, fruit=None, trunk=((156, 108, 72), (112, 72, 48), (72, 44, 36)), blossoms=None):
    dk, md, bs, lt = tones
    W = 2 * R + 6
    trunkH = R // 2 + 5
    cy = int(R * 0.92) + 2
    H = cy + int(R * 0.85) + trunkH
    cx = W / 2
    clumps = []
    clumps.append((cx, cy - R * 0.1, R * 0.62))
    k = 7
    a0 = rng.uniform(0, 6.28)
    for i in range(k):
        a = a0 + i * 6.283 / k + rng.uniform(-0.25, 0.25)
        d = R * rng.uniform(0.46, 0.56)
        clumps.append((cx + np.cos(a) * d, cy + np.sin(a) * d * 0.86, R * rng.uniform(0.44, 0.54)))
    for i in range(3):
        clumps.append((cx + rng.uniform(-R * 0.45, R * 0.45), cy + R * rng.uniform(0.15, 0.45), R * rng.uniform(0.32, 0.42)))
    clumps.sort(key=lambda c: c[1])
    yy, xx = np.mgrid[0:H, 0:W]
    label = -np.ones((H, W), int)
    for i, (ux, uy, ur) in enumerate(clumps):
        m = ((xx - ux) / ur) ** 2 + ((yy - uy) / (ur * 0.92)) ** 2 <= 1
        label[m] = i
    can = label >= 0
    B = bayer_tile(H, W)
    spr = np.zeros((H, W, 4), np.uint8)
    # trunk
    tx0 = int(cx - 3)
    ty0 = int(cy + R * 0.3)
    for y in range(ty0, H - 1):
        flare = 1 if y >= H - 3 else 0
        for x in range(tx0 - flare, tx0 + 6 + flare):
            u = (x - tx0) / 6
            c = trunk[0] if u < 0.3 else (trunk[1] if u < 0.75 else trunk[2])
            if (y * 3 + x) % 7 == 0:
                c = trunk[2]
            spr[y, x] = (*c, 255)
    tones4 = [dk, md, bs, lt]
    for y in range(H):
        for x in range(W):
            i = label[y, x]
            if i < 0:
                continue
            ux, uy, ur = clumps[i]
            dx, dy = (x - ux) / ur, (y - uy) / ur
            light = -(dx * 0.62 + dy * 0.78)
            v = 0.42 + 0.42 * light - 0.22 * ((y - cy) / R) + (B[y, x] - 0.5) * 0.32
            t = 0 if v < 0.12 else (1 if v < 0.42 else (2 if v < 0.72 else 3))
            # crevice under front clumps
            for ny, nx in ((y + 1, x), (y, x + 1), (y - 1, x), (y, x - 1), (y + 1, x + 1)):
                if 0 <= ny < H and 0 <= nx < W and label[ny, nx] > i:
                    t = 0
                    break
            spr[y, x] = (*tones4[t], 255)
    if fruit or blossoms:
        ys, xs = np.nonzero(can & erode(can, 2))
        cnt = 0
        for j in rng.permutation(len(ys)):
            y, x = ys[j], xs[j]
            if tuple(spr[y, x, :3]) in (tuple(bs), tuple(lt)) and y > cy - R * 0.5:
                if fruit:
                    spr[y, x] = (*fruit[0], 255)
                    spr[y + 1, x] = (*fruit[1], 255)
                    spr[y, x + 1] = (*fruit[1], 255)
                    spr[y - 1, x] = (*mix(fruit[0], (255, 255, 255), 0.5), 255) if spr[y - 1, x, 3] else spr[y - 1, x]
                else:
                    c = blossoms[cnt % len(blossoms)]
                    spr[y, x] = (*c, 255)
                    spr[y, x + 1] = (*c, 255)
                cnt += 1
                if cnt >= (9 if fruit else 26):
                    break
    return add_outline(spr)


def make_pine(Hh, tones, rng, trunk=((120, 84, 60), (88, 60, 44), (60, 40, 32))):
    dk, md, bs, lt = tones
    tiers = 4
    W = int(Hh * 0.7) | 1
    H = Hh + 5
    cx = W // 2
    spr = np.zeros((H, W, 4), np.uint8)
    for y in range(Hh, H - 1):
        for x in range(cx - 2, cx + 3):
            c = trunk[0] if x < cx else (trunk[1] if x == cx else trunk[2])
            spr[y, x] = (*c, 255)
    B = bayer_tile(H, W)
    for t in range(tiers):
        top = int(t * Hh * 0.2)
        bot = int(Hh * (0.36 + t * 0.21))
        bot = min(bot, Hh + 1)
        hw = W / 2 * (0.42 + 0.19 * t)
        for y in range(top, bot):
            f = (y - top) / max(1, bot - top)
            half = hw * f
            for x in range(W):
                dx = x - cx
                saw = 1.5 * abs(((x * 0.5) % 2) - 1) if y > bot - 3 else 0
                if abs(dx) <= half and y < bot - saw:
                    u = dx / max(half, 1)
                    v = 0.55 - 0.5 * u - 0.35 * f + (B[y, x] - 0.5) * 0.3
                    if y < top + 2 and t > 0:
                        v -= 0.35
                    c = dk if v < 0.05 else (md if v < 0.35 else (bs if v < 0.62 else lt))
                    spr[y, x] = (*c, 255)
    return add_outline(spr)


# ---------------------------------------------------------------- buildings
def make_house(W, roofH, wallH, roof, wall, trim, door_col, style='clap', windows=(), door_x=None,
               chimneys=(), shutters=None, glass=((40, 52, 84), (96, 136, 184)), lit=None, brick=None,
               door_w=8, win_h=8):
    over = 2
    H = roofH + wallH + 2
    spr = np.zeros((H, W, 4), np.uint8)

    def S(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            spr[y, x] = (*c, 255)

    wx0, wx1 = over, W - over - 1
    rhi, rbs, rsh, rdk = roof
    whi, wbs, wsh = wall
    for y in range(roofH, roofH + wallH):
        ry = y - roofH
        for x in range(wx0, wx1 + 1):
            if style == 'clap':
                c = (whi, wbs, wsh)[ry % 3]
            elif style == 'log':
                k = ry % 4
                c = (whi, wbs, wbs, wsh)[k]
                if k == 3 and (x * 7 + ry) % 11 == 0:
                    c = whi
            elif style == 'brick':
                row = ry // 3
                off = (row % 2) * 3
                if ry % 3 == 2 or (x + off) % 6 == 0:
                    c = brick[3]
                else:
                    hsh = ((x + off) // 6 * 7 + row * 13) % 5
                    c = brick[0] if hsh == 0 else (brick[2] if hsh == 1 else brick[1])
            else:
                c = wbs
            S(x, y, c)
    # roof shadow on wall
    for x in range(wx0, wx1 + 1):
        for k in range(2):
            y = roofH + k
            c = spr[y, x, :3]
            S(x, y, tuple(int(v * 0.6) for v in c))
    if style == 'clap':
        for y in range(roofH + 2, roofH + wallH):
            S(wx0, y, trim[0]); S(wx0 + 1, y, trim[1])
            S(wx1 - 1, y, trim[1]); S(wx1, y, trim[2])
    if style == 'log':
        for y in range(roofH + 1, roofH + wallH, 4):
            for cxx in (wx0, wx1):
                for dx, dy, c in ((-1, 0, (196, 156, 104)), (0, 0, (176, 132, 84)), (1, 0, (196, 156, 104)),
                                  (-1, 1, (176, 132, 84)), (0, 1, (120, 84, 52)), (1, 1, (176, 132, 84)),
                                  (0, 2, (140, 96, 60))):
                    S(cxx + dx, y + dy, c)
    # windows
    wy = roofH + 3
    for wxx in windows:
        if shutters:
            for y in range(wy, wy + win_h + 1):
                for sx in (wxx - 3, wxx - 2, wxx + 8, wxx + 9):
                    S(sx, y, shutters[0] if (y - wy) % 2 == 0 else shutters[1])
        for y in range(wy - 1, wy + win_h + 1):
            for x in range(wxx - 1, wxx + 8):
                S(x, y, trim[1])
        for y in range(wy, wy + win_h):
            for x in range(wxx, wxx + 7):
                gl = glass[0]
                if lit:
                    gl = lit[0] if (x + y) % 3 else lit[1]
                S(x, y, gl)
        for x in range(wxx, wxx + 7):
            S(x, wy + win_h // 2, trim[2] if not lit else lit[2])
        for y in range(wy, wy + win_h):
            S(wxx + 3, y, trim[2] if not lit else lit[2])
        if not lit:
            S(wxx + 1, wy + 1, glass[1]); S(wxx + 4, wy + 1, glass[1]); S(wxx + 1, wy + 2, glass[1])
        for x in range(wxx - 1, wxx + 8):
            S(x, wy + win_h, trim[0])
    # door
    if door_x is not None:
        dh = min(wallH - 3, 13)
        dy0 = roofH + wallH - dh
        for y in range(dy0 - 1, roofH + wallH):
            for x in range(door_x - 1, door_x + door_w + 1):
                S(x, y, trim[1])
        for y in range(dy0, roofH + wallH):
            for x in range(door_x, door_x + door_w):
                c = door_col[1]
                if x == door_x:
                    c = door_col[0]
                if x == door_x + door_w - 1:
                    c = door_col[2]
                if (y - dy0) in (2, 7) and door_x < x < door_x + door_w - 1:
                    c = door_col[2]
                S(x, y, c)
        S(door_x + door_w - 2, dy0 + dh // 2 + 1, (240, 200, 96))
        for x in range(door_x - 2, door_x + door_w + 2):
            S(x, roofH + wallH, (168, 164, 160)); S(x, roofH + wallH + 1, (112, 108, 112))
    # roof
    ridge = max(3, int(roofH * 0.36))
    for y in range(roofH):
        for x in range(W):
            if y < ridge:
                k = y % 2
                c = rsh if k == 0 else rdk
                if (x + (y // 2) * 2) % 5 == 0:
                    c = rdk
            elif y < ridge + 2:
                c = rhi if y == ridge else rbs
            else:
                ry = y - ridge - 2
                row = ry // 3
                k = ry % 3
                c = (rhi, rbs, rsh)[k]
                if (x + (row % 2) * 3) % 6 == 0 and k != 0:
                    c = rdk
            if x == 0:
                c = rhi
            if x == W - 1:
                c = rdk
            S(x, y, c)
    for x in range(W):
        S(x, roofH - 1, rdk)
    for (chx, chw) in chimneys:
        for y in range(ridge - 7, ridge + 3):
            for x in range(chx, chx + chw):
                row = (y - ridge) // 2
                c = (172, 76, 60) if ((x + (row % 2) * 2) % 4 and y % 2) else (132, 56, 48)
                if y == ridge - 7:
                    c = (88, 80, 84)
                if x == chx:
                    c = (196, 100, 76) if y != ridge - 7 else c
                S(x, y, c)
    spr = np.pad(spr, ((8, 0), (0, 0), (0, 0)))  # room for chimneys
    return add_outline(spr)


def make_tower(white=((252, 248, 236), (224, 220, 212), (176, 172, 176)), slate=((120, 128, 148), (88, 94, 116), (60, 64, 84), (40, 42, 58))):
    W = 22
    H = 76
    spr = np.zeros((H, W, 4), np.uint8)

    def S(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            spr[y, x] = (*c, 255)
    # base block rows 46..75
    for y in range(46, 76):
        for x in range(1, 21):
            c = white[(y - 46) % 3]
            if x <= 2:
                c = white[0]
            if x >= 19:
                c = white[2]
            S(x, y, c)
    for x in range(1, 21):
        S(x, 46, (112, 108, 116))
    # door
    for y in range(62, 76):
        for x in range(7, 15):
            c = (88, 52, 40) if 7 < x < 14 else (232, 228, 220)
            if y == 62:
                c = (232, 228, 220)
            S(x, y, c)
    S(12, 69, (240, 200, 96))
    # round window
    for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (1, -1), (-1, -1), (1, 1), (-1, 1)):
        S(10 + dx + 1, 52 + dy, (40, 52, 84))
    S(10, 51, (96, 136, 184))
    # belfry rows 28..45
    for y in range(28, 46):
        for x in range(3, 19):
            c = white[1]
            if x <= 4:
                c = white[0]
            if x >= 17:
                c = white[2]
            S(x, y, c)
    for (ax) in (6, 12):
        for y in range(31, 43):
            for x in range(ax, ax + 4):
                if y == 31 and x in (ax, ax + 3):
                    continue
                S(x, y, (36, 32, 48))
    for x in range(9, 13):
        S(x, 38, (232, 184, 72)); S(x, 39, (184, 132, 48))
    S(10, 37, (248, 216, 120))
    # cap
    for y in range(22, 28):
        half = 4 + (y - 22) * 1.3
        for x in range(W):
            if abs(x - 10.5) <= half:
                c = slate[0] if x < 10.5 - half / 3 else (slate[1] if x < 10.5 + half / 3 else slate[2])
                S(x, y, c)
    # spire
    for y in range(2, 22):
        half = (y - 2) / 20 * 4.5 + 0.5
        for x in range(W):
            if abs(x - 10.5) <= half:
                c = slate[0] if x < 10.5 else slate[2]
                if (y % 4 == 0):
                    c = slate[3] if x >= 10.5 else slate[1]
                S(x, y, c)
    S(10, 0, (240, 200, 96)); S(10, 1, (200, 160, 72)); S(9, 1, (240, 200, 96)); S(11, 1, (240, 200, 96))
    return add_outline(spr)


def make_stonewall(L, rng, pal=((196, 192, 184), (156, 152, 148), (112, 108, 112)), gap=(56, 52, 60)):
    H = 9
    spr = np.zeros((H, L, 4), np.uint8)
    spr[..., :3] = gap
    spr[..., 3] = 255
    for row, (y0, y1) in enumerate(((0, 4), (4, 9))):
        x = -rng.integers(0, 4)
        while x < L:
            sw = rng.integers(4, 8)
            tint = rng.uniform(-14, 10)
            hi, bs, sh = [tuple(int(np.clip(c + tint + (6 if row == 0 else -10), 0, 255)) for c in p) for p in pal]
            for yy in range(y0, y1 - 1 if row == 0 else y1):
                for xx in range(x + 1, x + sw):
                    if not (0 <= xx < L):
                        continue
                    corner = (yy in (y0, y1 - 1 - (1 if row == 0 else 0))) and (xx in (x + 1, x + sw - 1))
                    if corner:
                        continue
                    c = bs
                    if yy == y0 or xx == x + 1:
                        c = hi
                    if yy >= y1 - (2 if row == 0 else 1) or xx == x + sw - 1:
                        c = sh
                    spr[yy, xx, :3] = c
            x += sw
    return add_outline(spr)


def make_rail_fence(L, wood=((176, 128, 84), (136, 96, 60), (92, 64, 44)), post_every=16):
    H = 12
    spr = np.zeros((H, L, 4), np.uint8)
    for ry in (3, 7):
        for x in range(L):
            spr[ry, x] = (*wood[0], 255)
            spr[ry + 1, x] = (*wood[2], 255)
    for px in range(1, L, post_every):
        for y in range(0, H):
            for x in range(px, px + 3):
                if x < L:
                    spr[y, x] = (*wood[0 if x == px else (1 if x == px + 1 else 2)], 255)
        spr[0, px:px + 3] = (*wood[0], 255)
    return add_outline(spr)


def make_vfence(L, wood=((176, 128, 84), (136, 96, 60), (92, 64, 44)), post_every=14):
    W = 5
    spr = np.zeros((L, W, 4), np.uint8)
    for y in range(L):
        spr[y, 1] = (*wood[0], 255)
        spr[y, 2] = (*wood[1], 255)
        spr[y, 3] = (*wood[2], 255)
    for py in range(0, L, post_every):
        for y in range(py, min(L, py + 4)):
            for x in range(0, 5):
                spr[y, x] = (*wood[0 if x < 2 else 2], 255)
    return add_outline(spr)
