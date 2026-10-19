from pix import region_sprite, mirror

DET = ('e', 'w', 'p', 'Y', 'y', 'm', 'M', 'k', 'n', 'a', 'x', 'l', 'L', 'c2')

# ---------------------------------------------------------------- minuteman
MM_MATS = {
    'H': ((88, 80, 100), (58, 52, 70), (36, 32, 46)),
    'g': ((214, 200, 176), (176, 160, 140), (124, 112, 104)),
    'h': ((168, 104, 60), (128, 78, 42), (90, 52, 32)),
    'r': ((200, 56, 48),),
    'S': ((255, 216, 172), (242, 178, 130), (204, 128, 92)),
    'e': ((36, 24, 32),), 'w': ((252, 252, 244),), 'p': ((240, 140, 120),),
    'W': ((255, 252, 242), (232, 228, 216), (184, 180, 180)),
    'C': ((180, 122, 74), (142, 92, 56), (100, 60, 40)),
    'c': ((112, 70, 44),),
    'R': ((228, 92, 66), (186, 56, 48), (128, 36, 42)),
    'Y': ((244, 204, 92),),
    'B': ((228, 204, 148), (198, 170, 112), (148, 124, 86)),
    'G': ((252, 248, 238), (222, 218, 210), (170, 166, 172)),
    'F': ((90, 72, 68), (58, 46, 46), (38, 30, 34)),
    'y': ((250, 218, 112),),
    'm': ((156, 162, 178),),
}

MM_DOWN = [
    "....HHHHHHHH....",
    "..HHHHHHHHHHHH..",
    ".gHHHHHHHHHHHHg.",
    "gggHHHHHHHHHHggg",
    ".hgggHHHHHHgggh.",
    ".hhSSggggggSShh.",
    ".hSSSSSggSSSSSh.",
    ".hSSewSSSSweSSh.",
    ".hSSeSSSSSSeSSh.",
    ".hSpSSSSSSSSpSh.",
    "..hSSSSSSSSSSh..",
    "....SSSSSSSS....",
    "...CCCWWWWCCC...",
    "..CCCRRWWRRCCC..",
    ".CCCCRRYRRRCCCC.",
    ".CCCCRRRRRRCCCC.",
    ".CCCCRRYRRRCCCC.",
    ".SSCCRRRRRRCCSS.",
    ".SSCCCCBBCCCCSS.",
    "...CCBBBBBBCC...",
    "...CBBB..BBBC...",
    "....GGG..GGG....",
    "....GGG..GGG....",
    "...FFyF..FyFF...",
]
MM_DOWN = [r[:15] + 'm' if 4 <= i <= 11 else r for i, r in enumerate(MM_DOWN)]

MM_UP = [
    "....HHHHHHHH....",
    "..HHHHHHHHHHHH..",
    ".gHHHHHHHHHHHHg.",
    "gggHHHHHHHHHHggg",
    ".hggggggggggggh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    "..hhhhhhhhhhhh..",
    "..ShhhhrrhhhhS..",
    "....SSShhSSS....",
    "...CCCChhCCCC...",
    "..CCCCCCCCCCCC..",
    ".CCCCCCCCCCCCCC.",
    ".CCCCCCCCCCCCCC.",
    ".CCCCCCcCCCCCCC.",
    ".SSCCCCcCCCCCSS.",
    ".SSCCCCcCCCCCSS.",
    "...CCCCcCCCCC...",
    "...CBBB..BBBC...",
    "....GGG..GGG....",
    "....GGG..GGG....",
    "...FFFF..FFFF...",
]
MM_UP = ['m' + r[1:] if 4 <= i <= 11 else r for i, r in enumerate(MM_UP)]

MM_LEFT = [
    "......HHHHH.....",
    "....HHHHHHHHH...",
    "...HHHHHHHHHHH..",
    ".ggHHHHHHHHHHHg.",
    "gggggggggggggg..",
    ".SSSSSShhhhhh...",
    "SSeSSSShhhhhh...",
    "SSeSSSSShhhhh...",
    ".SSSSpSShhhhh...",
    ".SSSSSSShhhh....",
    "..SSSSSShhrr....",
    "....SSS..hr.....",
    "....WCCCCC......",
    "...WWCCCCCC.....",
    "...RRCCCCCC.....",
    "...RYCCCCCC.....",
    "...RRCCCCCC.....",
    "...RRCCSSCC.....",
    "...BBCCCCCCC....",
    "...BBBBBBCCC....",
    "....BBB.BBB.....",
    "....GGG.GGG.....",
    "....GGG.GGG.....",
    "...FFFF.FFF.....",
]


def _put(rows, pts, ch):
    rows = [list(r) for r in rows]
    for x, y in pts:
        if rows[y][x] == '.':
            rows[y][x] = ch
    return [''.join(r) for r in rows]


MM_LEFT = _put(MM_LEFT, [(11, 12), (12, 11), (13, 10), (14, 9), (15, 8)], 'm')

