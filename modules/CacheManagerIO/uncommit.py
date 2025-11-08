# 去注释工具。

import os

def decommit(file_path: str, save_path: str) -> bool:
    """
    去除文件内的行内注释（以 # 开头的内容），保留正常代码结构。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as source, \
             open(save_path, "w", encoding="utf-8") as target:
            for line in source:
                # 跳过空行
                if not line.strip():
                    target.write("\n")
                    continue

                # 查找 # 的位置（忽略在字符串里的情况）
                quote_chars = ('"', "'")
                in_string = False
                cleaned = []
                for i, ch in enumerate(line):
                    if ch in quote_chars:
                        in_string = not in_string
                    if ch == "#" and not in_string:
                        break
                    cleaned.append(ch)
                new_line = "".join(cleaned).rstrip()
                target.write(new_line + "\n")

        return True

    except Exception as e:
        print(f"Failed to process file: {e}")
        return False



path_title: str = "G:/Codes/软件工程作业/backend/PyBackend/homework-soft-engi-backend/modules/CacheManagerIO"

decommit(path_title + "/example.py", path_title + "/example_decommit.py")
