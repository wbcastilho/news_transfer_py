import unittest
from src.utils.StopWatch import StopWatch


class TestStopWatch(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        self.stop_watch = StopWatch()

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_time_convert_quando_param_igual_60_return_1(self):
        self.assertEqual(self.stop_watch._time_convert(60), 1)

    def test_check_quando_minelapsed_for_menor_que_timeout_retorna_true(self):
        self.assertTrue(self.stop_watch.check(1))

    def test_check_quando_minelapsed_for_maior_que_timeout_retorna_false(self):
        self.assertFalse(self.stop_watch.check(0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
