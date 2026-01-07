from services.gh_service import GhService
from models.cmd_result import CmdResult
from utils import errors

def test_create_pr_cmd_failed(monkeypatch, tmp_path):
    def fake_run(cmd, cwd, timeout_sec, max_chars=4000):
        return CmdResult(
            ok=False,
            cmd=" ".join(cmd),
            cwd=cwd,
            code=1,
            elapsed_sec=0.01,
            stdout="",
            stderr="gh auth required",
            stdout_truncated=False,
            stderr_truncated=False,
        )
    monkeypatch.setattr("services.gh_service.run_cmd_blocking", fake_run)

    gh = GhService()
    res = gh.create_pr(
        repo_dir_abs=str(tmp_path),
        title="t",
        body="",
        base="main",
        head="feature",
        draft=False,
        timeout_sec=10,
    )
    assert res.ok is False
    assert res.error.code == errors.CMD_FAILED
    assert "gh auth login" in (res.error.hint or "")

def test_create_pr_success(monkeypatch, tmp_path):
    def fake_run(cmd, cwd, timeout_sec, max_chars=4000):
        return CmdResult(
            ok=True,
            cmd=" ".join(cmd),
            cwd=cwd,
            code=0,
            elapsed_sec=0.01,
            stdout="https://github.com/org/repo/pull/1",
            stderr="",
            stdout_truncated=False,
            stderr_truncated=False,
        )
    monkeypatch.setattr("services.gh_service.run_cmd_blocking", fake_run)

    gh = GhService()
    res = gh.create_pr(str(tmp_path), "t", "", "main", "feature", False, 10)
    assert res.ok is True
    assert "pull/1" in res.data["stdout"]
