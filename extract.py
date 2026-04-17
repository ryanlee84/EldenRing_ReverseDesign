import csv
import os
import sys

# 1. 윈도우 바탕화면 경로 오류를 막기 위해, 스크립트 파일이 있는 '진짜 위치'를 강제로 찾습니다.
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 강제로 찾은 위치에 파일 이름을 정확하게 결합합니다.
input_file = os.path.join(current_dir, 'elden_ring_dump.sql')
output_file = os.path.join(current_dir, 'atkparam_npc.csv')

print(f"▶ 스크립트가 인식한 진짜 폴더 위치: {current_dir}")
print(f"▶ 찾고 있는 파일: {input_file}\n")

try:
    if not os.path.exists(input_file):
        print("[실패] 이 폴더에 SQL 파일이 없습니다!")
        print("💡 체크: 파일 이름이 'elden_ring_dump.sql.txt' 처럼 숨겨진 확장자가 있는지 윈도우에서 확인해 보세요.")
    else:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        table_start = -1
        for i, line in enumerate(lines):
            if 'COPY public.atkparam_npc ' in line:
                table_start = i
                break

        if table_start != -1:
            header_line = lines[table_start]
            columns_str = header_line[header_line.find('(')+1 : header_line.find(')')]
            columns = [c.strip() for c in columns_str.split(',')]

            data_lines = []
            for i in range(table_start + 1, len(lines)):
                if lines[i].strip() == '\\.':
                    break
                data_lines.append(lines[i].strip('\n').split('\t'))

            with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
                writer = csv.writer(f_out)
                writer.writerow(columns)
                writer.writerows(data_lines)
            print(f"[대성공!] {len(data_lines)}개의 데이터가 {output_file} 파일로 완벽하게 추출되었습니다.")
        else:
            print("[실패] 파일은 찾았지만 atkparam_npc 테이블을 찾을 수 없습니다.")
except Exception as e:
    print(f"[에러 발생] {e}")

print("\n" + "="*50)
input("결과를 확인하셨으면 엔터(Enter) 키를 눌러 창을 닫아주세요...")