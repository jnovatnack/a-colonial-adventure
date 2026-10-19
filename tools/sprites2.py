"""New characters and props for the homestead / tavern chapter."""
import numpy as np
from pix import region_sprite, add_outline, mirror
import chars as CH

DET = ('e', 'w', 'p', 'Y', 'y', 'm', 'k', 'n', 'c', 'f', 't', 'r', 'b', 's', 'l', 'g', 'o')


def rs(rows, mats, det=DET):
    return region_sprite(rows, mats, details=det)


def strip(rows, chars):
    return [''.join('.' if ch in chars else ch for ch in r) for r in rows]


def recolor_rows(rows, mapping):
    return [''.join(mapping.get(ch, ch) for ch in r) for r in rows]


# ---------------------------------------------------------------- people (4 stand frames each)
def four(down, up, left, mats, det=CH.DET):
    b = lambda r: region_sprite(r, mats, details=det)
    l = b(left)
    return [b(down), l, mirror(l), b(up)]


def wife():
    m = dict(CH.AP_MATS)
    m.update({'h': ((150, 96, 60), (116, 70, 44), (80, 48, 34)),
              'K': ((150, 170, 204), (114, 134, 172), (78, 94, 132)),
              'D': ((168, 112, 74), (134, 84, 54), (94, 58, 40))})
    rm = lambda r: strip(r, 'Ll')
    return four(rm(CH.AP_DOWN), rm(CH.AP_UP), recolor_rows(CH.AP_LEFT, {'L': 'D', 'l': 'D'}), m)


def widow():
    m = dict(CH.AP_MATS)
    m.update({'h': ((214, 210, 204), (180, 176, 172), (132, 128, 132)),
              'K': ((92, 86, 100), (64, 58, 72), (42, 38, 50)),
              'D': ((78, 74, 92), (54, 50, 66), (36, 32, 46)),
              'A': ((220, 216, 210), (190, 186, 182), (146, 142, 146))})
    rm = lambda r: strip(r, 'Ll')
    return four(rm(CH.AP_DOWN), rm(CH.AP_UP), recolor_rows(CH.AP_LEFT, {'L': 'D', 'l': 'D'}), m)


def keeper():
    m = dict(CH.WM_MATS)
    m.update({'N': ((255, 252, 244), (232, 228, 218), (188, 184, 186)),
              'B': ((214, 210, 200), (190, 186, 178), (150, 146, 144)),
              'b': ((196, 192, 186), (164, 160, 156), (120, 116, 118)),
              'h': ((196, 192, 186), (164, 160, 156), (120, 116, 118)),
              'c': ((255, 252, 242), (232, 228, 216), (184, 180, 180)),
              'V': ((176, 124, 80), (142, 96, 60), (102, 66, 44)),
              'R': ((120, 84, 56), (96, 66, 44), (70, 48, 34)),
              'L': ((110, 94, 84), (84, 70, 62), (60, 50, 46)),
              'P': ((176, 124, 80), (142, 96, 60), (102, 66, 44))})
    rm = lambda r: strip(r, 'xan')
    up = recolor_rows(rm(CH.WM_UP), {'r': 'h', 'P': 'c', 'k': 'R'})
    left = strip(rm(CH.WM_LEFT), 'rP')
    return four(rm(CH.WM_DOWN), up, left, m)


def holt():
    return four(CH.MM_DOWN, CH.MM_UP, CH.MM_LEFT, CH.MILITIA)


def brewer():
    return four(CH.MM_DOWN, CH.MM_UP, CH.MM_LEFT, CH.PRINTER)


def trapper():
    return four(CH.WM_DOWN, CH.WM_UP, CH.WM_LEFT, CH.WM_MATS)


# ---------------------------------------------------------------- dog
DOG_MATS = {'D': ((216, 160, 96), (180, 122, 66), (128, 82, 46)), 'w': ((250, 242, 226),),
            'e': ((30, 20, 30),), 'n': ((40, 28, 34),), 'o': ((100, 64, 40),), 't': ((180, 122, 66),)}
DOG_LEFT = [
    "..oo..........",
    ".oDDD.........",
    "nDeDD.......D.",
    "DDDDDD.....D..",
    ".wwDDDDDDDDD..",
    "..wDDDDDDDDD..",
    "...DDDDDDDDD..",
    "...D.D...D.D..",
    "...D.D...D.D..",
]
DOG_DOWN = [
    ".oo....oo.",
    ".oDDDDDDo.",
    "DDeDDDDeDD",
    "DDDDDDDDDD",
    ".DDDnnDDD.",
    "..DwwwwD..",
    ".DDwwwwDD.",
    ".DDDDDDDD.",
    ".DDDDDDDD.",
    ".D.D..D.D.",
]
DOG_UP = [
    ".oo....oo.",
    ".oDDDDDDo.",
    "DDDDDDDDDD",
    "DDDDDDDDDD",
    ".DDDDDDDD.",
    "..DDDDDD..",
    ".DDDDDDDD.",
    ".DDDDDDDD.",
    ".DDDDDDDD.",
    ".D.DDDD.D.",
]


