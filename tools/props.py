import numpy as np
from pix import region_sprite, add_outline, mix

DET = ('j', 'c', 'b', 'r', 'k', 'x', 'a', 's', 'y', 'e', 'Y', 'X', 'h', 'g', 'D', 'T2', 'G')

WOOD = ((196, 144, 92), (156, 108, 66), (108, 72, 46))
STONE = ((200, 196, 188), (160, 156, 152), (112, 108, 114))


def rs(rows, mats):
    return region_sprite(rows, mats, details=DET)


def barrel():
    return rs([
        ".TTTTTTTT.",
        "TTTTTTTTTT",
        "TTTTTTTTTT",
        ".TTTTTTTT.",
        "IIIIIIIIII",
        "OOOOOOOOOO",
        "OOOOOOOOOO",
        "IIIIIIIIII",
        "OOOOOOOOOO",
        "OOOOOOOOOO",
        ".IIIIIIII.",
    ], {'T': ((216, 168, 112), (184, 136, 86), (140, 100, 64)), 'I': ((128, 124, 132), (92, 88, 98), (62, 58, 68)),
        'O': ((176, 118, 70), (140, 90, 54), (98, 62, 40))})


def crate():
    return rs([
        "TTTTTTTTTTTT",
        "TTTTTTTTTTTT",
        "TTTTTTTTTTTT",
        "TTTTTTTTTTTT",
        "KKKKKKKKKKKK",
        "KXKKKKKKKKXK",
        "KKXKKKKKKXKK",
        "KKKXKKKKXKKK",
        "KKKKXKKXKKKK",
        "KKKKKXXKKKKK",
        "KKKKXKKXKKKK",
        "KKKXKKKKXKKK",
    ], {'T': ((222, 182, 122), (196, 152, 98), (150, 112, 70)), 'K': ((184, 136, 86), (152, 108, 66), (110, 76, 48)),
        'X': ((112, 76, 48),)})


def haystack():
    return rs([
        ".....HHHHHHH......",
        "...HHHHHHHHHHHH...",
        "..HHHHhHHHHHhHHH..",
        ".HHHHHHHHhHHHHHHH.",
        ".HHhHHHHHHHHHHhHH.",
        "HHHHHHHHHHHHHHHHHH",
        "HHHHHHhHHHHHhHHHHH",
        "HHhHHHHHHHHHHHHHhH",
        "HHHHHHHHHhHHHHHHHH",
        ".HHHHHHHHHHHHHHHH.",
    ], {'H': ((248, 224, 128), (220, 184, 88), (168, 128, 56)), 'h': ((184, 144, 64),)})


def chicken():
    return rs([
        ".r....",
        "yWe..W",
        ".WWWWW",
        ".WWWW.",
        "..Y.Y.",
    ], {'r': ((216, 56, 48),), 'y': ((244, 184, 64),), 'e': ((30, 20, 30),), 'Y': ((232, 160, 56),),
        'W': ((255, 255, 250), (236, 232, 226), (190, 186, 196))})


def cabbage():
    return rs([
        "..GGG..",
        ".GGgGG.",
        "GGgGgGG",
        "GGGgGGG",
        ".GGGGG.",
    ], {'G': ((160, 208, 112), (112, 172, 80), (72, 124, 60)), 'g': ((200, 232, 160),)})


def pumpkin():
    return rs([
        "...s....",
        ".PPPPPP.",
        "PPrPPrPP",
        "PPrPPrPP",
        ".PPPPPP.",
    ], {'P': ((252, 168, 72), (228, 124, 44), (172, 80, 32)), 's': ((88, 120, 48),), 'r': ((188, 92, 36),)})


def well():
    return rs([
        "..RRRRRRRRRRRRRR..",
        ".RRRRRRRRRRRRRRRR.",
        "RRRRRRRRRRRRRRRRRR",
        "..W.....r......W..",
        "..W.....r......W..",
        "..W....bbb.....W..",
        "..W....bbb.....W..",
        ".SWSSSSSSSSSSSSWS.",
        "SSWDDDDDDDDDDDDWSS",
        "SSDDDDDDDDDDDDDDSS",
        ".SSSSSSSSSSSSSSSS.",
        "TTTjTTTTTjTTTTjTTT",
        "TjTTTTjTTTTTjTTTTj",
        "TTTTjTTTTjTTTTTjTT",
        ".TTTTTTTTTTTTTTTT.",
    ], {'R': ((176, 104, 72), (140, 76, 56), (100, 52, 44)), 'W': WOOD, 'r': ((220, 200, 150),),
        'b': ((150, 100, 60),), 'S': STONE, 'D': ((32, 44, 76),),
        'T': ((168, 164, 160), (136, 132, 130), (98, 94, 100)), 'j': ((84, 80, 88),)})


def bubble():
    return rs([
        ".WWWWW.",
        "WWWrWWW",
        "WWWrWWW",
        "WWWrWWW",
        "WWWWWWW",
        "WWWrWWW",
        ".WWWWW.",
        "...W...",
    ], {'W': ((255, 255, 250), (244, 240, 230), (200, 196, 204)), 'r': ((216, 48, 48),)})


