import laspy
import numpy as np
import csv
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LAS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "옥성임도_2024.las"
)

OUTPUT_FILE = r"C:\Users\PC\Desktop\terrain_grid_5m_final.csv"

GRID_SIZE = 5.0
CHUNK_SIZE = 1_000_000
MAX_SAMPLE = 256


print("LAS 파일을 엽니다...")

reader = laspy.open(LAS_FILE)

xmin = reader.header.mins[0]
ymin = reader.header.mins[1]

samples = {}
counts = {}

rng = np.random.default_rng(42)

processed = 0
total = reader.header.point_count


# LAS 읽기

with reader as las:

    for points in las.chunk_iterator(CHUNK_SIZE):

        x = np.asarray(points.x)
        y = np.asarray(points.y)
        z = np.asarray(points.z)

        gx = np.floor(
            (x - xmin) / GRID_SIZE
        ).astype(np.int64)

        gy = np.floor(
            (y - ymin) / GRID_SIZE
        ).astype(np.int64)


        for ix, iy, zz in zip(gx, gy, z):

            key = (int(ix), int(iy))

            counts[key] = counts.get(key, 0) + 1

            if key not in samples:
                samples[key] = []

            sample = samples[key]

            n = counts[key]


            # 처음 256개는 그대로 저장
            if len(sample) < MAX_SAMPLE:

                sample.append(float(zz))


            # 이후에는 무작위 표본 유지
            else:

                j = int(
                    rng.integers(0, n)
                )

                if j < MAX_SAMPLE:

                    sample[j] = float(zz)


        processed += len(points)

        print(
            f"\r처리 중: "
            f"{processed:,} / "
            f"{total:,} "
            f"({processed / total * 100:.1f}%)",
            end=""
        )


print()
print("격자 고도를 계산합니다...")



# CSV 저장

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
        "PointCount",
        "Z_Min",
        "Z_P05",
        "Z_Mean"
    ])


    for (gx, gy), sample in samples.items():

        sample = np.asarray(
            sample,
            dtype=np.float64
        )


        grid_x = (
            xmin +
            (gx + 0.5) * GRID_SIZE
        )

        grid_y = (
            ymin +
            (gy + 0.5) * GRID_SIZE
        )


        z_min = np.min(sample)

        z_p05 = np.percentile(
            sample,
            5
        )

        z_p10 = np.percentile(
            sample,
            10
        )

        z_mean = np.mean(sample)


        writer.writerow([
            grid_x,
            grid_y,
            z_p10,
            counts[(gx, gy)],
            z_min,
            z_p05,
            z_mean
        ])


print("terrain_grid_5m_final.csv 생성 완료")
print("========================================")

print("파일:")
print(OUTPUT_FILE)

print("격자 수:", len(samples))

print("최종 Z = 5m 격자 내 Z값의 하위 10%")

print("좌표계 = EPSG:5186")
print("격자 크기 = 5m × 5m")
