"""비효율 지도 STEP 3: 2호선 구간별 풍경 기초 점수 표시.

STEP 2의 최단경로 계산을 그대로 이용하고, 별도로 조사한 지상/한강 구간
메타데이터로 그 경로의 풍경 점수를 평가합니다.
주의: 현재는 대체 경로를 추천하지 않습니다. 점수는 설계 예시이며 실제 조망 품질이 아닙니다.
"""

import csv
from pathlib import Path

from inefficient_map_step2 import load_graph, shortest_path, clean_station_name, format_time

SCENERY_FILE = Path(__file__).resolve().parent / "data" / "line2_scenery_v1.csv"
SURFACE_POINTS = 2
RIVER_BONUS = 8
VALID_STATUSES = {"surface", "transition", "unclassified"}


def edge_key(a, b):
    return frozenset((a, b))


def load_scenery(graph, csv_path=SCENERY_FILE):
    """STEP 2 노선의 43개 연결을 정확히 하나씩 주석 데이터와 연결합니다."""
    known_edges = {edge_key(a, b) for a, items in graph.items() for b, *_ in items}
    rows = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"start_station", "end_station", "ground_status", "han_river_crossing", "description"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("풍경 CSV에 필요한 열이 없습니다.")
        for row in reader:
            a, b = row["start_station"].strip(), row["end_station"].strip()
            key = edge_key(a, b)
            status = row["ground_status"].strip()
            crossing = row["han_river_crossing"].strip().lower()
            if (not a or not b or a == b or key not in known_edges or key in rows
                    or status not in VALID_STATUSES or crossing not in {"true", "false"}):
                raise ValueError(f"풍경 CSV 연결이 잘못되었습니다: {a} - {b}")
            if crossing == "true" and status != "surface":
                raise ValueError(f"한강 횡단 구간은 지상 구간이어야 합니다: {a} - {b}")
            rows[key] = {"ground_status": status,
                         "han_river_crossing": crossing == "true",
                         "description": row["description"].strip()}
    if set(rows) != known_edges or len(rows) != 43:
        raise ValueError("풍경 CSV가 STEP 2의 43개 구간을 모두 포함하지 않습니다.")
    return rows


def section_score(section):
    """가중치 예시: 확인된 지상 +2, 한강 횡단 추가 +8, 미분류/전환 0."""
    return ((SURFACE_POINTS if section["ground_status"] == "surface" else 0)
            + (RIVER_BONUS if section["han_river_crossing"] else 0))


def score_path(path, scenery):
    """연속된 경로를 평가: (총점, 지상수, 한강수, 미확인수, 관심구간 목록)."""
    if len(path) < 2:
        return 0, 0, 0, 0, []
    score = surface_count = river_count = unconfirmed_count = 0
    highlights = []
    for a, b in zip(path, path[1:]):
        key = edge_key(a, b)
        if key not in scenery:
            raise ValueError(f"풍경 정보에 없는 연결: {a} - {b}")
        part = scenery[key]
        value = section_score(part)
        score += value
        surface_count += (part["ground_status"] == "surface")
        river_count += part["han_river_crossing"]
        unconfirmed_count += (part["ground_status"] != "surface")
        if value > 0:
            highlights.append((a, b, value, part["description"]))
    return score, surface_count, river_count, unconfirmed_count, highlights


def main():
    try:
        graph = load_graph()
        scenery = load_scenery(graph)
    except (FileNotFoundError, UnicodeError, ValueError) as exc:
        print("데이터 파일을 읽지 못했습니다:", exc)
        print("STEP 2 및 STEP 3 데이터가 data/ 폴더에 있는지 확인해 주세요.")
        return

    print("=== 비효율 지도: 경로 풍경 점수 분석 (STEP 3) ===")
    print("공식 역간 소요시간 + 출처 기반 지상/한강 구간 주석 (43구간)")
    print("※ 점수 +2(확인된 지상 구간), +8(한강 횡단)는 자체 설계한 임시 기준입니다.")
    print("※ 미분류 구간의 0점은 지하라는 뜻이 아닙니다.")
    print()
    start = clean_station_name(input("출발역 (예: 합정): "))
    end = clean_station_name(input("도착역 (예: 당산): "))
    if start not in graph or end not in graph or start == end:
        print("지원되지 않는 역이거나 출발역과 도착역이 같습니다.")
        return
    path, seconds, distance = shortest_path(graph, start, end)
    if not path:
        print("연결된 경로가 없습니다.")
        return
    points, n_surface, n_river, n_unconfirmed, highlights = score_path(path, scenery)
    print()
    print("--- STEP 2 최단경로 + STEP 3 풍경 분석 ---")
    print("최단경로:", " → ".join(path))
    print("표준 구간 소요시간 합계:", format_time(seconds))
    print("구간 거리 합계: {:.1f} km".format(distance))
    print("풍경 점수(임시):", points)
    print("지상 확인 구간:", n_surface, "/ 한강 횡단:", n_river,
          "/ 미분류·경계 구간:", n_unconfirmed)
    if highlights:
        print("풍경 포인트:")
        for a, b, value, description in highlights:
            print(f"  - {a} → {b}: +{value}점 ({description})")
    else:
        print("해당 경로에 확인된 풍경 포인트가 없습니다. (추가 조사 필요)")
    print("※ 대체 경로 추천은 STEP 4에서 구현합니다.")
    print("※ 운행시간과 풍경 점수 모두 실제 탑승 환경을 보장하지 않습니다.")


if __name__ == "__main__":
    main()
