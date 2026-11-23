#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从四个子仓里取代表图，压成 README 用的缩略图。

这个仓本身不放源码，只放一张总览。但 README 里的图不能引用别的仓的路径
（GitHub 的 ![]() 不走跨仓相对路径，也不该让本仓的 README 依赖别人的文件在不在），
所以把四张代表图复制一份过来。

唯一要守的规矩：**别用手截图，也别在这里改图**。
源图改了就在兄弟仓里重跑它自己的出图脚本，再跑这里一次，缩略图自动跟上。

用法（从本仓根目录）：python tools/make_thumbs.py
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIBLING = os.path.dirname(HERE)          # 四个仓的公共父目录
OUT = os.path.join(HERE, "shots")
WIDTH = 1400

# (源仓内相对路径, 输出名)
SRC = [
    ("v12-engine/shots/overview.png",                  "01-v12.png"),
    ("arm-mujoco-sim/shots/02-iso.png",                "02-arm.png"),
    ("hw-designs/pcb-alcohol/shots/05-annotated.png",  "03-pcb.png"),
    ("hw-designs/pcb-alcohol/shots/03-copper.png",     "04-copper.png"),
    ("ar-subtitle-ui/shots/A-songti.png",              "05-ui.png"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for rel, name in SRC:
        src = os.path.join(SIBLING, rel)
        if not os.path.isfile(src):
            print("跳过（源图不存在）：%s" % rel)
            continue
        im = Image.open(src).convert("RGB")
        if im.width > WIDTH:
            h = round(im.height * WIDTH / im.width)
            im = im.resize((WIDTH, h), Image.LANCZOS)
        dst = os.path.join(OUT, name)
        im.save(dst, optimize=True)
        print("%-14s %-12s %5d KB  <- %s" % (name, "%dx%d" % im.size,
                                             os.path.getsize(dst) // 1024, rel))


if __name__ == "__main__":
    main()
