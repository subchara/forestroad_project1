import laspy
import numpy as np
import csv
import os
import math


# ==========================================
# 설정
# ==========================================

LAS_FILE = r"C:\Users\PC\Desktop\임도 자료(DB)\옥성임도_2024.las"

OUTPUT_FILE = r"C:\Users\PC\Desktop\임도 자료(DB)\terrain_grid_5m.csv"

GRID_SIZE = 5.0

# 한 번에 처리할 LAS 점 개수
CHUNK_SIZE = 1_000_000


# ==========================================
# LAS 파일 열기
# ==========================================

print("LAS 파일을 엽니다...")

reader = laspy.open(LAS_FILE)

print()
print("===== LAS 정보 =====")

print("점 개수:", reader.header.point_count)

print(
    "X 범위:",
    reader.header.mins[0],
    "~",
    reader.header.maxs[0]
)

print(
    "Y 범위:",
    reader.header.mins[1],
    "~",
    reader.header.maxs[1]
)

print(
    "Z 범위:",
    reader.header.mins[2],
    "~",
    reader.header.maxs[2]
)

print()


# ==========================================
# 지형 범위
# ==========================================

min_x = float(reader.header.mins[0])
max_x = float(reader.header.maxs[0])

min_y = float(reader.header.mins[1])
max_y = float(reader.header.maxs[1])


# ==========================================
# 5m 격자 개수
# ==========================================

grid_x_count = int(
    math.ceil((max_x - min_x) / GRID_SIZE)
)

grid_y_count = int(
    math.ceil((max_y - min_y) / GRID_SIZE)
)

total_cells = grid_x_count * grid_y_count


print("===== 격자 정보 =====")

print("격자 크기:", GRID_SIZE, "m")

print("X 방향 격자:", grid_x_count)

print("Y 방향 격자:", grid_y_count)

print("전체 격자:", total_cells)

print()


# ==========================================
# 격자별 Z 합계 / 점 개수
#
# 1차원 배열을 사용해서 메모리와
# 인덱싱 문제를 줄임
# ==========================================

z_sum = np.zeros(
    total_cells,
    dtype=np.float64
)

z_count = np.zeros(
    total_cells,
    dtype=np.int64
)


# ==========================================
# LAS Chunk 처리
# ==========================================

processed_points = 0

print("LAS 데이터를 처리합니다.")
print("총 7천만 점 정도이므로 시간이 걸릴 수 있습니다.")
print()


with reader as las:

    for points in las.chunk_iterator(CHUNK_SIZE):

        # ----------------------------------
        # NumPy 배열로 변환
        # ----------------------------------

        x = np.asarray(points.x)
        y = np.asarray(points.y)
        z = np.asarray(points.z)

        # ----------------------------------
        # 격자 번호 계산
        # ----------------------------------

        grid_x = np.floor(
            (x - min_x) / GRID_SIZE
        ).astype(np.int64)

        grid_y = np.floor(
            (y - min_y) / GRID_SIZE
        ).astype(np.int64)

        # ----------------------------------
        # 유효 범위 확인
        # ----------------------------------

        valid = (
            (grid_x >= 0) &
            (grid_x < grid_x_count) &
            (grid_y >= 0) &
            (grid_y < grid_y_count)
        )

        grid_x = grid_x[valid]
        grid_y = grid_y[valid]
        z = z[valid]

        # ----------------------------------
        # 2차원 좌표를 1차원 인덱스로 변환
        #
        # index =
        #     y * X방향 격자 수 + x
        # ----------------------------------

        cell_index = (
            grid_y * grid_x_count +
            grid_x
        )

        # ----------------------------------
        # 격자별 Z 합계
        # ----------------------------------

        z_sum += np.bincount(
            cell_index,
            weights=z,
            minlength=total_cells
        )

        # ----------------------------------
        # 격자별 점 개수
        # ----------------------------------

        z_count += np.bincount(
            cell_index,
            minlength=total_cells
        )

        # ----------------------------------
        # 진행 상황
        # ----------------------------------

        processed_points += len(points)

        percent = (
            processed_points /
            reader.header.point_count
        ) * 100

        print(
            f"\r처리 중: "
            f"{processed_points:,} / "
            f"{reader.header.point_count:,} "
            f"({percent:.1f}%)",
            end=""
        )


print()
print()
print("LAS 처리 완료!")


# ==========================================
# 결과 CSV 생성
# ==========================================

print("CSV 파일을 생성합니다...")


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

    writer.writerow([
        "X",
        "Y",
        "Z",
        "PointCount"
    ])

    valid_cell_count = 0

    # --------------------------------------
    # 격자 순회
    # --------------------------------------

    for gy in range(grid_y_count):

        for gx in range(grid_x_count):

            index = (
                gy * grid_x_count +
                gx
            )

            count = z_count[index]

            # 점이 없는 격자는 제외
            if count == 0:
                continue

            # ----------------------------------
            # 격자 중심 좌표
            # ----------------------------------

            center_x = (
                min_x +
                (gx + 0.5) * GRID_SIZE
            )

            center_y = (
                min_y +
                (gy + 0.5) * GRID_SIZE
            )

            # ----------------------------------
            # 평균 고도
            # ----------------------------------

            average_z = (
                z_sum[index] / count
            )

            writer.writerow([
                center_x,
                center_y,
                average_z,
                count
            ])

            valid_cell_count += 1


# ==========================================
# 결과
# ==========================================

print()
print("================================")
print("변환 완료!")
print("================================")

print(
    "전체 격자:",
    total_cells
)

print(
    "데이터가 존재하는 격자:",
    valid_cell_count
)

print(
    "결과 파일:",
    OUTPUT_FILE
)

print()
print("terrain_grid_5m.csv가 생성되었습니다.")