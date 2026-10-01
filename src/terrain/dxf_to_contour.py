import ezdxf
import csv
import os


# ==========================================
# 파일 경로
# ==========================================

DXF_FILE = r"C:\Users\PC\Desktop\임도 자료(DB)\ImageToStl.com_옥성임도_2024.dxf"

OUTPUT_FILE = r"C:\Users\PC\Desktop\임도 자료(DB)\contour.csv"


# ==========================================
# DXF 열기
# ==========================================

print("DXF 파일을 엽니다...")

doc = ezdxf.readfile(DXF_FILE)

msp = doc.modelspace()


# ==========================================
# 등고선 추출
# ==========================================

rows = []

contour_id = 0

basic_count = 0
major_count = 0

point_count = 0


for entity in msp:

    # 등고선 객체만 처리
    if entity.dxftype() != "LWPOLYLINE":
        continue


    layer = entity.dxf.layer

    # 실제 등고선 레이어만 처리
    if layer not in ["BasicContours", "MajorContours"]:
        continue


    contour_id += 1


    # --------------------------------------
    # 등고선의 고도
    # --------------------------------------

    elevation = float(
        entity.dxf.elevation
    )


    # --------------------------------------
    # 레이어별 개수
    # --------------------------------------

    if layer == "BasicContours":
        basic_count += 1

    elif layer == "MajorContours":
        major_count += 1


    # --------------------------------------
    # 등고선 좌표 추출
    # --------------------------------------

    points = entity.get_points()


    for point_index, point in enumerate(points):

        x = float(point[0])
        y = float(point[1])


        rows.append([
            layer,
            contour_id,
            point_index,
            x,
            y,
            elevation
        ])


        point_count += 1


# ==========================================
# CSV 저장
# ==========================================

print()
print("CSV 파일을 저장합니다...")


output_folder = os.path.dirname(
    OUTPUT_FILE
)

if output_folder:
    os.makedirs(
        output_folder,
        exist_ok=True
    )


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    # 헤더
    writer.writerow([
        "Layer",
        "ContourID",
        "PointIndex",
        "X",
        "Y",
        "Elevation"
    ])


    # 데이터
    writer.writerows(rows)


# ==========================================
# 결과 출력
# ==========================================

print()
print("========================================")
print("DXF 등고선 추출 완료")
print("========================================")

print()

print(
    "BasicContours:",
    basic_count,
    "개"
)

print(
    "MajorContours:",
    major_count,
    "개"
)

print(
    "전체 등고선:",
    contour_id,
    "개"
)

print(
    "전체 좌표점:",
    point_count,
    "개"
)

print()

print(
    "결과 파일:",
    OUTPUT_FILE
)

print()
print("contour.csv 생성 완료!")