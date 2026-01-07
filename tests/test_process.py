from utils.process import run_cmd_blocking

def test_run_cmd_blocking_success():
    res = run_cmd_blocking(["python", "-c", "print('hi')"], cwd=None, timeout_sec=5)
    assert res.ok is True
    assert "hi" in (res.stdout or "")

def test_run_cmd_blocking_timeout():
    res = run_cmd_blocking(["python", "-c", "import time; time.sleep(2)"], cwd=None, timeout_sec=0.1)
    assert res.ok is False
    assert res.error == "timeout"
    assert "timed out" in (res.stderr or "").lower()
