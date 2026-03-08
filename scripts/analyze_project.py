#!/usr/bin/env python3
"""
示例脚本：分析项目目录结构
"""
import os
import json

def analyze_directory(directory):
    """分析目录结构"""
    result = {
        "name": os.path.basename(directory),
        "type": "directory",
        "children": []
    }
    
    for item in sorted(os.listdir(directory)):
        if item.startswith("."):
            continue  # 跳过隐藏文件和目录
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            result["children"].append(analyze_directory(item_path))
        else:
            result["children"].append({
                "name": item,
                "type": "file",
                "size": os.path.getsize(item_path)
            })
    
    return result

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    structure = analyze_directory(project_root)
    print(json.dumps(structure, indent=2, ensure_ascii=False))
