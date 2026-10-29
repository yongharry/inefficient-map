"""비효율 지도 STEP 2: 공식 역간 소요시간을 이용한 2호선 순환선 최단경로.

실행: Spyder에서 F5, 또는 `python inefficient_map_step2.py`
데이터: data/line2_main_240810.csv (사용자가 제공한 서울교통공사 CSV에서 추출)
주의: 표준 역간 소요시간만 합산합니다. 대기·실시간 운행·방향별 차이는 반영하지 않습니다.
"""

import csv
import heapq
from pathlib import Path

# Spyder의 현재 작업 폴더가 달라도 데이터 파일을 찾도록 스크립트 위치를 사용합니다.
DATA_FILE = Path(__file__).resolve().parent / "data" / "line2_main_240810.csv"


def load_graph(csv_path=DATA_FILE):
    """CSV의 역간 구간을 양방향 그래프로 구성합니다.

    그래프 구조: {역이름: [(인접역, 소요초, 거리km), ...]}
    현재 자료는 한 방향의 구간 시간을 제공하므로 역방향에도 같은 값을 적용합니다.
    """
    graph = {}
    connections = set()

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"start_station", "end_station", "travel_seconds", "distance_km"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("2호선 데이터 CSV의 열 이름을 확인해 주세요.")

        for row in reader:
            start = row["start_station"].strip()
            end = row["end_station"].strip()
            seconds = int(row["travel_seconds"])
            distance_km = float(row["distance_km"])
            if not start or not end or start == end or seconds <= 0 or distance_km <= 0:
                raise ValueError(f"잘못된 구간 데이터: {row}")

            key = frozenset((start, end))
            if key in connections:
                raise ValueError(f"중복된 역간 연결: {start} - {end}")
            connections.add(key)

            graph.setdefault(start, []).append((end, seconds, distance_km))
            graph.setdefault(end, []).append((start, seconds, distance_km))

    if len(graph) != 43 or len(connections) != 43 or any(len(v) != 2 for v in graph.values()):
        raise ValueError("2호선 본선의 43개 역/43개 구간 데이터가 올바르지 않습니다.")
    return graph


def shortest_path(graph, start, end):
    """다익스트라 알고리즘으로 소요시간(초)이 가장 짧은 경로를 찾습니다."""
    if start not in graph or end not in graph:
        raise ValueError("입력한 역이 2호선 본선 데이터에 없습니다.")
    if start == end:
        return [start], 0, 0.0

    best_time = {station: float("inf") for station in graph}
    prev = {}  # 역 -> (직전 역, 역간 거리km)
    best_time[start] = 0
    queue = [(0, start)]

    while queue:
        elapsed, station = heapq.heappop(queue)
        if elapsed != best_time[station]:
            continue
        if station == end:
            break

        for next_station, seconds, distance_km in graph[station]:
            new_time = elapsed + seconds
            if new_time < best_time[next_station]:
                best_time[next_station] = new_time
                prev[next_station] = (station, distance_km)
                heapq.heappush(queue, (new_time, next_station))

    if best_time[end] == float("inf"):
        return [], None, None

    path = [end]
    total_distance = 0.0
    while path[-1] != start:
        before, km = prev[path[-1]]
        path.append(before)
        total_distance += km
    path.reverse()
    return path, best_time[end], round(total_distance, 2)


def clean_station_name(value):
    """'합정역'과 '합정'을 동일하게 받아들입니다."""
    name = value.strip()
    return name[:-1] if name.endswith("역") else name


def format_time(seconds):
    """초를 'n분 n초' 형식으로 출력합니다."""
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes}분 {remainder:02d}초"


def main():
    try:
        graph = load_graph()
    except (FileNotFoundError, ValueError, UnicodeError) as error:
        print("데이터를 불러오지 못했습니다:", error)
        print("inefficient_map_step2.py 옆에 data/line2_main_240810.csv가 있는지 확인하세요.")
        return

    print("=== 비효율 지도: 2호선 최단경로 (STEP 2) ===")
    print("서울교통공사 역간 소요시간 데이터 사용 / 순환선 본선 43개 역")
    print("※ 역간 운행시간 기준이며 대기·환승·실시간 정보는 포함하지 않습니다.\n")
    start = clean_station_name(input("출발역 (예: 합정): "))
    end = clean_station_name(input("도착역 (예: 당산): "))

    if start not in graph or end not in graph:
        print("\n지원하지 않는 역 이름입니다. (현재 2호선 본선만 지원)")
        print("지원 역: " + ", ".join(graph))
        return
    if start == end:
        print("\n출발역과 도착역이 같습니다.")
        return

    path, seconds, km = shortest_path(graph, start, end)
    if not path:
        print("이동할 수 있는 경로가 없습니다.")
        return

    print("\n--- 계산 결과 ---")
    print("출발역:", start)
    print("도착역:", end)
    print("최단경로:", " → ".join(path))
    print("이동 구간 수:", len(path) - 1)
    print("표준 역간 소요시간 합계:", format_time(seconds))
    print("구간 거리 합계: {:.1f} km".format(km))
    print("※ 실제 열차 대기시간, 방향별 차이, 운행 지연은 반영되지 않았습니다.")


if __name__ == "__main__":
    main()
