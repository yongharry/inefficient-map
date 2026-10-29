"""Python 기본 unittest로 STEP 2의 데이터·경로 계산을 확인합니다."""

import unittest
from inefficient_map_step2 import load_graph, shortest_path, format_time


class TestLine2ShortestPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()

    def test_main_loop_has_43_stations_and_connections(self):
        self.assertEqual(len(self.graph), 43)
        self.assertEqual(sum(len(edges) for edges in self.graph.values()) // 2, 43)
        self.assertTrue(all(len(edges) == 2 for edges in self.graph.values()))

    def test_hapjeong_to_dangsan(self):
        path, seconds, km = shortest_path(self.graph, "합정", "당산")
        self.assertEqual(path, ["합정", "당산"])
        self.assertEqual(seconds, 150)  # 원본 CSV: 당산 -> 합정 02:30
        self.assertEqual(km, 2.0)

    def test_loop_closes_from_chungjeongno_to_cityhall(self):
        path, seconds, km = shortest_path(self.graph, "충정로", "시청")
        self.assertEqual(path, ["충정로", "시청"])
        self.assertEqual(seconds, 90)
        self.assertEqual(km, 1.1)

    def test_same_station(self):
        self.assertEqual(shortest_path(self.graph, "합정", "합정"), (["합정"], 0, 0.0))

    def test_time_format(self):
        self.assertEqual(format_time(150), "2분 30초")


if __name__ == "__main__":
    unittest.main()
