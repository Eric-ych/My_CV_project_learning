#!/usr/bin/env python3
"""自动把 mpeg4 视频转成 H.264(可在 VSCode 内嵌预览)。

用法:
  python auto_h264.py            # 后台监听模式:持续监控,新 mpeg4 自动转 H.264
  python auto_h264.py --once     # 只扫一遍:给现有所有 mpeg4 补生成 H.264 版本
  python auto_h264.py --root DIR # 指定监控目录(默认脚本所在目录)
  python auto_h264.py --interval 3   # 轮询间隔秒数(默认 5)

产物命名:xxx.mp4(mpeg4) -> xxx_h264.mp4。原文件保留不动。
"""
import argparse, os, subprocess, sys, time

EXCLUDE_DIRS = {".venv", "__pycache__", "build", "node_modules", ".git"}


def find_mp4s(root):
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if fn.lower().endswith(".mp4") and not fn.endswith("_h264.mp4"):
                yield os.path.join(dp, fn)


def codec_of(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_name", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except Exception:
        return ""


def target_of(src):
    return src[:-4] + "_h264.mp4"


def needs_convert(src):
    """是 mpeg4,且尚无最新的 h264 版本时才需要转。"""
    if codec_of(src) != "mpeg4":
        return False
    dst = target_of(src)
    if not os.path.exists(dst):
        return True
    # 源文件比产物新 -> 重转
    return os.path.getmtime(src) > os.path.getmtime(dst)


def convert(src):
    dst = target_of(src)
    print(f"[转码] {os.path.relpath(src)}  ->  {os.path.basename(dst)}", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "20", "-movflags", "+faststart", dst],
        capture_output=True, text=True)
    if r.returncode == 0:
        print(f"[完成] {os.path.basename(dst)}", flush=True)
    else:
        print(f"[失败] {os.path.basename(src)}\n{r.stderr[-400:]}", flush=True)


def is_stable(path, seen):
    """文件大小连续两轮不变才算写完(避免转到写一半的文件)。"""
    try:
        sz = os.path.getsize(path)
    except OSError:
        return False
    key = path
    stable = seen.get(key) == sz
    seen[key] = sz
    return stable


def scan_once(root):
    n = 0
    for f in find_mp4s(root):
        if needs_convert(f):
            convert(f); n += 1
    return n


def watch(root, interval):
    print(f"[监听] 正在监控:{root}(每 {interval}s 扫描一次,Ctrl+C 停止)", flush=True)
    sizes, pending = {}, set()
    # 启动时先把存量补齐
    scan_once(root)
    while True:
        try:
            for f in find_mp4s(root):
                if needs_convert(f):
                    if is_stable(f, sizes):
                        convert(f)
                        pending.discard(f)
                    else:
                        pending.add(f)  # 还在写,下一轮再看
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[退出] 已停止监听。", flush=True)
            break


def main():
    ap = argparse.ArgumentParser(description="mpeg4 -> H.264 自动转码")
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--once", action="store_true", help="只扫一遍就退出")
    ap.add_argument("--interval", type=int, default=5, help="轮询间隔秒")
    args = ap.parse_args()

    if args.once:
        n = scan_once(args.root)
        print(f"[完成] 本次转换 {n} 个文件。", flush=True)
    else:
        watch(args.root, args.interval)


if __name__ == "__main__":
    main()
