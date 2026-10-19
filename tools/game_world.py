"""Chapter 1 world: the homestead, the forest path & creek, the crossroads tavern, and the tavern interior."""
import json, os
import numpy as np
from PIL import Image
from pix import *
import props as P
import chars as CH
import sprites2 as S2
from game_village import frames, pack

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'world')
os.makedirs(OUTDIR, exist_ok=True)
PREVIEW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'previews')
os.makedirs(PREVIEW_DIR, exist_ok=True)

TG = ((32, 76, 48), (48, 112, 56), (84, 152, 64), (136, 192, 92))
TD = ((22, 58, 42), (34, 88, 50), (60, 124, 58), (104, 164, 82))
PINE = ((20, 44, 40), (32, 70, 54), (50, 98, 68), (82, 130, 86))
TRIM = ((255, 255, 250), (232, 228, 222), (160, 156, 164))


class World:
    def __init__(self, w, h, seed):
        self.sc = Scene(w, h)
        self.w, self.h = w, h
        self.rng = np.random.default_rng(seed)
        self.block = np.zeros((h, w), bool)
        self.objects = []
        self.npcs = []
        self.acts = []
        self.doors = []

    def add(self, spr, x, y, box='full', z=None):
        h, w = spr.shape[:2]
        self.objects.append((spr, int(x), int(y), int(z if z is not None else y + h)))
        if box == 'full':
            self.block[max(0, y):max(0, y + h), max(0, x):max(0, x + w)] = True
        elif box is not None:
            bx0, by0, bx1, by1 = box
            self.block[max(0, y + by0):max(0, y + by1), max(0, x + bx0):max(0, x + bx1)] = True

    def act(self, r, id_, label):
        self.acts.append({'r': [int(v) for v in r], 'id': id_, 'label': label})

    def tree(self, bx, by, R=None, kind=None, tones=TG, pine=False):
        """Place a tree so its trunk base sits at (bx, by)."""
        rng = self.rng
        if pine:
            t = make_pine(int(R or 34), PINE, rng)
        else:
            t = make_tree(int(R or 12), tones, rng,
                          fruit=((220, 48, 48), (150, 24, 36)) if kind == 'a' else None,
                          blossoms=[(255, 236, 244), (248, 184, 212)] if kind == 'b' else None)
        h, w = t.shape[:2]
        x, y = int(bx - w / 2), int(by - h + 3)
        self.sc.foot_shadow(bx + 2, by, w * 0.4, 3)
        self.add(t, x, y, box=(w // 2 - 5, h - 9, w // 2 + 5, h - 2))
        return t


# ============================================================ OUTDOORS
def outdoor():
    W_, H_ = 576, 900
    DY = 196  # the homestead sits this far below where it was in the first layout
    wd = World(W_, H_, 1774)
    sc, rng = wd.sc, wd.rng
    G = ((40, 96, 56), (64, 128, 64), (88, 156, 72), (120, 184, 88), (176, 216, 112))
    grass(sc, G, rng, flowers=(220, [(255, 255, 240), (248, 200, 232), (180, 200, 255), (255, 228, 120)]))
    # forest floor: darker, mossier grass outside the clearings
    tav_clear = ellipse(sc.shape, 300, 64, 236, 78)
    home_clear = ellipse(sc.shape, 296, 590 + DY, 282, 160)
    clear = tav_clear | home_clear
    B = bayer_tile(H_, W_)
    forest_floor = ~dilate(clear, 3)
    edge = dilate(clear, 3) & ~clear
    sc.img[forest_floor] *= np.array([0.78, 0.82, 0.80])
    sc.img[edge & (B > 0.5)] *= np.array([0.86, 0.9, 0.88])
    ys, xs = np.nonzero(forest_floor)
    for i in rng.choice(len(ys), 1300, replace=False):
        c = [(110, 84, 50), (140, 110, 60), (70, 100, 50)][i % 3]
        sc.put(xs[i], ys[i], c)

    # ---- paths
    D = ((112, 76, 48), (152, 108, 64), (188, 148, 92), (212, 176, 116), (236, 208, 152))
    DF = ((92, 66, 44), (128, 94, 58), (158, 124, 80), (184, 152, 104), (212, 186, 140))
    P_NS = [(300, -12), (300, 92), (296, 120), (296, 172), (288, 220), (262, 270), (270, 330), (252, 390),
            (262, 450), (240, 510), (232, 570), (222, 610), (186, 640), (170, 682), (186, 716), (246, 732)]
    road = thick_path(sc.shape, [(-12, 92), (150, 90), (300, 92), (450, 90), (588, 92)], 10, rng)
    path = thick_path(sc.shape, P_NS, 6, rng, wob=0.7)
    yard = ellipse(sc.shape, 284, 540 + DY, 96, 20) | ellipse(sc.shape, 388, 528 + DY, 52, 16)
    tyard = ellipse(sc.shape, 206, 84, 62, 12) | ellipse(sc.shape, 384, 76, 70, 14)
    dirt(sc, road | tyard, D, rng, lip=G[0], pebbles=90)
    dirt(sc, (path & ~road & ~yard) | yard, DF, rng, lip=G[0], pebbles=160)

    # ---- creek: in from the east, along the east side of the path, then west under the footbridge beside the road
    CREEK = [(588, 604), (500, 592), (400, 584), (300, 572), (264, 556), (268, 510), (290, 452), (280, 392),
             (298, 332), (290, 272), (314, 222), (322, 186), (316, 162), (296, 150), (268, 145), (200, 136),
             (100, 132), (-12, 134)]
    creek = thick_path(sc.shape, CREEK, 6, rng, wob=1.0)
    Wt = ((24, 40, 72), (40, 84, 132), (60, 120, 168), (120, 180, 216), (236, 248, 252))
    water(sc, creek, Wt, rng, bank=((104, 88, 60), (150, 128, 86)))
    bx0, bx1 = 285, 307
    by0, by1 = 134, 166
    bridge = np.zeros(sc.shape, bool)
    bridge[by0:by1, bx0:bx1] = True
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            k = (y - by0) % 4
            c = (204, 160, 108) if k == 0 else ((174, 130, 84) if k < 3 else (112, 78, 52))
            if (x - bx0) in (2, bx1 - bx0 - 3) and k == 1:
                c = (90, 64, 48)
            sc.put(x, y, c)
    for y in range(by0, by1):
        sc.put(bx0 - 1, y, OUT); sc.put(bx1, y, OUT)
    wd.block |= creek & ~bridge
    rail = np.zeros((by1 - by0 + 4, 5, 4), np.uint8)
    for y in range(rail.shape[0]):
        for x in range(5):
            rail[y, x] = (*((176, 128, 84), (150, 106, 68), (120, 84, 54), (96, 66, 44), (76, 52, 38))[x], 255)
        if y % 9 == 0:
            rail[y, :] = (70, 48, 36, 255)
    rail = add_outline(rail)
    wd.add(rail, bx0 - 6, by0 - 4)
    wd.add(rail, bx1 - 1, by0 - 4)
    for (x, y) in ((298, 330), (268, 508), (420, 584), (150, 133), (282, 394)):
        wd.add(P.rock(1), x - 5, y - 4, box=None)
    wd.act([bx0 - 8, by0, bx1 + 8, by1], 'creek', 'LOOK')
    for (x, y) in ((292, 300), (275, 470), (300, 246)):
        wd.act([x - 14, y - 14, x + 14, y + 14], 'creek', 'LOOK')

    # ---- forest trees (avoid clearings, path, creek)
    corridor = dilate(path | road, 11) | dilate(creek, 8) | dilate(tyard | yard, 6)
    for (x0, y0, x1, y1) in ((48, 440 + DY, 170, 530 + DY), (200, 440 + DY, 500, 530 + DY), (440, 480 + DY, 500, 560 + DY)):
        corridor[y0:y1, x0:x1] = True
    pts = []
    for gy in range(-6, H_ + 20, 19):
        for gx in range(-8, W_ + 20, 21):
            x = gx + int(rng.integers(-7, 8))
            y = gy + int(rng.integers(-6, 7))
            yy, xx = min(max(y, 0), H_ - 1), min(max(x, 0), W_ - 1)
            if clear[yy, xx] or corridor[yy, xx]:
                continue
            pts.append((x, y))
    for (x, y) in pts:
        if rng.random() < 0.3:
            wd.tree(x, y, 34 + int(rng.integers(-4, 6)), pine=True)
        else:
            wd.tree(x, y, int(rng.integers(11, 15)), tones=TD if rng.random() < 0.6 else TG)
    fern = S2.fern()
    mush = S2.mushrooms()
    near = (dilate(path, 14) | dilate(creek, 12)) & ~dilate(path, 8) & ~clear & ~dilate(creek, 4)
    ys, xs = np.nonzero(near)
    for i in rng.choice(len(ys), 70, replace=False):
        x, y = xs[i], ys[i]
        spr = fern if i % 3 else mush
        wd.add(spr, x - spr.shape[1] // 2, y - spr.shape[0], box=None)
    wd.add(S2.log(), 196, 300, box=(0, 1, 26, 7))
    wd.add(S2.log(), 200, 484, box=(0, 1, 26, 7))
    for (x, y) in ((214, 244), (204, 420), (204, 566), (322, 270), (318, 420)):
        wd.add(P.rock(2), x, y, box=(0, 3, 14, 9))
    wd.act([190, 292, 228, 310], 'log', 'LOOK')

    # ---- TAVERN at the crossroads
    roof_dk = ((132, 112, 100), (100, 82, 74), (72, 58, 54), (48, 38, 38))
    tav_wall = ((176, 100, 70), (148, 76, 54), (104, 52, 42))
    lit = ((255, 220, 128), (255, 196, 96), (150, 96, 56))
    tav = make_house(104, 28, 26, roof_dk, tav_wall, TRIM, ((96, 120, 84), (68, 90, 60), (44, 60, 42)),
                     windows=[10, 26, 66, 82], door_x=48, chimneys=[(8, 8), (88, 8)], lit=lit,
                     shutters=((60, 84, 60), (44, 64, 48)))
    tx, ty = 150, 6
    sc.shadow_of(tav, tx, ty, 4, 3)
    th = tav.shape[0]
    wd.add(tav, tx, ty, box=(0, 12, tav.shape[1], th - 2))
    door_cx = tx + 1 + 48 + 4
    ridge = int(28 * 0.36)
    chim_y = ty + 1 + 8 + ridge - 7
    smoke = [[tx + 1 + 8 + 4, chim_y - 1], [tx + 1 + 88 + 4, chim_y - 1]]
    wd.doors.append({'r': [door_cx - 6, ty + th - 2, door_cx + 6, ty + th + 7], 'to': 'tavern', 'spawn': [128, 178], 'dir': 'up'})
    wd.act([door_cx - 7, ty + th - 10, door_cx + 7, ty + th + 2], 'tavern_door', 'ENTER')
    sign = S2.tavern_sign()
    wd.add(sign, tx + tav.shape[1] + 2, 40, box=(0, sign.shape[0] - 3, 3, sign.shape[0]))
    wd.act([tx + tav.shape[1] + 2, 40, tx + tav.shape[1] + 16, 58], 'tavern_sign', 'READ')
    for (x, y) in ((128, 52), (134, 60)):
        sc.foot_shadow(x + 6, y + 12, 6, 2)
        wd.add(P.barrel(), x, y, box=(1, 5, 11, 13))
    wd.add(P.woodpile(), 108, 36, box=(0, 4, 24, 14))

    # stable
    st = make_house(92, 22, 22, ((150, 128, 100), (120, 100, 78), (88, 72, 58), (60, 48, 42)),
                    ((176, 160, 136), (146, 130, 110), (106, 94, 84)), TRIM, ((0, 0, 0),) * 3, windows=[])
    hh = st.shape[0]
    wall_top = 1 + 8 + 22
    for bx in (10, 38, 66):
        for y in range(wall_top + 4, hh - 1):
            for x in range(bx, bx + 18):
                arch = (y == wall_top + 4 and x in (bx, bx + 17))
                if not arch:
                    st[y, x] = (36, 26, 30, 255) if x > bx + 1 else (70, 52, 46, 255)
        for x in range(bx + 3, bx + 15):
            st[hh - 4, x] = (214, 184, 96, 255)
            st[hh - 3, x] = (180, 148, 72, 255)
    sx, sy = 330, 8
    sc.shadow_of(st, sx, sy, 4, 3)
    wd.add(st, sx, sy, box=(0, 12, st.shape[1], hh - 2))
    railf = make_rail_fence(110, post_every=36)
    wd.add(railf, 326, 64, box=(0, 6, 110, 12))
    bay = ((196, 132, 80), (160, 96, 56), (112, 64, 40))
    grey = ((246, 242, 234), (212, 206, 200), (156, 152, 156))
    h1 = S2.horse(bay, (60, 40, 36))
    h2 = S2.horse(grey, (120, 110, 110), saddle=False)
    for (spr, x, y) in ((h1, 340, 60), (h2, 396, 62)):
        sc.foot_shadow(x + 15, y + spr.shape[0] - 2, 11, 2.5)
        wd.add(spr, x, y, box=(6, spr.shape[0] - 7, 22, spr.shape[0] - 1))
        wd.act([x, y, x + spr.shape[1], y + spr.shape[0]], 'horse_bay' if spr is h1 else 'horse_grey', 'LOOK')
    tr = S2.trough()
    wd.add(tr, 446, 70, box=(0, 3, tr.shape[1], tr.shape[0]))
    sp = S2.signpost()
    wd.add(sp, 312, 100, box=(6, 10, 12, 15))
    wd.act([310, 98, 330, 116], 'signpost', 'READ')

    # ---- HOMESTEAD
    roof_br = ((140, 120, 104), (108, 90, 78), (78, 64, 58), (52, 42, 40))
    weath = ((204, 186, 160), (172, 154, 132), (124, 110, 98))
    house = make_house(72, 26, 22, roof_br, weath, TRIM, ((150, 64, 50), (120, 46, 38), (84, 32, 30)),
                       windows=[7, 18, 47, 58], door_x=32, chimneys=[(31, 10)], shutters=((52, 80, 60), (38, 60, 46)))
    hx, hy = 210, 452 + DY
    sc.shadow_of(house, hx, hy, 4, 3)
    wd.add(house, hx, hy, box=(0, 12, house.shape[1], house.shape[0] - 2))
    hdoor = hx + 1 + 32 + 4
    hb = hy + house.shape[0]
    wd.act([hdoor - 7, hb - 12, hdoor + 7, hb + 2], 'house_door', 'KNOCK')
    house_smoke = [hx + 1 + 31 + 5, hy + 1 + 8 + int(26 * 0.36) - 8]
    smoke.append(house_smoke)

    barn_red = ((186, 74, 56), (150, 52, 44), (104, 36, 36))
    barn = make_house(100, 32, 28, ((144, 140, 136), (112, 108, 106), (82, 78, 80), (56, 52, 56)), barn_red, TRIM,
                      ((150, 60, 48), (120, 44, 38), (84, 30, 30)), windows=[8, 84], door_x=38, door_w=24, win_h=7)
    bxx, byy = 336, 444 + DY
    sc.shadow_of(barn, bxx, byy, 4, 3)
    wd.add(barn, bxx, byy, box=(0, 12, barn.shape[1], barn.shape[0] - 2))
    bdoor = bxx + 1 + 38 + 12
    bb = byy + barn.shape[0]
    wd.act([bdoor - 14, bb - 12, bdoor + 14, bb + 2], 'barn_door', 'LOOK')

    coop = make_house(30, 12, 10, roof_br, weath, TRIM, ((90, 64, 44), (70, 48, 34), (50, 34, 26)), door_x=11)
    wd.add(coop, 452, 494 + DY, box=(0, 8, coop.shape[1], coop.shape[0] - 1))
    wd.act([452, 494 + DY, 484, 528 + DY], 'coop', 'LOOK')
    lau = S2.laundry()
    wd.add(lau, 290, 470 + DY, box=(0, lau.shape[0] - 4, 5, lau.shape[0]))
    wd.add(lau, 290, 470 + DY, box=(lau.shape[1] - 5, lau.shape[0] - 4, lau.shape[1], lau.shape[0]), z=-99999)
    wd.objects.pop()  # second call only added collision
    wd.act([290, 470 + DY, 336, 498 + DY], 'laundry', 'LOOK')
    wl = P.well()
    sc.shadow_of(wl, 294, 538 + DY, 3, 2)
    wd.add(wl, 294, 538 + DY, box=(0, 6, wl.shape[1], wl.shape[0]))
    wd.act([292, 538 + DY, 314, 558 + DY], 'well', 'LOOK')
    hay = P.haystack()
    for (x, y) in ((440, 524 + DY), (458, 534 + DY)):
        sc.foot_shadow(x + 11, y + 12, 10, 3)
        wd.add(hay, x, y, box=(1, 3, 19, 12))
    wd.add(P.woodpile(), 182, 520 + DY, box=(0, 4, 24, 14))
    wd.add(P.stump(), 208, 524 + DY, box=(1, 6, 11, 12))
    wd.act([180, 518 + DY, 222, 538 + DY], 'woodpile', 'LOOK')

    # kitchen garden
    gx0, gy0, gx1, gy1 = 66, 460 + DY, 152, 508 + DY
    for y in range(gy0, gy1):
        for x in range(gx0, gx1):
            k = (y - gy0) % 6
            sc.img[y, x] = (120, 80, 52) if k < 3 else ((96, 62, 42) if k == 3 else (144, 100, 64))
    for y in range(gy0 + 1, gy1 - 4, 6):
        for x in range(gx0 + 3, gx1 - 6, 9):
            spr = P.cabbage() if (x // 9 + y // 6) % 2 else P.pumpkin()
            if gx0 + 30 < x < gx0 + 46:
                continue
            sc.blit(spr, x, y - 2)
    wd.add(make_rail_fence(92), 62, 450 + DY, box=(0, 4, 92, 12))
    wd.add(make_rail_fence(92), 62, 506 + DY, box=(0, 4, 92, 12))
    wd.add(make_vfence(56), 60, 456 + DY, z=512 + DY)
    wd.add(make_vfence(26), 151, 456 + DY, z=512 + DY)
    wd.act([64, 458 + DY, 154, 510 + DY], 'garden', 'LOOK')

    # fields behind a split-rail fence
    for x0, x1 in ((38, 268), (304, 542)):
        wd.add(make_rail_fence(x1 - x0), x0, 556 + DY, box=(0, 4, x1 - x0, 12))
    # corn (walk-through)
    corn = S2.corn()
    for gy in range(574 + DY, 676 + DY, 12):
        for gx in range(48, 176, 9):
            ox = 4 if (gy // 12) % 2 else 0
            wd.add(corn, gx + ox + int(rng.integers(-1, 2)), gy - 14, box=None)
    wd.act([44, 566 + DY, 184, 684 + DY], 'corn', 'LOOK')
    # wheat, struck with rust: worst beside the barberry hedge on its west edge, healthier to the east
    rn = value_noise(H_, W_, 7, rng)
    for y in range(570 + DY, 684 + DY):
        for x in range(196, 342):
            k = (x + (y // 3)) % 4
            c = (236, 204, 112) if k == 0 else ((214, 176, 84) if k < 3 else (176, 136, 64))
            if (y % 6) == 0:
                c = (160, 124, 58)
            sick = max(0.0, 1 - (x - 196) / 130) * 0.85 + (rn[y, x] - 0.5) * 0.6
            h = ((x * 73856093) ^ (y * 19349663)) % 1000 / 1000
            if h < sick * 0.75:
                c = (182, 96, 46) if k < 2 else ((146, 70, 38) if k == 2 else (120, 56, 34))
            elif h < sick:
                c = (196, 168, 104) if k else (170, 140, 86)
            sc.put(x, y, c)
    for x in range(196, 342):
        sc.put(x, 569 + DY, (120, 92, 50))
    st_k = S2.stook()
    for (x, y) in ((310, 596 + DY), (318, 652 + DY)):
        wd.add(st_k, x, y, box=(2, 7, 10, 11))
    wd.act([194, 568 + DY, 344, 686 + DY], 'wheat', 'LOOK')
    # barberry hedge between the corn and the wheat
    BARB = ((44, 70, 40), (74, 108, 50), (112, 146, 64), (164, 190, 98))
    for i, y in enumerate(range(556 + DY, 676 + DY, 8)):
        t = make_tree(7, BARB, rng, fruit=((236, 40, 52), (160, 24, 40)))
        x = 176 + int(rng.integers(-1, 2))
        wd.add(t, x, y, box=(5, t.shape[0] - 10, t.shape[1] - 5, t.shape[0] - 2))
    wd.act([178, 560 + DY, 198, 690 + DY], 'barberry', 'LOOK')
    # flax (blue flowers) and pumpkins
    for y in range(570 + DY, 626 + DY):
        for x in range(356, 452):
            c = (84, 140, 72) if (x + y) % 3 else (64, 116, 60)
            if (x * 7 + y * 13) % 11 == 0:
                c = (128, 160, 232)
            if (x * 5 + y * 3) % 29 == 0:
                c = (196, 212, 255)
            sc.put(x, y, c)
    wd.act([354, 568 + DY, 454, 628 + DY], 'flax', 'LOOK')
    for y in range(636 + DY, 686 + DY):
        for x in range(356, 452):
            sc.img[y, x] = (100, 74, 48) if (y // 4) % 2 else (120, 88, 56)
    for y in range(638 + DY, 680 + DY, 10):
        for x in range(360, 444, 12):
            for k in range(6):
                sc.put(x + k, y + 4 + (k % 2), (64, 128, 56))
            sc.blit(P.pumpkin(), x + int(rng.integers(0, 4)), y)
    wd.act([354, 634 + DY, 454, 688 + DY], 'pumpkins', 'LOOK')

    # orchard
    for (x, y) in ((506, 450 + DY), (536, 486 + DY), (500, 530 + DY), (530, 562 + DY)):
        wd.tree(x, y, 11, kind='a')
    for (x, y) in ((40, 452 + DY), (28, 520 + DY)):
        wd.tree(x, y, 12)

    # NPCs
    wd.npcs.append({'id': 'wife', 'row': 0, 'x': 112, 'y': 492 + DY, 'dir': 'down'})
    wd.block[489 + DY:493 + DY, 106:118] = True
    data = {'w': W_, 'h': H_, 'smoke': [[int(a), int(b)] for a, b in smoke],
            'chickens': [[470, 540 + DY], [486, 534 + DY], [462, 548 + DY], [420, 552 + DY]],
            'sound': {'creek': [list(p) for p in CREEK], 'bridge': [bx0 - 4, by0 - 2, bx1 + 4, by1 + 2],
                      'barn': [bdoor, bb], 'stable': [[354, 78], [410, 80]], 'door': [door_cx, ty + th], 'forest': [146, 622]},
            'acts': wd.acts, 'doors': wd.doors, 'npcs': wd.npcs}
    return wd, data


# ============================================================ TAVERN INTERIOR
def tavern():
    W_, H_ = 256, 192
    wd = World(W_, H_, 99)
    sc, rng = wd.sc, wd.rng
    # floor: vertical boards
    for x in range(W_):
        board = x // 8
        tint = ((board * 37) % 5 - 2) * 5
        for y in range(H_):
            k = x % 8
            c = (170, 120, 78) if k == 0 else ((150, 104, 66) if k < 6 else (124, 84, 54))
            if k == 7:
                c = (86, 58, 40)
            if (y + board * 23) % 41 == 0:
                c = (86, 58, 40)
            if (y + board * 23) % 41 in (3,) and k in (2, 5):
                c = (70, 50, 40)
            sc.img[y, x] = np.clip(np.array(c) + tint, 0, 255)
    # braided rug
    rug = ellipse(sc.shape, 120, 136, 34, 13)
    yy, xx = np.mgrid[0:H_, 0:W_]
    rr = np.sqrt(((xx - 120) / 34) ** 2 + ((yy - 136) / 13) ** 2)
    ring = (rr * 6).astype(int)
    pal = [(150, 60, 48), (190, 140, 80), (110, 70, 90), (170, 84, 60), (120, 110, 70), (90, 46, 40)]
    for i in range(6):
        sc.img[rug & (ring == i)] = pal[i]
    sc.img[rug & ~erode(rug, 1)] = (60, 36, 34)
    # back wall
    for y in range(0, 58):
        for x in range(W_):
            if y < 4:
                c = (84, 56, 40) if y < 3 else (52, 36, 30)
            elif y < 40:
                c = (226, 214, 190) if (x * 3 + y * 7) % 23 else (210, 196, 172)
                if x % 48 < 4:
                    c = (104, 70, 48) if x % 48 < 3 else (70, 48, 36)
            elif y < 43:
                c = (176, 124, 80) if y == 40 else (128, 88, 56)
            elif y < 56:
                px = x % 24
                c = (120, 80, 52)
                if px in (0, 23) or y in (43, 55):
                    c = (90, 60, 40)
                elif px in (1,) or y == 44:
                    c = (146, 100, 64)
            else:
                c = (60, 40, 32)
            sc.img[y, x] = c
    for x in range(W_):
        sc.img[58, x] *= 0.7
        sc.img[59, x] *= 0.85
    # windows
    for wx in (22, 152):
        for y in range(10, 34):
            for x in range(wx, wx + 24):
                c = (150, 196, 230) if (x - wx) % 8 not in (0,) and (y - 10) % 8 != 0 else (232, 228, 218)
                if x in (wx, wx + 23) or y in (10, 33):
                    c = (110, 74, 50)
                if c == (150, 196, 230) and (x + y) % 9 == 0:
                    c = (210, 236, 250)
                sc.put(x, y, c)
        for x in range(wx - 1, wx + 25):
            sc.put(x, 34, (176, 124, 80)); sc.put(x, 35, (110, 74, 50))
    # shelves behind the bar
    for sy in (14, 30):
        for x in (196, 197):
            pass
        for x in range(194, 248):
            sc.put(x, sy, (176, 124, 80)); sc.put(x, sy + 1, (110, 74, 50)); sc.put(x, sy + 2, (150, 136, 112))
        for i, x in enumerate(range(197, 244, 6)):
            kind = (i + sy) % 3
            if kind == 0:  # bottle
                for y in range(sy - 8, sy):
                    c = (60, 110, 70) if y > sy - 6 else (50, 80, 60)
                    sc.put(x, y, c); sc.put(x + 1, y, (90, 150, 100) if y > sy - 6 else c)
            elif kind == 1:  # mug
                for y in range(sy - 5, sy):
                    for dx in range(3):
                        sc.put(x + dx, y, (190, 194, 204) if dx == 0 else (140, 146, 160))
                sc.put(x + 3, sy - 3, (140, 146, 160))
            else:  # jug
                for y in range(sy - 7, sy):
                    for dx in range(4):
                        sc.put(x + dx, y, (196, 150, 100) if dx < 2 else (160, 116, 76))
    # fireplace
    fx0, fx1 = 88, 144
    stone = np.zeros(sc.shape, bool)
    stone[4:62, fx0:fx1] = True
    from harbor import cobbles
    cobbles(sc, stone, rng, pal=((196, 188, 176), (160, 152, 144), (118, 112, 110), (64, 58, 62)))
    for y in range(18, 23):
        for x in range(fx0 - 4, fx1 + 4):
            sc.put(x, y, (130, 88, 56) if y == 18 else ((104, 70, 46) if y < 22 else (60, 40, 32)))
    for y in range(28, 60):
        for x in range(100, 132):
            d = abs(x - 116) / 16
            c = (20, 12, 18) if d < 0.85 else (44, 30, 34)
            if y < 31:
                c = (44, 30, 34)
            sc.put(x, y, c)
    for y in range(60, 68):
        for x in range(92, 140):
            sc.put(x, y, (150, 144, 138) if y < 62 else ((126, 120, 116) if y < 66 else (84, 78, 80)))
    # mantel items
    for x in (96, 136):
        for y in range(10, 18):
            sc.put(x, y, (240, 232, 200) if y > 12 else (255, 210, 110))
            sc.put(x + 1, y, (210, 200, 170) if y > 12 else (255, 180, 80))
    # side & bottom walls
    for y in range(H_):
        for x in list(range(0, 6)) + list(range(250, 256)):
            sc.img[y, x] = (70, 48, 36) if x not in (5, 250) else (110, 76, 52)
    for y in range(184, 192):
        for x in range(W_):
            if 118 <= x < 138:
                c = (60, 40, 30) if y > 186 else (130, 90, 58)
            else:
                c = (84, 56, 40) if y > 185 else (130, 90, 58)
            sc.img[y, x] = c
    for y in range(174, 184):
        for x in range(116, 140):
            c = (150, 60, 48) if (x + y) % 4 else (120, 46, 38)
            if y in (174, 183) or x in (116, 139):
                c = (80, 34, 30)
            sc.img[y, x] = c

    # collision
    wd.block[:60, :] = True
    wd.block[:, :7] = True
    wd.block[:, 249:] = True
    wd.block[182:, :116] = True
    wd.block[182:, 140:] = True
    wd.block[58:68, 90:142] = True

    # bar + kegs + keeper
    for x in (206, 220, 234):
        wd.add(P.barrel(), x - 6, 46, box=None)
    cnt = S2.counter(78)
    wd.add(cnt, 170, 72, box=None)
    wd.block[58:72 + cnt.shape[0] - 2, 170:250] = True
    wd.npcs.append({'id': 'keeper', 'row': 2, 'x': 208, 'y': 82, 'dir': 'down'})
    wd.act([170, 78, 250, 104], 'keeper', 'ORDER')
    wd.act([90, 54, 142, 74], 'fireplace', 'LOOK')
    wd.act([150, 44, 178, 70], 'window', 'LOOK')

    tables = {'t1': (22, 96), 't2': (22, 146), 't3': (98, 112), 't4': (176, 146)}
    seats = []
    tb = S2.table(40)
    mug = S2.mug()
    patrons = {('t1', 0): ('holt', 3), ('t1', 1): ('brewer', 4), ('t2', 0): ('widow', 1), ('t3', 0): ('trapper', 5)}
    for name, (tx, ty) in tables.items():
        wd.add(tb, tx, ty, box=(0, 1, tb.shape[1], tb.shape[0] - 1))
        for i, sxo in enumerate((13, 31)):
            sxp, syp = tx + sxo, ty + 9
            mx, my = sxp - 3, ty + 2
            if (name, i) in patrons:
                pid, row = patrons[(name, i)]
                wd.npcs.append({'id': pid, 'row': row, 'x': sxp, 'y': syp, 'dir': 'down', 'seated': True})
                wd.add(mug, mx, my, box=None, z=ty + tb.shape[0] + 1)
                wd.act([sxp - 8, ty - 16, sxp + 8, ty + 10], pid, 'TALK')
            else:
                seats.append({'x': sxp, 'y': syp, 'stand': [sxp, ty - 2], 'mug': [mx, my], 'z': ty + tb.shape[0] + 1,
                              'table': name})
                wd.act([sxp - 7, ty - 8, sxp + 7, ty + 10], 'seat:%d' % (len(seats) - 1), 'SIT')
    wd.doors.append({'r': [116, 180, 140, 192], 'to': 'outdoor', 'spawn': None, 'dir': 'down'})
    data = {'w': W_, 'h': H_, 'acts': wd.acts, 'doors': wd.doors, 'npcs': wd.npcs, 'seats': seats,
            'fire': [116, 58], 'smoke': [], 'chickens': []}
    return wd, data


def build_all():
    od, odata = outdoor()
    td, tdata = tavern()
    objs = [o for o in od.objects] + [o for o in td.objects]
    atlas, packed = pack(objs)
    n_out = len(od.objects)
    odata['objects'] = packed[:n_out]
    tdata['objects'] = packed[n_out:]
    # mug sprite position in atlas for the player's ale
    mug_spr = S2.mug()
    mug_empty = S2.mug(False)
    extra = [(mug_spr, 0, 0, 0), (mug_empty, 0, 0, 0)]
    atlas2, packed2 = pack(objs + extra)
    odata['objects'] = packed2[:n_out]
    tdata['objects'] = packed2[n_out:len(objs)]
    mugs = packed2[len(objs):]
    # door spawn back outside
    door_r = odata['doors'][0]['r']
    tdata['doors'][0]['spawn'] = [(door_r[0] + door_r[2]) // 2, door_r[3] + 4]

    Image.fromarray(od.sc.to_image()).save(f'{OUTDIR}/outdoor.png')
    Image.fromarray(td.sc.to_image()).save(f'{OUTDIR}/tavern.png')
    Image.fromarray(atlas2).save(f'{OUTDIR}/objects.png')
    for name, wd in (('outdoor', od), ('tavern', td)):
        m = np.zeros((wd.h, wd.w, 4), np.uint8)
        m[wd.block] = (255, 0, 0, 255)
        Image.fromarray(m).save(f'{OUTDIR}/{name}_collide.png')

    # player sheet (3 walk frames x 4 dirs)
    mm = frames(CH.MM_DOWN, CH.MM_UP, CH.MM_LEFT, CH.MM_MATS, 4)
    fw, fh = mm['down'][0].shape[1], mm['down'][0].shape[0]
    sheet = np.zeros((fh * 4, fw * 3, 4), np.uint8)
    for r, d in enumerate(['down', 'left', 'right', 'up']):
        for c in range(3):
            sheet[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw] = mm[d][c]
    Image.fromarray(sheet).save(f'{OUTDIR}/player.png')
    # people sheet: rows = wife, widow, keeper, holt, brewer, trapper ; cols = down,left,right,up
    people = [S2.wife(), S2.widow(), S2.keeper(), S2.holt(), S2.brewer(), S2.trapper()]
    ps = np.zeros((fh * len(people), fw * 4, 4), np.uint8)
    for r, fr in enumerate(people):
        for c, s in enumerate(fr):
            h, w = s.shape[:2]
            ps[r * fh + fh - h:(r + 1) * fh, c * fw + (fw - w) // 2:c * fw + (fw - w) // 2 + w] = s
    Image.fromarray(ps).save(f'{OUTDIR}/people.png')
    # dog sheet: cells 16x12, rows down,left,right,up ; 3 frames
    df = S2.dog_frames()
    cw, chh = 16, 12
    ds = np.zeros((chh * 4, cw * 3, 4), np.uint8)
    for r, d in enumerate(['down', 'left', 'right', 'up']):
        for c in range(3):
            s = df[d][c]
            h, w = s.shape[:2]
            ds[r * chh + chh - h:(r + 1) * chh, c * cw + (cw - w) // 2:c * cw + (cw - w) // 2 + w] = s
    Image.fromarray(ds).save(f'{OUTDIR}/dog.png')
    ch = P.chicken()
    chick = np.zeros((ch.shape[0] + 1, ch.shape[1] * 2, 4), np.uint8)
    chick[1:, :ch.shape[1]] = ch
    chick[:-1, ch.shape[1]:] = ch
    Image.fromarray(chick).save(f'{OUTDIR}/chicken.png')

    world = {'frame': [fw, fh], 'dog': [cw, chh], 'chicken': [ch.shape[1], ch.shape[0] + 1],
             'mug': mugs[0][:4], 'mugEmpty': mugs[1][:4],
             'start': {'map': 'outdoor', 'x': 262, 'y': 744, 'dir': 'down'},
             'maps': {'outdoor': odata, 'tavern': tdata}}
    json.dump(world, open(f'{OUTDIR}/world.json', 'w'))

    # previews
    for name, wd, data in (('outdoor', od, odata), ('tavern', td, tdata)):
        prev = wd.sc.to_image().copy()
        objs_sorted = sorted(data['objects'], key=lambda o: o[6])
        for sx, sy, w, h, x, y, z in objs_sorted:
            spr = atlas2[sy:sy + h, sx:sx + w]
            for yy in range(h):
                ty_ = y + yy
                if not (0 <= ty_ < wd.h):
                    continue
                for xx in range(w):
                    tx_ = x + xx
                    if spr[yy, xx, 3] and 0 <= tx_ < wd.w:
                        prev[ty_, tx_] = spr[yy, xx, :3]
        for npc in data['npcs']:
            s = people[npc['row']][0]
            h, w = s.shape[:2]
            x0, y0 = npc['x'] - w // 2, npc['y'] - h + (6 if npc.get('seated') else 2)
            for yy in range(h):
                for xx in range(w):
                    if s[yy, xx, 3] and 0 <= y0 + yy < wd.h and 0 <= x0 + xx < wd.w:
                        prev[y0 + yy, x0 + xx] = s[yy, xx, :3]
        Image.fromarray(prev).resize((wd.w * 2, wd.h * 2), Image.NEAREST).save(os.path.join(PREVIEW_DIR, f'{name}.png'))
    print('ok', atlas2.shape, len(odata['objects']), len(tdata['objects']))


if __name__ == '__main__':
    build_all()
