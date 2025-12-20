#!/usr/bin/env python3
"""
简单的 JSON 自动缩进脚本：接收一个或多个 JSON 文件路径，原地格式化为 2 空格缩进，并保持中文字符不转义。
用法：
    python scripts/format_json.py path/to/file.json [other.json ...]
"""
import argparse
import json
from pathlib import Path


def format_file(path: Path, indent: int = 2) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="格式化 JSON 文件（原地修改）")
    parser.add_argument("files", nargs="+", help="要格式化的 JSON 文件路径")
    parser.add_argument("--indent", type=int, default=2, help="缩进空格数，默认 2")
    args = parser.parse_args()

    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"跳过：文件不存在 {p}")
            continue
        try:
            format_file(p, indent=args.indent)
            print(f"已格式化：{p}")
        except Exception as e:
            print(f"格式化失败 {p}: {e}")


if __name__ == "__main__":
    main()
