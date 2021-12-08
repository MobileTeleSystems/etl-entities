from hwmlib.process import Process, ProcessStackManager


def test_process_stack_manager():
    with Process(name="some1", host="abc") as process1:
        with Process(name="some2", host="cde") as process2:
            assert ProcessStackManager.get_current() == process2
            assert ProcessStackManager.get_current_level() == 2

        assert ProcessStackManager.get_current() == process1
        assert ProcessStackManager.get_current_level() == 1

    assert ProcessStackManager.get_current() == Process()
    assert ProcessStackManager.get_current_level() == 0
