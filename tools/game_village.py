"""Build the explorable Concord village: ground layer, object atlas, collision mask, character frames."""
import json, os
import numpy as np
from PIL import Image
from pix import *
import props as P
import chars as CH

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'village')
os.makedirs(OUT, exist_ok=True)
MW, MH = 480, 352


# ------------------------------------------------------------ walk frames
def raise_half(rows, n, left, mid=8):
    g = [list(r) for r in rows]
    H, W = len(g), len(g[0])
    out = [r[:] for r in g]
    for y in range(H - n, H):
        for x in range(W):
            if (x < mid) == left:
                out[y][x] = g[y + 1][x] if y + 1 < H else '.'
    return [''.join(r) for r in out]


def stride(rows, n, mid):
    g = [list(r) for r in rows]
    H, W = len(g), len(g[0])
    out = [r[:] for r in g]
    for y in range(H - n, H):
        for x in range(W):
            if x < mid:
                out[y][x] = g[y][x + 1] if x + 1 < W and x + 1 < mid else '.'
            else:
                out[y][x] = g[y][x - 1] if x - 1 >= mid else '.'
    return [''.join(r) for r in out]


def frames(down, up, left, mats, n, side_mid=7):
    b = lambda r: region_sprite(r, mats, details=CH.DET)
    d = [b(down), b(raise_half(down, n, True)), b(raise_half(down, n, False))]
    u = [b(up), b(raise_half(up, n, True)), b(raise_half(up, n, False))]
    l = [b(left), b(stride(left, n, side_mid)), b(stride(left, n, side_mid))]
    r = [mirror(s) for s in l]
    return {'down': d, 'up': u, 'left': l, 'right': r}


