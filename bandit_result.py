#!/usr/bin/env python3
import os
from bandit_result import run_bandit_cli

def get_source_files(root_dir, extensions=(".py", ".js", ".java", ".cpp", ".c", ".h")):
    """
    주어진 루트 디렉토리 내에서 지정된 확장자를 가진 모든 소스 파일의 경로를 리스트로 반환합니다.
    """
    source_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(extensions):
                source_files.append(os.path.join(dirpath, filename))
    return source_files

def main():
    # 분석할 전체 디렉토리 경로 지정 (예: '../DevSecX')
    root_dir = os.path.abspath("../DevSecX/uploads")
    source_files = get_source_files(root_dir)

    if not source_files:
        print("탐색된 소스 파일이 없습니다.")
        return

    for file_path in source_files:
        print(f"파일: {file_path}")
        result = run_bandit_cli(file_path)
        print(result)
        print("-" * 80)

if __name__ == "__main__":
    main()
