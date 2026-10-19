import numpy as np
from pix import *
import props as P
import chars as CH

NIGHT_PAL = np.array([
    (10, 8, 22), (22, 20, 44), (34, 38, 70), (50, 60, 102), (70, 90, 132), (104, 128, 162), (156, 176, 198),
    (40, 28, 40), (72, 46, 52), (112, 66, 56), (164, 96, 62), (212, 136, 70), (242, 184, 94), (255, 232, 160),
    (142, 50, 50), (200, 78, 56), (232, 236, 240)], float)


def cobbles(sc, mask, rng, pal=((176, 164, 156), (136, 126, 122), (96, 88, 90), (52, 46, 54))):
    h, w = sc.shape
    cw, ch = 7, 5
    cells = {}
    for gy in range(-1, h // ch + 2):
        for gx in range(-1, w // cw + 2):
            off = (gy % 2) * cw / 2
            cells[(gx, gy)] = (gx * cw + off + rng.uniform(-1, 1), gy * ch + rng.uniform(-0.7, 0.7), rng.uniform(-12, 12))
    lab = np.zeros((h, w), int)
    dist = np.zeros((h, w))
    loc = np.zeros((h, w, 2))
    keys = list(cells.keys())
    idx = {k: i for i, k in enumerate(keys)}
    for y in range(h):
        for x in range(w):
            if not mask[y, x]:
                continue
            gy = y // ch
            best = None
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    gx0 = int((x - ((gy + dy) % 2) * cw / 2) // cw) + dx
                    k = (gx0, gy + dy)
                    if k not in cells:
                        continue
                    cx, cy, t = cells[k]
                    d = ((x - cx) / cw) ** 2 + ((y - cy) / ch) ** 2
                    if best is None or d < best[0]:
                        best = (d, k, cx, cy)
            lab[y, x] = idx[best[1]]
            loc[y, x] = (x - best[2], y - best[3])
    for y in range(h):
        for x in range(w):
            if not mask[y, x]:
                continue
            l = lab[y, x]
            edge = (x + 1 < w and lab[y, x + 1] != l) or (y + 1 < h and lab[y + 1, x] != l)
            t = cells[keys[l]][2]
            if edge:
                c = pal[3]
            else:
                lx, ly = loc[y, x]
                if (y > 0 and lab[y - 1, x] != l) or (x > 0 and lab[y, x - 1] != l):
                    c = pal[0]
                elif lx + ly > 2:
                    c = pal[2]
                else:
                    c = pal[1]
            sc.img[y, x] = np.clip(np.array(c) + t, 0, 255)


def planks(sc, x0, y0, x1, y1, pal=((212, 168, 112), (176, 132, 84), (128, 92, 60), (72, 50, 40)), rng=None, board=4):
    for y in range(y0, y1):
        row = (y - y0) // board
        k = (y - y0) % board
        seam_off = (row * 13) % 17
        for x in range(x0, x1):
            c = pal[0] if k == 0 else (pal[1] if k < board - 1 else pal[2])
            if k == board - 1 and False:
                c = pal[3]
            if (x - x0 + seam_off) % 23 == 0:
                c = pal[3]
            if (x - x0 + seam_off) % 23 in (2, 20) and k == 1:
                c = pal[3]
            sc.put(x, y, c)
        if k == board - 1:
            for x in range(x0, x1):
                sc.put(x, y, pal[3] if (x % 2) else pal[2])


def ship(sc, x0, y0, L, Wd):
    h, w = sc.shape
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx - x0) / L
    v = (yy - (y0 + Wd / 2)) / (Wd / 2)
    width = np.where(u < 0.72, 1.0 - 0.12 * (1 - u / 0.72) ** 4, np.sqrt(np.clip(1 - ((u - 0.72) / 0.28) ** 2, 0, 1)))
    hull = (u >= 0) & (u <= 1) & (np.abs(v) <= width)
    inner = erode(hull, 3)
    rail = hull & ~inner
    sc.img[hull] = (40, 30, 34)
    # bulwark
    ring1 = hull & ~erode(hull, 1)
    ring2 = erode(hull, 1) & ~erode(hull, 2)
    ring3 = erode(hull, 2) & ~inner
    sc.img[ring2] = (150, 104, 66)
    sc.img[ring3] = (110, 72, 48)
    sc.img[ring1] = (28, 20, 30)
    top = ring2 & (yy < y0 + Wd / 2)
    sc.img[top] = (196, 146, 92)
    # deck planks running along length
    for y in range(h):
        for x in range(w):
            if inner[y, x]:
                k = (y - y0) % 3
                c = (204, 164, 110) if k == 0 else ((178, 136, 88) if k == 1 else (132, 96, 62))
                if (x + (y // 3) * 11) % 19 == 0:
                    c = (96, 66, 48)
                sc.img[y, x] = c
    # hatch
    hx, hy = int(x0 + L * 0.4), int(y0 + Wd / 2 - 6)
    for y in range(hy, hy + 12):
        for x in range(hx, hx + 14):
            c = (72, 50, 40) if (x - hx) % 3 == 0 or (y - hy) % 3 == 0 else (30, 22, 28)
            if y in (hy, hy + 11) or x in (hx, hx + 13):
                c = (150, 104, 66)
            sc.put(x, y, c)
    return hull


def mast_and_sail(sc, cx, cy, span):
    # furled sail on yard across the ship (vertical on screen)
    for y in range(cy - span, cy + span + 1):
        for x in range(cx - 3, cx + 4):
            dx = x - cx
            bulge = 3 - (1 if abs(y - cy) > span - 2 else 0)
            if abs(dx) <= bulge:
                c = (248, 240, 220) if dx < -1 else ((220, 208, 184) if dx < 2 else (168, 156, 140))
                if (y - cy) % 5 == 0:
                    c = (150, 132, 112)
                sc.put(x, y, c)
        sc.put(cx - 4, y, (28, 20, 30)); sc.put(cx + 4, y, (28, 20, 30))
    for x in range(cx - 4, cx + 5):
        sc.put(x, cy - span - 1, (28, 20, 30)); sc.put(x, cy + span + 1, (28, 20, 30))
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                c = (176, 120, 72) if dx + dy < 0 else (112, 72, 46)
                sc.put(cx + dx, cy + dy, c)
    sc.put(cx - 1, cy - 1, (220, 168, 110))


def line(sc, x0, y0, x1, y1, c):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n):
        t = i / max(1, n - 1)
        sc.put(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), c)


def build():
    rng = np.random.default_rng(7)
    sc = Scene(320, 200)
    # water
    wmask = np.zeros(sc.shape, bool)
    wmask[112:, :] = True
    W = ((20, 28, 56), (34, 54, 98), (46, 78, 130), (88, 130, 176), (210, 230, 244))
    sc.img[:] = (40, 60, 90)
    water(sc, wmask, W, rng, sparkle=False)
    # street
    smask = np.zeros(sc.shape, bool)
    smask[40:104, :] = True
    cobbles(sc, smask, rng)
    # granite quay edge
    for y in range(104, 113):
        for x in range(320):
            bx = (x + (3 if y > 108 else 0)) % 16
            c = (190, 186, 180) if y in (104, 105) else ((150, 146, 144) if y < 111 else (96, 92, 98))
            if bx == 0 or y == 108:
                c = (64, 60, 70)
            sc.put(x, y, c)
    for x in range(320):
        sc.put(x, 113, (16, 20, 40)); sc.put(x, 114, (20, 28, 56))
    # pier
    planks(sc, 100, 106, 140, 200)
    for y in range(106, 200):
        sc.put(99, y, (28, 20, 30)); sc.put(140, y, (28, 20, 30))
    for py in range(118, 200, 20):
        for (px) in (95, 139):
            for y in range(py, py + 6):
                for x in range(px, px + 6):
                    c = (120, 88, 60) if x < px + 2 else ((92, 64, 46) if x < px + 4 else (64, 44, 34))
                    if y == py:
                        c = (164, 124, 84)
                    sc.put(x, y, c)
            for x in range(px - 1, px + 7):
                sc.put(x, py + 6, (28, 20, 30))
    # ship
    hull = ship(sc, 150, 128, 156, 56)
    for (mx, span) in ((188, 30), (232, 32), (272, 26)):
        mast_and_sail(sc, mx, 156, span)
    for (mx) in (188, 232, 272):
        for ex in (152, 300):
            pass
        line(sc, mx, 156, mx - 10, 130, (60, 46, 50))
        line(sc, mx, 156, mx - 10, 182, (60, 46, 50))
    line(sc, 300, 156, 319, 152, (140, 100, 64))
    line(sc, 300, 157, 319, 153, (28, 20, 30))
    # rowboat
    rb = np.zeros(sc.shape, bool)
    rb |= ellipse(sc.shape, 52, 152, 18, 7)
    sc.img[rb] = (28, 20, 30)
    sc.img[erode(rb, 1)] = (150, 104, 66)
    sc.img[erode(rb, 2)] = (110, 74, 50)
    for x in (46, 58):
        for y in range(147, 158):
            sc.put(x, y, (176, 128, 84))
    line(sc, 40, 150, 28, 160, (200, 160, 110))
    line(sc, 64, 150, 76, 160, (200, 160, 110))
    # reflections
    for (lx) in (40, 176, 300):
        for k, y in enumerate(range(116, 150, 3)):
            hw = 3 - k // 4
            if hw < 0:
                break
            for x in range(lx - hw + rng.integers(-1, 2), lx + hw + 1):
                sc.put(x, y, (232, 176, 96) if k < 4 else (176, 120, 80))

    # buildings
    slate = ((104, 108, 128), (78, 82, 104), (56, 58, 78), (38, 38, 54))
    shingle = ((150, 112, 80), (120, 86, 60), (90, 62, 46), (62, 42, 34))
    brick = ((196, 96, 72), (164, 72, 56), (128, 52, 46), (120, 108, 104))
    trim = ((240, 232, 216), (208, 200, 188), (140, 132, 132))
    lit = ((255, 220, 128), (255, 196, 96), (150, 96, 56))
    wood_door = ((136, 92, 60), (104, 68, 46), (70, 46, 34))
    bl = []
    b1 = make_house(80, 22, 26, slate, ((0, 0, 0),) * 3, trim, wood_door, style='brick', brick=brick,
                    windows=[8, 64], door_x=34, door_w=10, lit=lit, chimneys=[(12, 7)])
    bl.append((b1, -2, -4))
    b2 = make_house(78, 22, 26, shingle, ((176, 172, 164), (144, 140, 134), (104, 100, 100)), trim, ((70, 90, 70), (52, 70, 54), (36, 48, 40)),
                    windows=[8, 62], door_x=34, lit=None, chimneys=[(50, 7)])
    bl.append((b2, 80, -4))
    b3 = make_house(82, 22, 26, slate, ((0, 0, 0),) * 3, trim, ((96, 70, 56), (72, 52, 44), (50, 36, 32)), style='brick', brick=brick,
                    windows=[10], door_x=44, door_w=20, lit=lit)
    bl.append((b3, 160, -4))
    b4 = make_house(80, 22, 26, slate, ((212, 176, 104), (180, 144, 80), (132, 104, 60)), trim, wood_door,
                    windows=[8, 34, 64], door_x=None, lit=lit, chimneys=[(30, 7)])
    bl.append((b4, 244, -4))
    for spr, x, y in bl:
        sc.shadow_of(spr, x, y, 3, 3)
    for spr, x, y in bl:
        sc.add(spr, x, y)
    # props
    for (x, y) in ((150, 80), (160, 86), (148, 90), (252, 84)):
        sc.foot_shadow(x + 6, y + 12, 6, 2)
        sc.add(P.barrel(), x, y)
    for (x, y) in ((104, 126), (116, 126), (110, 136), (128, 150), (200, 140), (212, 140), (206, 150), (256, 166)):
        sc.add(P.crate(), x, y)
    lamps = []
    for lx in (40, 176, 300):
        lp = P.lantern_post()
        sc.add(lp, lx - 4, 80)
        lamps.append((lx, 84))
    ap = CH.apprentice()
    pr = CH.minuteman(CH.PRINTER)
    sc.foot_shadow(75, 99, 7, 2)
    sc.add(ap['right'], 66, 74)
    sc.foot_shadow(97, 97, 7, 2)
    sc.add(pr['left'], 88, 70)
    sc.flush()

    # ---- night lighting + palette quantize
    base = sc.img.copy()
    h, w = sc.shape
    yy, xx = np.mgrid[0:h, 0:w]
    night = base * np.array([0.40, 0.44, 0.66]) + np.array([6, 8, 22])
    light = np.zeros((h, w))
    lights = [(x, y, 58, 1.35) for x, y in lamps] + [(75, 92, 34, 1.1), (156, 150, 30, 0.8)]
    for (b, bx, by) in bl:
        pass
    # windows
    for (wx, wy) in ((10, 6), (70, 6), (176, 6), (256, 6), (282, 6), (312, 6)):
        lights.append((wx, wy + 20, 22, 0.6))
    for (lx, ly, r, s) in lights:
        d = np.sqrt((xx - lx) ** 2 + ((yy - ly) * 1.15) ** 2)
        light += s * np.clip(1 - d / r, 0, 1) ** 1.4
    light = np.clip(light, 0, 1.2)
    warm = base * np.array([1.12, 0.96, 0.74])
    out = night * (1 - np.clip(light, 0, 1)[..., None]) + warm * np.clip(light, 0, 1)[..., None]
    # lantern glass stays bright
    glow = (base[..., 0] > 250) & (base[..., 1] > 210)
    out[glow] = (255, 236, 168)
    # quantize with ordered dither
    B = bayer_tile(h, w)[..., None]
    jit = out + (B - 0.5) * 26
    d = ((jit[:, :, None, :] - NIGHT_PAL[None, None]) ** 2 * np.array([0.35, 0.45, 0.2])).sum(-1)
    q = NIGHT_PAL[d.argmin(-1)]
    sc.img = q
    return sc


if __name__ == '__main__':
    sc = build()
    Image.fromarray(sc.to_image()).resize((960, 600), Image.NEAREST).save('out/harbor.png')
