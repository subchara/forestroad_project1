import csv
import math
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
# 파일
# ==========================================

GRID_FILE = os.path.join(
    PROJECT_DIR,
    "results",
    "terrain_grid_5m_final.csv"
)

CONTOUR_FILE = os.path.join(
    PROJECT_DIR,
    "results",
    "contour.csv"
)


# ==========================================
# 파일 확인
# ==========================================

if not os.path.exists(GRID_FILE):

    print("terrain_grid_5m_final.csv를 찾을 수 없습니다.")

    print(GRID_FILE)

    exit()


if not os.path.exists(CONTOUR_FILE):

    print("contour.csv를 찾을 수 없습니다.")

    print(CONTOUR_FILE)

    exit()


# ==========================================
# Grid 읽기
# ==========================================

print("terrain_grid_5m_final.csv 읽는 중...")

grid = []


with open(
    GRID_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        grid.append({
            "x": float(row["X"]),
            "y": float(row["Y"]),
            "z": float(row["Z"])
        })


print(
    "격자 수:",
    f"{len(grid):,}"
)


# ==========================================
# Contour 읽기
# ==========================================

print()

print("contour.csv 읽는 중...")

contours = []


with open(
    CONTOUR_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        contours.append({
            "x": float(row["X"]),
            "y": float(row["Y"]),
            "z": float(row["Elevation"])
        })


print(
    "등고선 좌표점:",
    f"{len(contours):,}"
)


# ==========================================
# 공간 인덱스
# ==========================================

print()

print("등고선 공간 인덱스를 만드는 중...")


contour_index = {}


for point in contours:

    cell_x = math.floor(
        point["x"] / 5
    )

    cell_y = math.floor(
        point["y"] / 5
    )


    key = (
        cell_x,
        cell_y
    )


    if key not in contour_index:

        contour_index[key] = []


    contour_index[key].append(
        point
    )


# ==========================================
# 비교
# ==========================================

print()

print("고도 비교 중...")


differences = []

matched = 0


for i, g in enumerate(grid):

    cell_x = math.floor(
        g["x"] / 5
    )

    cell_y = math.floor(
        g["y"] / 5
    )


    candidates = []


    # 주변 3×3 셀 검색
    for dx in range(-1, 2):

        for dy in range(-1, 2):

            key = (
                cell_x + dx,
                cell_y + dy
            )


            if key in contour_index:

                candidates.extend(
                    contour_index[key]
                )


    if not candidates:

        continue


    # 가장 가까운 등고선 점
    min_distance = float("inf")

    nearest_z = None


    for c in candidates:

        distance = math.sqrt(

            (g["x"] - c["x"]) ** 2 +

            (g["y"] - c["y"]) ** 2

        )


        if distance < min_distance:

            min_distance = distance

            nearest_z = c["z"]


    # 5m 이내만 비교
    if min_distance <= 5.0:

        difference = abs(
            g["z"] - nearest_z
        )


        differences.append(
            difference
        )


        matched += 1


    if (i + 1) % 1000 == 0:

        print(
            f"\r진행: "
            f"{i + 1:,} / "
            f"{len(grid):,}",
            end=""
        )


print()


# ==========================================
# 결과
# ==========================================

print()

print("========================================")

print("LAS 격자 ↔ DWG 등고선 비교 결과")

print("========================================")


if len(differences) == 0:

    print("비교할 데이터가 없습니다.")

else:

    differences.sort()


    average = (
        sum(differences)
        /
        len(differences)
    )


    minimum = differences[0]

    maximum = differences[-1]


    median = differences[
        len(differences) // 2
    ]


    under_1m = sum(
        1
        for d in differences
        if d <= 1
    )


    under_2m = sum(
        1
        for d in differences
        if d <= 2
    )


    under_5m = sum(
        1
        for d in differences
        if d <= 5
    )


    print()

    print(
        "비교된 격자:",
        f"{matched:,}"
    )


    print(
        "평균 고도 차이:",
        f"{average:.2f} m"
    )


    print(
        "중앙값 고도 차이:",
        f"{median:.2f} m"
    )


    print(
        "최소 고도 차이:",
        f"{minimum:.2f} m"
    )


    print(
        "최대 고도 차이:",
        f"{maximum:.2f} m"
    )


    print()


    print(
        "1m 이하:",
        f"{under_1m:,}",
        f"({under_1m / len(differences) * 100:.1f}%)"
    )


    print(
        "2m 이하:",
        f"{under_2m:,}",
        f"({under_2m / len(differences) * 100:.1f}%)"
    )


    print(
        "5m 이하:",
        f"{under_5m:,}",
        f"({under_5m / len(differences) * 100:.1f}%)"
    )


print()

print("분석 완료.")