# ---------------------------------------------------------------- apprentice
AP_MATS = {
    'Q': ((255, 254, 248), (234, 230, 222), (190, 186, 196)),
    'h': ((212, 104, 60), (168, 72, 42), (116, 46, 34)),
    'S': ((255, 216, 176), (244, 182, 136), (206, 132, 98)),
    'e': ((36, 24, 32),), 'w': ((252, 252, 244),), 'p': ((244, 136, 124),),
    'K': ((226, 84, 76), (182, 50, 56), (126, 32, 48)),
    'W': ((255, 252, 242), (232, 228, 216), (184, 180, 180)),
    'D': ((104, 118, 172), (72, 82, 136), (46, 50, 92)),
    'A': ((255, 250, 238), (234, 226, 206), (188, 180, 170)),
    'F': ((90, 72, 68), (58, 46, 46), (38, 30, 34)),
    'L': ((60, 54, 58),), 'l': ((255, 226, 120),),
}
AP_DOWN = [
    ".....QQQQQQ.....",
    "...QQQQQQQQQQ...",
    "..QQQQQQQQQQQQ..",
    ".QQQQQQQQQQQQQQ.",
    ".QQhhhhhhhhhhQQ.",
    ".QhhhhhhhhhhhhQ.",
    ".hhSSSSSSSSSShh.",
    ".hSSewSSSSweSSh.",
    ".hSSeSSSSSSeSSh.",
    ".hSpSSSSSSSSpSh.",
    ".hhSSSSSSSSSShh.",
    "..hhSSSSSSSShh..",
    "...KKKWWWWKKK...",
    "..KKKKKWWKKKKK..",
    ".KKKKKKKKKKKKKK.",
    ".KKDDDDDDDDDDKK.",
    ".SKDAAAAAAAADKS.",
    "..DDAAAAAAAADLLL",
    "..DDAAAAAAAADLlL",
    "..DDAAAAAAAADLlL",
    "..DDDAAAAAADDLLL",
    "..DDDDDDDDDDDD..",
    "...DDDDDDDDDD...",
    "....FFF..FFF....",
]
AP_UP = [
    ".....QQQQQQ.....",
    "...QQQQQQQQQQ...",
    "..QQQQQQQQQQQQ..",
    ".QQQQQQQQQQQQQQ.",
    ".QQQQQQQQQQQQQQ.",
    ".QQQQQQQQQQQQQQ.",
    ".hQQQQQQQQQQQQh.",
    ".hhQQQQQQQQQQhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    "..hhhhhhhhhhhh..",
    "...KKKKKKKKKK...",
    "..KKKKKKKKKKKK..",
    ".KKKKKKKKKKKKKK.",
    ".KKKKKKKKKKKKKK.",
    ".SKKKKKKKKKKKKS.",
    "LLLDDDDDDDDDDD..",
    "LlLDDDDDDDDDDD..",
    "LlLDDDDDDDDDDD..",
    "LLLDDDDDDDDDDD..",
    "..DDDDDDDDDDDD..",
    "...DDDDDDDDDD...",
    "....FFF..FFF....",
]
AP_LEFT = [
    "....QQQQQQ......",
    "..QQQQQQQQQQ....",
    ".QQQQQQQQQQQQ...",
    ".QQQQQQQQQQQQQ..",
    "..QhhQQQQQQQQQ..",
    ".QhSShhhhhhhQQ..",
    ".SSSShhhhhhhhQ..",
    "SSeSSShhhhhhh...",
    "SSeSSSShhhhhh...",
    ".SSpSSShhhhh....",
    ".SSSSSShhhhh....",
    "..SSSSShhhh.....",
    "...WKKKKKK......",
    "..WKKKKKKKK.....",
    "..KKKKKKKKK.....",
    "..ADDDDDDDK.....",
    "..ADDDSSDDD.....",
    "..ADDDLLLDD.....",
    ".AADDDLlLDD.....",
    ".AADDDLlLDDD....",
    ".AADDDLLLDDD....",
    ".DDDDDDDDDDD....",
    "..DDDDDDDDD.....",
    "...FFF.FFF......",
]

