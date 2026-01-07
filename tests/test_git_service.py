from services.git_service import GitService
from models.cmd_result import CmdResult
from utils import errors

def _ok_cmd(cmd, cwd, timeout_sec, max_chars=4000):
    return CmdResult(
        ok=True,
        cmd=" ".join(cmd),
        cwd=cwd,
        code=0,
        elapsed_sec=0.01,
        stdout="OK",
        stderr="",
        stdout_truncated=False,
        stderr_truncated=False,
        error=None,
    )

def _fail_cmd(cmd, cwd, timeout_sec, max_chars=4000):
    return CmdResult(
        ok=False,
        cmd=" ".join(cmd),
        cwd=cwd,
        code=1,
        elapsed_sec=0.01,
        stdout="",
        stderr="boom",
        stdout_truncated=False,
        stderr_truncated=False,
        error=None,
    )

def test_status_not_a_repo(monkeypatch, tmp_path):
    # validate_repo_dir returns (False, path)
    monkeypatch.setattr("services.git_service.validate_repo_dir", lambda p: (False, str(tmp_path)))
    gs = GitService()
    res = gs.status(str(tmp_path), 10)
    assert res.ok is False
    assert res.error.code == errors.NOT_A_GIT_REPO

def test_status_cmd_failed(monkeypatch, tmp_path):
    monkeypatch.setattr("services.git_service.validate_repo_dir", lambda p: (True, str(tmp_path)))
    monkeypatch.setattr("services.git_service.run_cmd_blocking", _fail_cmd)

    gs = GitService()
    res = gs.status(str(tmp_path), 10)

    assert res.ok is False
    assert res.error.code == errors.CMD_FAILED
    assert isinstance(res.error.details, dict)
    assert "stderr" in res.error.details

def test_diff_success(monkeypatch, tmp_path):
    monkeypatch.setattr("services.git_service.validate_repo_dir", lambda p: (True, str(tmp_path)))
    monkeypatch.setattr("services.git_service.run_cmd_blocking", lambda cmd, cwd, timeout_sec, max_chars=4000: CmdResult(
        ok=True, cmd=" ".join(cmd), cwd=cwd, code=0, elapsed_sec=0.01,
        stdout="diff --git a/x b/x", stderr="", stdout_truncated=False, stderr_truncated=False
    ))

    gs = GitService()
    res = gs.diff(str(tmp_path), staged=False, name_only=False, stat=False, max_chars=20000, timeout_sec=10)
    assert res.ok is True
    assert "diff --git" in res.data["diff"]