def _shift_legs(rows, n, cols_a, cols_b, up=True):
    g = [list(r) for r in rows]
    out = [r[:] for r in g]
    H = len(g)
    for y in range(H - n, H):
        for x in cols_a:
            out[y][x] = g[y + 1][x] if y + 1 < H else '.'
    return [''.join(r) for r in out]


def dog_frames():
    """Returns dict dir -> [stand, step]."""
    b = lambda r: rs(r, DOG_MATS)
    l0 = DOG_LEFT
    l1 = [r for r in DOG_LEFT[:-2]] + ["..D...D.D...D.", "..D...D.D...D."]
    d1 = DOG_DOWN[:-1] + [".D.......D."[:10]]
    d2 = DOG_DOWN[:-1] + ["...D..D..."]
    u1 = DOG_UP[:-1] + [".D..DD...."]
    L = [b(l0), b(l1)]
    return {'down': [b(DOG_DOWN), b(d1), b(d2)], 'up': [b(DOG_UP), b(u1), b(DOG_UP)],
            'left': [L[0], L[1], L[0]], 'right': [mirror(L[0]), mirror(L[1]), mirror(L[0])]}


# ---------------------------------------------------------------- horses
HORSE = [
    "...MM...................",
    "..MBBM..................",
    ".BBBBMM.................",
    "BBeBBBMM................",
    "BBBBBBMMM...............",
    "WBBB.BBBMMSSSSSBBBBB....",
    "..B..BBBBBSSSSSBBBBBBM..",
    ".....BBBBBBSSSBBBBBBBMM.",
    ".....BBBBBBBBBBBBBBBBBMM",
    ".....BBBBBBBBBBBBBBBBB.M",
    "......BBBBBBBBBBBBBBB..M",
    "......BB.BB.....BB.BB...",
    "......BB.BB.....BB.BB...",
    "......BB.BB.....BB.BB...",
    "......BB.BB.....BB.BB...",
    "......HH.HH.....HH.HH...",
]


def horse(coat, mane, saddle=True):
    rows = HORSE if saddle else recolor_rows(HORSE, {'S': 'B'})
    return rs(rows, {'B': coat, 'M': (mane,), 'H': ((60, 50, 50),), 'e': ((30, 20, 30),), 'W': ((250, 246, 236),),
                     'S': ((150, 60, 44), (120, 44, 36), (84, 30, 28))}, det=DET + ('M', 'H', 'W'))


# ---------------------------------------------------------------- props
def corn():
    return rs([
        "...t...",
        "..ttt..",
        "...G...",
        "..GGG..",
        ".GG.GG.",
        "G..G..G",
        "...Gy..",
        "..GGy..",
        ".G.G.G.",
        "G..G..G",
        "...G...",
        "..GGG..",
        ".G.G.G.",
        "...G...",
        "...G...",
        "..GGG..",
    ], {'G': ((128, 184, 80), (88, 144, 60), (56, 100, 48)), 't': ((236, 212, 120),), 'y': ((248, 216, 96),)})


def stook():
    return rs([
        "....WW....",
        "...WWWW...",
        "..WWwWWW..",
        "..WWWWwW..",
        "..WbbbbW..",
        ".WWWwWWWW.",
        ".WwWWWWwW.",
        "WWWWWwWWWW",
        "WWwWWWWWwW",
        "WWWWWWWWWW",
    ], {'W': ((252, 228, 140), (226, 192, 96), (176, 140, 64)), 'w': ((196, 160, 72),), 'b': ((140, 96, 52),)})


def signpost():
    return rs([
        "..BBBBBBBB......",
        ".BkkBkkBkB......",
        "..BBBBBBBB......",
        ".......PP.......",
        "......BBBBBBBB..",
        "......BkkBkkBkB.",
        "......BBBBBBBB..",
        ".......PP.......",
        ".......PP.......",
        ".......PP.......",
        ".......PP.......",
        ".......PP.......",
        "......PPPP......",
    ], {'B': ((222, 186, 132), (190, 150, 100), (140, 104, 70)), 'k': ((96, 64, 44),),
        'P': ((156, 112, 72), (122, 84, 54), (86, 58, 40))})


def tavern_sign():
    return rs([
        "PPPPPPPPPPPP",
        "P.c......c..",
        "P.c......c..",
        "P.BBBBBBBB..",
        "P.BBByyBBB..",
        "P.BByyyyBB..",
        "P.BByyyBBB..",
        "P.BBByyBBB..",
        "P.BBBBBBBB..",
        "P...........",
        "P...........",
        "P...........",
        "P...........",
        "PP..........",
    ], {'P': ((120, 84, 56), (96, 66, 44), (70, 48, 34)), 'c': ((120, 116, 124),),
        'B': ((196, 72, 56), (160, 48, 44), (112, 32, 34)), 'y': ((248, 208, 96),)})