# ---------------------------------------------------------------- woodsman
WM_MATS = {
    'N': ((212, 78, 60), (166, 54, 46), (114, 36, 38)),
    'B': ((150, 52, 44), (124, 40, 38), (92, 30, 32)),
    'h': ((136, 90, 56), (104, 66, 42), (74, 46, 30)),
    'b': ((150, 98, 60), (114, 72, 44), (80, 50, 32)),
    'S': ((255, 214, 170), (238, 172, 126), (198, 124, 90)),
    'e': ((36, 24, 32),), 'w': ((252, 252, 244),), 'p': ((240, 140, 120),),
    'c': ((214, 200, 146), (180, 164, 114), (132, 118, 84)),
    'V': ((124, 140, 78), (94, 108, 58), (64, 76, 42)),
    'R': ((212, 70, 56), (168, 46, 42), (118, 32, 34)),
    'L': ((190, 144, 96), (152, 110, 72), (108, 76, 50)),
    'M': ((132, 94, 64), (100, 68, 46), (70, 46, 34)),
    'P': ((160, 114, 72), (124, 86, 54), (86, 58, 38)),
    'r': ((220, 204, 160), (188, 170, 128), (140, 124, 94)),
    'k': ((70, 50, 36),), 'n': ((240, 228, 200),), 'a': ((164, 112, 62),), 'x': ((184, 192, 206),),
}
WM_DOWN = [
    "......NNNN......",
    "....NNNNNNNN....",
    "...NNNNNNNNNN...",
    "..NNNNNNNNNNNN..",
    "..BBBBBBBBBBBB..",
    "..hSSSSSSSSSSh..",
    "..SSewSSSSweSS..",
    "..SSeSSSSSSeSS..",
    "..bSSSSSSSSSSb..",
    "..bbSSbbbbSSbb..",
    "..bbbbbbbbbbbb..",
    "...bbbbbbbbbb...",
    "...cccbbbbccc.xx",
    "..cccccbbccccxxx",
    ".VccccccccccccVa",
    ".VVVVVVVVVVVVVVa",
    ".VVnVVVVVVVVVVVa",
    ".VRRRRRRRRRRRRVa",
    ".SVVVVVVVVVVVVSa",
    "..VVVVVVVVVVVV.a",
    "..cVcVcVcVcVcV.a",
    "...LLLL..LLLL...",
    "...LLLL..LLLL...",
    "..MMMMM..MMMMM..",
]
WM_UP = [
    "......NNNN......",
    "....NNNNNNNN....",
    "...NNNNNNNNNN...",
    "..NNNNNNNNNNNN..",
    "..BBBBBBBBBBBB..",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..ShhhhhhhhhhS..",
    "...hhhhhhhhhh...",
    "..rrrrrrrrrrrr..",
    ".rrrrrrrrrrrrrr.",
    ".VPPPPPPPPPPPPV.",
    ".VPPPPPPPPPPPPV.",
    ".VPPkPPPPPPkPPV.",
    ".VPPkPPPPPPkPPV.",
    "xVPPPPPPPPPPPPV.",
    "xVRRRRRRRRRRRRV.",
    "aSVVVVVVVVVVVVS.",
    "a.VVVVVVVVVVVV..",
    "a.cVcVcVcVcVcV..",
    "...LLLL..LLLL...",
    "...LLLL..LLLL...",
    "..MMMMM..MMMMM..",
]
WM_LEFT = [
    ".....NNNN.......",
    "...NNNNNNNNN....",
    "..NNNNNNNNNNNN..",
    "..NNNNNNNNNNNNN.",
    "..BBBBBBBBBBB.N.",
    ".SSSShhhhhhhh...",
    "SSeSSShhhhhhh...",
    "SSSSSSShhhhh....",
    "bSSSSSShhhhh....",
    "bbbbSSShhhh.....",
    "bbbbbbbhhh......",
    ".bbbbbb.........",
    "..cccccccrrrr...",
    "..cccccccPPPPP..",
    "..VVVVVVVPPPPP..",
    "..VVVVSVVPPPPP..",
    "..VVVVVVVPPPPP..",
    "..RRRRRRRRPPP...",
    "..VVVVVVVV......",
    "..VVVVVVVV......",
    "..cVcVcVcV......",
    "...LLL.LLL......",
    "...LLL.LLL......",
    "..MMMM.MMMM.....",
]


def build(rows, mats):
    return region_sprite(rows, mats, details=DET)


def minuteman(mats=None):
    m = mats or MM_MATS
    l = build(MM_LEFT, m)
    return {'down': build(MM_DOWN, m), 'up': build(MM_UP, m), 'left': l, 'right': mirror(l)}


def apprentice():
    l = build(AP_LEFT, AP_MATS)
    return {'down': build(AP_DOWN, AP_MATS), 'up': build(AP_UP, AP_MATS), 'left': l, 'right': mirror(l)}


def woodsman():
    l = build(WM_LEFT, WM_MATS)
    return {'down': build(WM_DOWN, WM_MATS), 'up': build(WM_UP, WM_MATS), 'left': l, 'right': mirror(l)}


MILITIA = dict(MM_MATS)
MILITIA.update({
    'C': ((96, 116, 160), (66, 82, 124), (42, 52, 86)),
    'R': ((230, 210, 160), (200, 176, 122), (150, 128, 88)),
    'h': ((220, 216, 208), (188, 182, 176), (140, 134, 136)),
    'B': ((150, 126, 96), (118, 96, 72), (84, 68, 54)),
})
PRINTER = dict(MM_MATS)
PRINTER.update({
    'C': ((120, 96, 84), (92, 70, 62), (62, 46, 44)),
    'R': ((96, 92, 96), (70, 66, 72), (48, 44, 52)),
    'h': ((236, 232, 224), (204, 200, 194), (150, 146, 150)),
    'B': ((100, 84, 72), (76, 62, 54), (54, 44, 40)),
    'W': ((255, 252, 242), (232, 228, 216), (184, 180, 180)),
})
