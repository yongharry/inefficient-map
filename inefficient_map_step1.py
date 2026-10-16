"""비효율 지도 / STEP 1: 서울 지하철 2호선 순환선 최단경로 연습.

실제 2호선 본선 역 순서를 사용하되, 역간 운행시간은 모두 2분으로
가정한 학습용 코드입니다. 실제 경로 안내·운행시간으로 사용하지 마세요.
지선(성수지선, 신정지선), 환승, 대기시간은 포함하지 않습니다.
"""

import heapq

# 2호선 순환선 43개 역, 시청부터 내선 방향 순서
STATIONS = [
    '시청', '을지로입구', '을지로3가', '을지로4가',
    '동대문역사문화공원', '신당', '상왕십리', '왕십리',
    '한양대', '뚝섬', '성수', '건대입구', '구의',
    '강변', '잠실나루', '잠실', '잠실새내', '종합운동장',
    '삼성', '선릉', '역삼', '강남', '교대', '서초',
    '방배', '사당', '낙성대', '서울대입구', '봉천',
    '신림', '신대방', '구로디지털단지', '대림',
    '신도림', '문래', '영등포구청', '당산', '합정',
    '홍대입구', '신촌', '이대', '아현', '충정로'
]

# 실제 운행시간이 아닙니다. 이후 서울교통공사 공식 역간 시간으로 교체 예정.
SAMPLE_TIME_MIN = 2.0


def make_graph(stations):
    """역을 점(node), 역 사이를 양방향 연결(edge)로 표현합니다."""
    graph = {station: [] for station in stations}
    for i in range(len(stations)):
        current_station = stations[i]
        next_station = stations[(i + 1) % len(stations)]  # 마지막 역 -> 시청
        graph[current_station].append((next_station, SAMPLE_TIME_MIN))
        graph[next_station].append((current_station, SAMPLE_TIME_MIN))
    return graph


def shortest_path(graph, start, end):
    """다익스트라 알고리즘으로 최단시간 경로를 구합니다."""
    distances = {station: float('inf') for station in graph}
    previous = {}
    distances[start] = 0.0
    queue = [(0.0, start)]

    while queue:
        current_time, current = heapq.heappop(queue)
        if current_time > distances[current]:
            continue
        if current == end:
            break

        for neighbor, minutes in graph[current]:
            new_time = current_time + minutes
            if new_time < distances[neighbor]:
                distances[neighbor] = new_time
                previous[neighbor] = current
                heapq.heappush(queue, (new_time, neighbor))

    if distances[end] == float('inf'):
        return [], float('inf')

    path = [end]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    return path, distances[end]


def clean_station_name(name):
    """'잠실역'도 '잠실'로 인식합니다."""
    name = name.strip()
    return name[:-1] if name.endswith('역') else name


def main():
    graph = make_graph(STATIONS)
    print('=== 비효율 지도: 2호선 최단경로 (STEP 1) ===')
    print('2호선 본선 43개 역 / 지선 제외')
    print('주의: 역간 2분을 가정한 학습용 시간입니다.\n')

    start = clean_station_name(input('출발역 (예: 합정): '))
    end = clean_station_name(input('도착역 (예: 잠실): '))

    if start not in graph or end not in graph:
        print('\n역 이름을 확인해 주세요. 본선 43개 역만 지원합니다.')
        print('지원 역: ' + ', '.join(STATIONS))
        return
    if start == end:
        print('출발역과 도착역이 같습니다.')
        return

    path, minutes = shortest_path(graph, start, end)
    print('\n--- 계산 결과 ---')
    print('출발역:', start)
    print('도착역:', end)
    print('최단경로:', ' → '.join(path))
    print('이동 구간 수:', len(path) - 1)
    print('테스트용 추정시간: {:.0f}분'.format(minutes))
    print('※ 실제 배차·정차·대기시간이 반영되지 않았습니다.')


if __name__ == '__main__':
    main()
