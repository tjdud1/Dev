#!/usr/bin/env python3
import os
import subprocess
from Grok_api import Grok_req
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
    # API 키를 환경 변수에서 안전하게 불러옴
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY 환경 변수가 설정되지 않았습니다. 보안을 위해 API 키를 환경 변수로 제공하세요.")

    # 대상 소스 코드 디렉토리의 절대 경로 사용
    root_dir = os.path.abspath('../DevSecX')
    source_files_list = get_source_files(root_dir)

    if not source_files_list:
        print("탐색된 소스 파일이 없습니다.")
        return

    # 결과 저장 폴더 및 파일 지정
    reports_folder = "reports"
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)
    response_file = os.path.join(reports_folder, "response.txt")
    
    # 기존 파일이 있다면 초기화 (덮어쓰기)
    with open(response_file, "w", encoding="utf-8") as outfile:
        outfile.write("")

    # 각 소스 파일에 대해 스캔 및 LLM API 요청 실행
    for file_path in source_files_list:
        try:
            # Bandit 스캔 실행 (파일 경로를 인자로 전달하여 결과 문자열 반환)
            scan_result = run_bandit_cli(file_path)
            
            # LLM API에 전달할 프롬프트 구성
            prompt = scan_result + '''
            위 결과를 보고 밑에 조건대로 명심하고 응답하세요
            1. 한국어로 답변할 것
            2. 아래 주어진 양식대로 작성할 것
            [Example report form].

            1. Overview.  
            - Scan run date and time and target file information:  
            - Summary of the overall scan results (e.g., total number of issues detected, severity distribution, etc.):

            2. Detailed vulnerability analysis  
            - Vulnerability ID: Example) B307  
            - Vulnerability Description:  
            - Issues and security concerns related to the use of dangerous functions (e.g., eval).  
            - Severity and confidence level: e.g.) Medium, High  
            - Related CWE: CWE-78 (OS Instruction Injection)  
            - Found in: File path and code line number  
            - References: Links to related documentation

            3. Impact Analysis and Risk Assessment  
            - The impact of the vulnerability on the system or application:  
            - Security risk assessment and prioritization:

            4. Recommendations and remediation.  
            - Specific recommendations for improving the vulnerability (e.g., recommendation to use ast.literal_eval instead of eval)  
            - Suggestions for additional security best practices:

            5. Conclusion  
            - Summary of the report and recommendations for future remediation:
            '''
            # LLM API 요청 실행
            llm_response = Grok_req(prompt, api_key)
        except Exception as e:
            print(f"{file_path} 스캔 중 오류 발생: {e}")
            continue

        try:
            # 결과를 reports 폴더 내의 response.txt 파일에 추가
            with open(response_file, "a", encoding="utf-8") as outfile:
                outfile.write(f"--- {file_path} 스캔 결과 ---\n")
                outfile.write(llm_response + "\n\n")
        except Exception as e:
            print(f"{response_file} 작성 중 오류 발생: {e}")

    print(f"스캔 결과가 '{response_file}'에 저장되었습니다.")

    # Git 커밋 및 푸시 (GitHub Actions 등에서 GITHUB_TOKEN을 사용해 인증)
    try:
        # Git 사용자 설정
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        
        # 변경 사항 스테이징
        subprocess.run(["git", "add", response_file], check=True)
        # 커밋 (커밋 메시지는 필요에 따라 수정)
        subprocess.run(["git", "commit", "-m", "Add LLM API response report"], check=True)
        # 원격 저장소에 푸시 (GITHUB_TOKEN이 이미 설정되어 있다고 가정)
        subprocess.run(["git", "push"], check=True)
        print("변경사항이 Git 저장소에 커밋 및 푸시되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"Git 커밋/푸시 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