def trough():
    return rs([
        "WWWWWWWWWWWWWWWW",
        "WwwwwwwwwwwwwwwW",
        "WwwwwwwwwwwwwwwW",
        "WWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWW",
        ".W............W.",
    ], {'W': ((176, 128, 84), (140, 98, 62), (98, 68, 46)), 'w': ((88, 136, 184),)})


def fern():
    return rs([
        "F...F...F",
        ".F.FFF.F.",
        "..FFFFF..",
        ".FFF.FFF.",
        "FF.....FF",
    ], {'F': ((112, 176, 84), (72, 136, 64), (44, 96, 52))})


def mushrooms():
    return rs([
        ".RR...",
        "RgRR..",
        ".s..RR",
        ".s.RgR",
        "....s.",
    ], {'R': ((236, 96, 72), (200, 60, 52), (140, 40, 44)), 'g': ((255, 244, 232),), 's': ((236, 224, 200),)})


def log():
    return rs([
        ".LLLLLLLLLLLLLLLLLLLLEE.",
        "LLLLLLLLLLLLLLLLLLLLEEEE",
        "LLLLLLLLLLLLLLLLLLLLErEE",
        "LLLLLLLLLLLLLLLLLLLLEEEE",
        ".LLLLLLLLLLLLLLLLLLLLEE.",
    ], {'L': ((144, 104, 72), (112, 78, 54), (78, 54, 40)), 'E': ((230, 198, 140), (206, 168, 112), (160, 124, 80)),
        'r': ((168, 128, 84),)})


def mug(foam=True):
    return rs([
        "fff..",
        "MMMM.",
        "MMMMM",
        "MMMMM",
        "MMMM.",
    ] if foam else [
        ".....",
        "MMMM.",
        "MMMMM",
        "MMMMM",
        "MMMM.",
    ], {'M': ((200, 204, 212), (156, 160, 172), (108, 112, 126)), 'f': ((255, 250, 236),)})


def table(W=40):
    rows = []
    for y in range(8):
        rows.append('T' * W)
    for y in range(4):
        rows.append('A' * W)
    for y in range(3):
        r = ['.'] * W
        for x in (1, 2, W - 3, W - 2):
            r[x] = 'l'
        rows.append(''.join(r))
    return rs(rows, {'T': ((208, 160, 104), (178, 128, 80), (132, 92, 58)), 'A': ((140, 98, 62), (114, 78, 50), (82, 56, 38)),
                     'l': ((100, 68, 44),)})


def bench(W=36):
    rows = ['S' * W, 'S' * W, 'K' * W]
    r = ['.'] * W
    for x in (2, W - 3):
        r[x] = 'l'
    rows.append(''.join(r))
    return rs(rows, {'S': ((196, 150, 98), (166, 120, 76), (122, 86, 54)), 'K': ((110, 76, 48),), 'l': ((90, 62, 40),)},
              det=DET + ('K',))


def counter(W=72, D=8, H=14):
    rows = []
    for y in range(D):
        rows.append('T' * W)
    for y in range(H):
        r = ''.join('p' if (x % 12 in (0, 11) and 1 <= y <= H - 2) else 'A' for x in range(W))
        rows.append(r)
    return rs(rows, {'T': ((176, 120, 76), (146, 96, 60), (106, 68, 44)), 'A': ((124, 84, 54), (100, 66, 42), (72, 46, 32)),
                     'p': ((84, 56, 38),)})


def laundry():
    W, H = 46, 26
    spr = np.zeros((H, W, 4), np.uint8)
    wood = ((176, 128, 84), (136, 96, 60), (92, 64, 44))
    for px in (1, W - 4):
        for y in range(0, H):
            for x in range(px, px + 3):
                spr[y, x] = (*wood[x - px], 255)
    for x in range(3, W - 3):
        y = 3 + int(2.5 * np.sin(np.pi * (x - 3) / (W - 6)))
        spr[y, x] = (220, 212, 190, 255)
    clothes = [(8, 9, 10, ((255, 252, 244), (230, 226, 216), (184, 180, 182))),
               (20, 8, 12, ((150, 176, 220), (116, 140, 190), (78, 98, 150))),
               (31, 7, 8, ((230, 96, 80), (196, 64, 56), (140, 44, 44)))]
    for cx, cw, ch, pal in clothes:
        top = 3 + int(2.5 * np.sin(np.pi * (cx - 3) / (W - 6))) + 1
        for y in range(top, top + ch):
            for x in range(cx, cx + cw):
                c = pal[0] if x == cx else (pal[2] if x == cx + cw - 1 or y == top + ch - 1 else pal[1])
                spr[y, x] = (*c, 255)
    return add_outline(spr)


def bush(rng, tones=((32, 76, 48), (48, 112, 56), (84, 152, 64), (136, 192, 92)), berries=None):
    from pix import make_tree
    t = make_tree(7, tones, rng, fruit=berries)
    # chop the trunk: keep only canopy rows
    a = t[..., 3] > 0
    return t