def corn_shock():
    return rs([
        "....CC....",
        "....CC....",
        "...CCCC...",
        "...CcCC...",
        "..CCtCCC..",
        "..CCCcCC..",
        ".CCcCCCCC.",
        ".CCCCcCCC.",
        ".CcCCCCcC.",
        "CCCCcCCCCC",
        "CcCCCCCcCC",
        "CCCcCCCCcC",
    ], {'C': ((244, 216, 132), (214, 180, 96), (160, 128, 64)), 'c': ((176, 140, 70),), 't': ((150, 96, 52),)})


def rock(scale=1):
    rows = [
        "..RRRR..",
        ".RRRRRR.",
        "RRRRRRRR",
        "RRRRRRRR",
        ".RRRRRR.",
    ] if scale == 1 else [
        "...RRRRRR...",
        ".RRRRRRRRRR.",
        "RRRRRRRRRRRR",
        "RRRRRRRRRRRR",
        "RRRRRRRRRRRR",
        "RRRRRRRRRRRR",
        ".RRRRRRRRRR.",
    ]
    return rs(rows, {'R': ((196, 192, 184), (150, 146, 144), (104, 100, 108))})


def stump():
    return rs([
        "......xx..",
        ".....xxx..",
        "......a...",
        ".....a....",
        "..TTaTTT..",
        ".TTTcTTTT.",
        ".TTTTTcTT.",
        "..TTTTTT..",
        "BBBBBBBBBB",
        "BBBbBBBBbB",
        ".BBBBBBBB.",
    ], {'T': ((232, 200, 140), (210, 172, 112), (168, 132, 84)), 'c': ((176, 136, 86),),
        'B': ((140, 96, 60), (110, 74, 46), (78, 52, 36)), 'b': ((70, 46, 32),),
        'x': ((196, 204, 216),), 'a': ((168, 116, 64),)})


def canoe():
    return rs([
        "....BBBBBBBBBBBBBBBBBB....",
        "..BBBIIIIIIIIIIIIIIIIBBB..",
        "BBBIIIITIIIIIIIIITIIIIIBBB",
        "..BBBIIIIIIIIIIIIIIIIBBB..",
        "....BkBBBBkBBBBBkBBBBB....",
        "......BBBBBBBBBBBBBB......",
    ], {'B': ((248, 240, 220), (222, 212, 190), (170, 160, 146)), 'k': ((60, 50, 50),),
        'I': ((200, 150, 96), (168, 120, 74), (124, 86, 54)), 'T': ((120, 84, 52),)})


def lantern_post():
    rows = ["..II..", ".IIII.", "IGGGGI", "IGGGGI", "IGGGGI", ".IIII."] + ["..PP.."] * 14 + [".PPPP."]
    return rs(rows, {'I': ((60, 54, 62),), 'G': ((255, 228, 140),), 'P': ((120, 104, 104), (88, 76, 80), (60, 52, 58))})


def woodpile():
    W, H = 22, 14
    spr = np.zeros((H, W, 4), np.uint8)
    ends = [(3, 10), (8, 10), (13, 10), (18, 10), (5.5, 6), (10.5, 6), (15.5, 6), (8, 2.5), (13, 2.5)]
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy in ends:
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m = d <= 2.6
        spr[m] = (214, 176, 118, 255)
        spr[m & (xx - cx + yy - cy > 1.2)] = (172, 132, 84, 255)
        spr[d <= 0.8] = (150, 108, 64, 255)
        ring = (d > 2.6) & (d <= 3.4)
        spr[ring & (spr[..., 3] == 0)] = (104, 70, 44, 255)
    return add_outline(spr)


# ---------------------------------------------------------------- HUD icons
def icons():
    R = ((255, 96, 88), (224, 40, 56), (150, 24, 48))
    E = ((120, 104, 120), (84, 70, 88), (56, 46, 62))
    out = {}
    heart = [".RR.RR.", "RwRRRRR", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."]
    out['heart'] = rs(heart, {'R': R, 'w': ((255, 236, 236),)})
    half = [".RR.EE.", "RwRREEE", "RRRREEE", ".RRREE.", "..RRE..", "...R..."]
    out['heart_half'] = rs(half, {'R': R, 'E': E, 'w': ((255, 236, 236),)})
    out['heart_empty'] = rs([r.replace('R', 'E').replace('w', 'E') for r in heart], {'E': E})
    out['coin'] = rs(["..YYY..", ".YYYYY.", "YYYcYYY", "YYcYcYY", "YYYcYYY", ".YYYYY.", "..YYY.."],
                     {'Y': ((248, 248, 252), (200, 204, 216), (136, 140, 160)), 'c': ((120, 124, 144),)})
    out['horn'] = rs(["HH.......", ".HHH.....", "..HHHHH..", "...HHHHHb", "....HHHHb", "......HH."],
                     {'H': ((255, 248, 224), (232, 216, 180), (176, 156, 120)), 'b': ((120, 80, 48),)})
    out['axe'] = rs([".xxx....", "xxxxx...", "xxxxxa..", ".xx..a..", ".....a..", "......a.", "......a.", ".......a"],
                    {'x': ((224, 230, 240), (176, 184, 200), (120, 128, 148)), 'a': ((176, 120, 64),)})
    out['map'] = rs(["MMMMMMMMM", "MrMMkMMMM", "MMrMkMMrM", "MMMrkMrMM", "MMMMkrMMM", "MMMMkMMMM"],
                    {'M': ((255, 244, 210), (236, 216, 168), (186, 160, 116)), 'r': ((208, 56, 48),), 'k': ((196, 170, 124),)})
    return out
