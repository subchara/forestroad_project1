# forestroad_project1

사용 데이터:
- 옥성임도_2024.las
- 옥성임도_2024.dwg

좌표계:
EPSG:5186

# 산림도로 임도 설계 프로젝트

## 목적
지형 데이터를 분석하여 임도 설계 및 경로 탐색에 활용할
지형 정보를 생성하는 프로젝트.

## 지형 데이터 처리

### LAS
- 파일: 옥성임도_2024.las
- 점 개수: 70,164,479
- 좌표계: EPSG:5186
- 격자 크기: 5m × 5m
- Classification: Class 0 전체

Classification이 Ground로 분류되어 있지 않아
각 격자의 하위 10% 고도값(P10)을 대표 지형고도로 사용

### DXF
- BasicContours: 227개
- MajorContours: 51개
- 전체 등고선: 278개
- 좌표점: 434,681개

## 결과

### terrain_grid_5m_final.csv
5m × 5m 지형 격자 데이터

### contour.csv
DXF에서 추출한 등고선 좌표 및 고도 데이터

## 검증 결과
LAS 기반 지형 격자와 DWG 등고선을 비교

- 비교 격자: 11,973개
- 평균 고도 차이: 0.52m
- 중앙값 고도 차이: 0.39m
- 2m 이내: 98.4%
- 5m 이내: 99.7%

  
