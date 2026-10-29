"""STEP 3: 기본 unittest, STEP 2와 연동한 풍경 점수 검증."""
import unittest
from inefficient_map_step2 import load_graph, shortest_path
from inefficient_map_step3 import load_scenery, score_path, section_score, edge_key

class TestStep3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph=load_graph()
        cls.scenery=load_scenery(cls.graph)

    def test_complete_edge_metadata(self):
        self.assertEqual(len(self.scenery), 43)
        self.assertEqual(sum(x["ground_status"]=="surface" for x in self.scenery.values()), 10)
        self.assertEqual(sum(x["ground_status"]=="transition" for x in self.scenery.values()), 4)
        self.assertEqual(sum(x["han_river_crossing"] for x in self.scenery.values()), 2)

    def test_bridge_hapjeong_dangsan(self):
        section=self.scenery[edge_key("합정","당산")]
        self.assertEqual(section_score(section), 10)
        path,seconds,km=shortest_path(self.graph,"합정","당산")
        self.assertEqual((path,seconds),(["합정","당산"],150))
        self.assertEqual(score_path(path,self.scenery)[:4],(10,1,1,0))

    def test_bridge_jamsil(self):
        section=self.scenery[edge_key("강변","잠실나루")]
        self.assertEqual(section_score(section), 10)

    def test_east_side(self):
        path,seconds,km=shortest_path(self.graph,"건대입구","잠실")
        points, n_surface, n_river, n_unc, highlights=score_path(path,self.scenery)
        self.assertEqual(path,["건대입구","구의","강변","잠실나루","잠실"])
        self.assertEqual((points,n_surface,n_river,n_unc),(14,3,1,1))

    def test_unclassified_not_underground(self):
        part=self.scenery[edge_key("강남","역삼")]
        self.assertEqual(part["ground_status"],"unclassified")
        self.assertEqual(section_score(part),0)

    def test_invalid_edge_rejected(self):
        with self.assertRaises(ValueError):
            score_path(["합정","강남"],self.scenery)

if __name__ == "__main__":
    unittest.main()
