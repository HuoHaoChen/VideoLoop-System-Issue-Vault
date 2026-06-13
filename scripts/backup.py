#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 一键备份：把整个仓库打包到 backups/（3-2-1 的第一份）
import os, sys, datetime, zipfile

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
outdir = os.path.join(ROOT, "backups")
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, "VideoLoop-" + stamp + ".zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for base, _, fs in os.walk(ROOT):
        if "backups" in base:
            continue
        for fn in fs:
            fp = os.path.join(base, fn)
            z.write(fp, os.path.relpath(fp, ROOT))
print("已备份到", out)
print("提醒：再把这个 zip 复制到云盘/U盘，满足 3-2-1（3份 2介质 1异地）")
