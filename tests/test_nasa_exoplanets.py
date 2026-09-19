import unittest

from longhorizon.nasa_exoplanets import NasaExoplanetClient


class NasaExoplanetTests(unittest.TestCase):
    def test_snapshot_contract_and_cache(self):
        responses = iter([
            [{"planet_count": 3}],
            [{"discoverymethod": "Transit", "planet_count": 2}],
            [{"disc_year": 2024, "planet_count": 1}],
            [{"pl_name": "Example b", "hostname": "Example", "disc_year": 2024, "discoverymethod": "Transit", "pl_orbper": 2.0, "pl_rade": 1.0, "sy_dist": 10.0}],
        ])
        client = NasaExoplanetClient()
        client._fetch = lambda _: next(responses)  # type: ignore[method-assign]
        first, second = client.snapshot(), client.snapshot()
        self.assertEqual(first["cache"], "miss")
        self.assertEqual(second["cache"], "hit")
        self.assertEqual(first["summary"]["confirmed_planets"], 3)


if __name__ == "__main__":
    unittest.main()
