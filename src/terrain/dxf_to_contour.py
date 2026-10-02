import ezdxf
import csv
import os


# ==========================================
# 프로젝트 폴더
# ==========================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================
# 입력 / 출력
# ==========================================

DXF_FILE = os.path.join(
    PROJECT_DIR,
    "data",
    "옥성임도_2024_1.dxf"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR,
    "results"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "contour.csv"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==========================================
# 파일 확인
# ==========================================

if not os.path.exists(DXF_FILE):

    print("DXF 파일을 찾을 수 없습니다.")
    print()
    print(DXF_FILE)

    input("\nEnter를 누르면 종료합니다.")
    exit()


# ==========================================
# DXF 열기
# ==========================================

print("DXF 파일을 엽니다...")

doc = ezdxf.readfile(
    DXF_FILE
)

msp = doc.modelspace()


# ==========================================
# 등고선 레이어
# ==========================================

TARGET_LAYERS = {
    "BasicContours",
    "MajorContours"
}


# ==========================================
# CSV 저장
# ==========================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Layer",
        "ContourID",
        "PointIndex",
        "X",
        "Y",
        "Elevation"
    ])


    contour_id = 0

    total_points = 0

    basic_count = 0
    major_count = 0


    # ======================================
    # 모든 Entity 확인
    # ======================================

    for entity in msp:

        layer = entity.dxf.layer


        if layer not in TARGET_LAYERS:

            continue


        # ----------------------------------
        # LWPOLYLINE
        # ----------------------------------

        if entity.dxftype() == "LWPOLYLINE":

            contour_id += 1

            if layer == "BasicContours":
                basic_count += 1

            elif layer == "MajorContours":
                major_count += 1


            elevation = entity.dxf.get(
                "elevation",
                0
            )


            points = entity.get_points()


            for point_index, point in enumerate(points):

                x = point[0]
                y = point[1]

                writer.writerow([
                    layer,
                    contour_id,
                    point_index,
                    x,
                    y,
                    elevation
                ])

                total_points += 1


        # ----------------------------------
        # POLYLINE
        # ----------------------------------

        elif entity.dxftype() == "POLYLINE":

            contour_id += 1

            if layer == "BasicContours":
                basic_count += 1

            elif layer == "MajorContours":
                major_count += 1


            vertices = list(
                entity.vertices()
            )


            for point_index, vertex in enumerate(vertices):

                location = vertex.dxf.location


                x = location.x
                y = location.y
                z = location.z


                writer.writerow([
                    layer,
                    contour_id,
                    point_index,
                    x,
                    y,
                    z
                ])

                total_points += 1


        # ----------------------------------
        # LINE
        # ----------------------------------

        elif entity.dxftype() == "LINE":

            contour_id += 1

            if layer == "BasicContours":
                basic_count += 1

            elif layer == "MajorContours":
                major_count += 1


            start = entity.dxf.start
            end = entity.dxf.end


            writer.writerow([
                layer,
                contour_id,
                0,
                start.x,
                start.y,
                start.z
            ])

            writer.writerow([
                layer,
                contour_id,
                1,
                end.x,
                end.y,
                end.z
            ])


            total_points += 2


# ==========================================
# 완료
# ==========================================

print("DXF 등고선 추출 완료")

print("BasicContours:", basic_count)

print("MajorContours:", major_count)

print("전체 등고선:", contour_id)

print("전체 좌표점:", total_points)

print()
print("결과 파일:")

print(OUTPUT_FILE)