# ------------------------------------------------------------ build
def build():
    rng = np.random.default_rng(1775)
    sc = Scene(MW, MH)
    block = np.zeros((MH, MW), bool)
    G = ((40, 96, 56), (64, 128, 64), (88, 156, 72), (120, 184, 88), (176, 216, 112))
    grass(sc, G, rng, flowers=(150, [(255, 255, 240), (248, 200, 232), (180, 200, 255)]))

    D = ((112, 76, 48), (152, 108, 64), (188, 148, 92), (212, 176, 116), (236, 208, 152))
    road = thick_path(sc.shape, [(-12, 200), (120, 197), (240, 201), (360, 198), (492, 200)], 10, rng)
    road |= thick_path(sc.shape, [(240, 104), (240, 150), (240, 200)], 7, rng, wob=0.6)
    road |= thick_path(sc.shape, [(108, 160), (108, 180), (108, 198)], 4, rng, wob=0.3)
    road |= thick_path(sc.shape, [(379, 156), (379, 178), (379, 198)], 4, rng, wob=0.3)
    road |= thick_path(sc.shape, [(330, 200), (338, 240), (352, 272)], 5, rng, wob=0.6)
    road |= thick_path(sc.shape, [(158, 200), (158, 230)], 5, rng, wob=0.3)
    dirt(sc, road, D, rng, lip=G[0], pebbles=160)

    pond = ellipse(sc.shape, 402, 300, 46, 24) | ellipse(sc.shape, 374, 316, 28, 14)
    W = ((24, 36, 72), (40, 72, 136), (56, 104, 168), (104, 160, 208), (230, 244, 252))
    water(sc, pond, W, rng, bank=((112, 92, 60), (160, 132, 84)))
    block |= erode(pond, 1)
    for (x, y) in ((388, 292), (420, 306), (410, 288), (366, 316)):
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) < 3:
                    sc.put(x + dx, y + dy, (72, 140, 64))
        sc.put(x - 1, y - 1, (128, 192, 96)); sc.put(x + 1, y, (40, 92, 52))
    for (x, y) in ((356, 290), (359, 288), (446, 300), (443, 302), (440, 286)):
        for k in range(5):
            sc.put(x, y - k, (56, 112, 52) if k < 3 else (96, 152, 72))
        sc.put(x, y - 5, (120, 80, 48))

    # garden (crops baked into ground)
    gx0, gy0, gx1, gy1 = 122, 238, 208, 278
    for y in range(gy0, gy1):
        for x in range(gx0, gx1):
            k = (y - gy0) % 6
            sc.img[y, x] = (120, 80, 52) if k < 3 else ((96, 62, 42) if k == 3 else (144, 100, 64))
    for y in range(gy0 + 1, gy1 - 4, 6):
        for x in range(gx0 + 3, gx1 - 6, 9):
            if gx0 + 28 < x < gx0 + 46 and False:
                continue
            spr = P.cabbage() if (x // 9 + y // 6) % 3 else P.pumpkin()
            sc.blit(spr, x, y - 2)

    objects = []  # (sprite, x, y, z, collide box or None)

    def add(spr, x, y, box='full', z=None):
        h, w = spr.shape[:2]
        zz = z if z is not None else y + h
        objects.append((spr, x, y, zz))
        if box == 'full':
            block[max(0, y):max(0, y + h), max(0, x):max(0, x + w)] = True
        elif box is not None:
            bx0, by0, bx1, by1 = box
            block[max(0, y + by0):max(0, y + by1), max(0, x + bx0):max(0, x + bx1)] = True

    def house(spr, x, y):
        sc.shadow_of(spr, x, y, 4, 3)
        h, w = spr.shape[:2]
        add(spr, x, y, box=(0, 12, w, h - 2))

    roofs = ((150, 146, 152), (112, 108, 118), (80, 76, 90), (54, 50, 64))
    white = ((255, 252, 242), (230, 226, 216), (184, 180, 182))
    trim = ((255, 255, 250), (232, 228, 222), (160, 156, 164))
    red_roof = ((132, 120, 116), (100, 90, 90), (72, 64, 68), (48, 42, 48))
    meet = make_house(84, 26, 22, roofs, white, trim, ((120, 76, 56), (96, 58, 44), (64, 40, 32)),
                      windows=[8, 22, 54, 68], win_h=10)
    tower = make_tower()
    mx, my = 198, 46
    house(meet, mx, my)
    th = tower.shape
    tx, ty = 240 - th[1] // 2, my + meet.shape[0] - th[0] + 3
    sc.shadow_of(tower, tx, ty, 4, 3)
    add(tower, tx, ty, box=(0, th[0] - 34, th[1], th[0] - 1))

    red = ((216, 88, 64), (176, 58, 46), (124, 38, 38))
    house(make_house(56, 22, 18, red_roof, red, trim, ((96, 112, 84), (68, 84, 60), (44, 56, 42)),
                     windows=[8, 40], door_x=23, chimneys=[(36, 7)], shutters=((60, 84, 60), (44, 64, 48))), 80, 112)
    grey_roof = ((120, 132, 156), (90, 100, 124), (64, 72, 94), (42, 46, 64))
    grey = ((200, 192, 176), (164, 156, 142), (118, 112, 106))
    house(make_house(56, 22, 18, grey_roof, grey, trim, ((168, 64, 52), (132, 44, 40), (90, 30, 32)),
                     windows=[8, 40], door_x=24, chimneys=[(10, 7), (40, 7)]), 350, 108)
    yel = ((248, 212, 112), (216, 172, 76), (164, 124, 56))
    house(make_house(54, 20, 18, red_roof, yel, trim, ((80, 96, 140), (58, 70, 110), (40, 46, 76)),
                     windows=[7, 39], door_x=22, chimneys=[(8, 7)], shutters=((60, 84, 60), (44, 64, 48))), 40, 232)
    barn_red = ((176, 72, 56), (144, 52, 44), (100, 36, 36))
    house(make_house(80, 26, 24, ((140, 112, 92), (110, 86, 70), (80, 62, 54), (54, 42, 40)), barn_red,
                     trim, ((150, 60, 48), (120, 44, 38), (84, 30, 30)), windows=[8, 64], door_x=30, door_w=20, win_h=7),
          250, 226)

    # stone walls
    for x0, x1 in ((20, 100), (116, 232), (248, 371), (387, 460)):
        wall = make_stonewall(x1 - x0, rng)
        sc.shadow_of(wall, x0, 176, 2, 2)
        add(wall, x0, 176)
    # garden fences with a gate
    for (fx, L) in ((120, 30), (170, 42)):
        add(make_rail_fence(L), fx, 228, box=(0, 4, L, 12))
    add(make_rail_fence(92), 120, 276, box=(0, 4, 92, 12))
    add(make_vfence(48), 118, 234, z=282)
    add(make_vfence(48), 208, 234, z=282)

    # trees
    TG = ((32, 76, 48), (48, 112, 56), (84, 152, 64), (136, 192, 92))
    TD = ((24, 60, 44), (36, 92, 52), (64, 128, 60), (108, 168, 84))

    def tree(x, y, R, kind=None, tones=TG):
        t = make_tree(R, tones, rng,
                      fruit=((220, 48, 48), (150, 24, 36)) if kind == 'a' else None,
                      blossoms=[(255, 236, 244), (248, 184, 212)] if kind == 'b' else None)
        h, w = t.shape[:2]
        sc.foot_shadow(x + w / 2 + 2, y + h - 3, R * 0.9, R * 0.33)
        cx = x + w // 2
        add(t, x, y, box=(w // 2 - 5, h - 9, w // 2 + 5, h - 2))

    # forest border
    for i, x in enumerate(range(-14, MW + 10, 22)):
        tree(x + rng.integers(-3, 4), -18 + rng.integers(-3, 4), 13, tones=TD)
        tree(x + 11 + rng.integers(-3, 4), MH - 34 + rng.integers(-3, 4), 13, tones=TD)
    for y in range(4, MH - 30, 24):
        if 170 < y < 214:
            continue
        tree(-16 + rng.integers(-3, 3), y + rng.integers(-3, 4), 13, tones=TD)
        tree(MW - 22 + rng.integers(-3, 3), y + 10 + rng.integers(-3, 4), 13, tones=TD)
    # road ends: dense trees past the edges so the road fades into the woods
    for (x, y) in ((-24, 168), (-20, 206), (MW - 14, 166), (MW - 18, 206)):
        tree(x, y, 13, tones=TD)
    # orchard + village trees
    for (x, y, k) in ((20, 22, 'b'), (52, 34, 'b'), (24, 62, 'b'), (56, 74, 'a'), (150, 26, None), (300, 22, 'a'),
                      (408, 30, 'b'), (430, 64, 'b'), (396, 66, 'a'), (100, 66, None)):
        tree(x, y, 12, k)
    tree(156, 120, 17)
    tree(430, 150, 11, 'a')
    tree(20, 288, 11, 'b')
    tree(222, 300, 12)
    tree(300, 304, 10, 'a')

    # props
    wl = P.well()
    sc.shadow_of(wl, 262, 140, 3, 2)
    add(wl, 262, 140, box=(0, 6, wl.shape[1], wl.shape[0]))
    hay = P.haystack()
    for (x, y) in ((40, 150), (336, 258), (340, 272)):
        sc.foot_shadow(x + 11, y + 12, 10, 3)
        add(hay, x, y, box=(1, 3, 19, 12))
    for (x, y) in ((330, 138), (336, 146), (226, 280)):
        sc.foot_shadow(x + 6, y + 12, 6, 2)
        add(P.barrel(), x, y, box=(1, 5, 11, 13))
    add(P.crate(), 214, 284, box=(0, 5, 14, 14))
    for (x, y) in ((196, 330), (60, 214)):
        add(P.rock(2), x, y, box=(0, 3, 14, 9))

    # NPCs (static for now)
    mil = CH.minuteman(CH.MILITIA)
    npcs = []
    sc.foot_shadow(295, 153, 7, 2.2)
    add(mil['left'], 286, 128, box=(3, 20, 15, 26))
    sc.foot_shadow(193, 213, 7, 2.2)
    ap = CH.apprentice()
    add(ap['down'], 184, 188, box=(3, 20, 15, 26))

    ground = sc.to_image()
    return ground, objects, block


def pack(objects):
    # shelf-pack unique sprites
    uniq = {}
    order = []
    for spr, x, y, z in objects:
        k = spr.tobytes() + bytes(spr.shape[:2])
        if k not in uniq:
            uniq[k] = None
            order.append((k, spr))
    order.sort(key=lambda o: -o[1].shape[0])
    AW = 512
    cx = cy = rowh = 0
    pos = {}
    for k, spr in order:
        h, w = spr.shape[:2]
        if cx + w > AW:
            cx = 0
            cy += rowh + 1
            rowh = 0
        pos[k] = (cx, cy)
        cx += w + 1
        rowh = max(rowh, h)
    AH = cy + rowh + 1
    atlas = np.zeros((AH, AW, 4), np.uint8)
    for k, spr in order:
        x, y = pos[k]
        h, w = spr.shape[:2]
        atlas[y:y + h, x:x + w] = spr
    out = []
    for spr, x, y, z in objects:
        k = spr.tobytes() + bytes(spr.shape[:2])
        sx, sy = pos[k]
        out.append([int(sx), int(sy), int(spr.shape[1]), int(spr.shape[0]), int(x), int(y), int(z)])
    return atlas, out


def char_sheet():
    mm = frames(CH.MM_DOWN, CH.MM_UP, CH.MM_LEFT, CH.MM_MATS, 4)
    fw, fh = mm['down'][0].shape[1], mm['down'][0].shape[0]
    rows = ['down', 'left', 'right', 'up']
    sheet = np.zeros((fh * 4, fw * 3, 4), np.uint8)
    for r, d in enumerate(rows):
        for c in range(3):
            sheet[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw] = mm[d][c]
    ch = P.chicken()
    chick = np.zeros((ch.shape[0] + 1, ch.shape[1] * 2, 4), np.uint8)
    chick[1:, :ch.shape[1]] = ch
    chick[:-1, ch.shape[1]:] = ch  # bob frame
    return sheet, fw, fh, chick


if __name__ == '__main__':
    ground, objects, block = build()
    atlas, objs = pack(objects)
    sheet, fw, fh, chick = char_sheet()
    Image.fromarray(ground).save(f'{OUT}/ground.png')
    Image.fromarray(atlas).save(f'{OUT}/objects.png')
    Image.fromarray(sheet).save(f'{OUT}/player.png')
    Image.fromarray(chick).save(f'{OUT}/chicken.png')
    m = np.zeros((MH, MW, 4), np.uint8)
    m[block] = (255, 0, 0, 255)
    Image.fromarray(m).save(f'{OUT}/collide.png')
    data = {'w': MW, 'h': MH, 'objects': objs, 'frame': [fw, fh], 'start': [240, 166],
            'chicken': [chick.shape[1] // 2, chick.shape[0]],
            'chickens': [[300, 300], [316, 296], [292, 312], [70, 300]]}
    json.dump(data, open(f'{OUT}/village.json', 'w'))
    # preview composite
    prev = ground.copy()
    for sx, sy, w, h, x, y, z in sorted(objs, key=lambda o: o[6]):
        spr = atlas[sy:sy + h, sx:sx + w]
        for yy in range(h):
            for xx in range(w):
                if spr[yy, xx, 3] and 0 <= y + yy < MH and 0 <= x + xx < MW:
                    prev[y + yy, x + xx] = spr[yy, xx, :3]
    Image.fromarray(prev).resize((MW * 2, MH * 2), Image.NEAREST).save(f'{OUT}/_preview.png')
    Image.fromarray(sheet).resize((sheet.shape[1] * 6, sheet.shape[0] * 6), Image.NEAREST).save(f'{OUT}/_sheet.png')
    print(atlas.shape, len(objs), sheet.shape)
