#!/usr/bin/env python3
"""Dispatch-roster ACP probe — light real handshake per registry target.

For each agent target this spawns the ACP adapter process, runs
``initialize`` + ``session/new`` (newline-delimited JSON-RPC over stdio,
UTF-8; stderr is agent logs only), and reads ``authMethods`` +
``configOptions`` (``category: "model"`` = the live model list — never
guess models from a static table). A credential probe then classifies the
target into one of three states:

- ``available``     handshake OK and the agent can run headless now
- ``needs_login``   handshake OK but a one-time interactive login is
                    required first (the report carries the exact command)
- ``not_installed`` the process did not spawn or never answered

A fourth bucket ``error`` is used when the process spawned but the
handshake itself failed for a non-auth reason — that is not one of the
three contract states, it means "look at the detail".

Usage:
    python probe_roster.py                 # probe every known target
    python probe_roster.py --target claude # one target only
    python probe_roster.py --prompt-check  # escalate: send a trivial
                                           # session/prompt; a -32000
                                           # auth error or a real
                                           # stopReason settles the state
    python probe_roster.py --registry path/to/acp-agents.json
    python probe_roster.py --json          # machine-readable report

The built-in table mirrors the CLI's bundled ``acp-agents.json``
(packages/cli/src/commands/channel/adapters/). ``--registry`` accepts
that file: either ``{"<id>": {row}}`` or ``[{id, ...row}]`` shapes.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time

IS_WIN = os.name == "nt"

# --- Bundled default registry -------------------------------------------------
# Mirrors the three rows the design (multi-agent orchestration §1) ships in the
# CLI's acp-agents.json. `windows:` overrides command/args and merges env_extra.
# `credProbe` is the cheap pre-login check used for the three-state call:
#   {"type": "file",    "path": "~/.grok/auth.json"}
#   {"type": "command", "cmd": [...], "expectExit": 0}
#   {"type": "command", "cmd": [...], "expectJson": {"loggedIn": true}}
# `resolveEnv` maps an env var to a PATH binary resolved at probe time when the
# var is not already set (CODEX_PATH → codex).
DEFAULT_REGISTRY = {
    "grok-build": {
        # grok.exe runs directly; --always-approve is a `grok agent` PARENT
        # option and must precede the `stdio` subcommand.
        "command": "grok",
        "args": ["agent", "--always-approve", "stdio"],
        "env": {},
        "modelOptionId": "model",
        "effortOptionId": "reasoning_effort",
        "authHint": "grok login",
        "credProbe": {"type": "file", "path": "~/.grok/auth.json"},
    },
    "codex": {
        # npx is a .cmd on Windows → must go through cmd.exe /c.
        "command": "npx",
        "args": ["-y", "@agentclientprotocol/codex-acp"],
        "env": {"INITIAL_AGENT_MODE": "agent-full-access"},
        "windows": {
            "command": "cmd.exe",
            "args": ["/c", "npx", "-y", "@agentclientprotocol/codex-acp"],
        },
        "modelOptionId": "model",
        "effortOptionId": "reasoning_effort",
        "authHint": "codex login  (或 codex login --with-api-key)",
        "credProbe": {
            "type": "command",
            "cmd": ["codex", "login", "status"],
            "expectExit": 0,
        },
        "resolveEnv": {"CODEX_PATH": "codex"},
    },
    "claude": {
        "command": "npx",
        "args": ["-y", "@agentclientprotocol/claude-agent-acp"],
        "env": {},
        "windows": {
            "command": "cmd.exe",
            "args": ["/c", "npx", "-y", "@agentclientprotocol/claude-agent-acp"],
        },
        "modelOptionId": "model",
        "effortOptionId": "effort",
        "authHint": "claude auth login --claudeai  (或 --console)",
        "credProbe": {
            "type": "command",
            "cmd": ["claude", "auth", "status"],
            "expectJson": {"loggedIn": True},
        },
    },
}

INIT_PARAMS = {
    "protocolVersion": 1,
    "clientCapabilities": {
        "fs": {"readTextFile": False, "writeTextFile": False},
        "terminal": False,
        "auth": {"terminal": True},
    },
    "clientInfo": {"name": "dispatch-roster-probe", "version": "1.0.0"},
}

PROMPT_CHECK_TEXT = "Reply with exactly one word: ok"


# --- Minimal NDJSON JSON-RPC stdio client ------------------------------------
class AcpProbe:
    """initialize + session/new (+ optional session/prompt) over stdio.

    Agent→Client blocking methods: session/request_permission is answered
    with the first allow* option; anything else gets -32601 so a private
    blocking call can never hang the probe.
    """

    def __init__(self, cmd: list[str], env: dict | None = None, cwd: str | None = None):
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
            bufsize=0,
        )
        self._next_id = 1
        self._pending: dict[int, queue.Queue] = {}
        self._stderr: queue.Queue = queue.Queue()
        self._alive = True
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stderr(self):
        try:
            for line in iter(self.proc.stderr.readline, b""):
                self._stderr.put(line.decode("utf-8", "replace").rstrip())
        except Exception:
            pass
        finally:
            self._stderr.put(None)

    def _read_stdout(self):
        try:
            for raw in iter(self.proc.stdout.readline, b""):
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._dispatch(msg)
        except Exception:
            pass
        finally:
            self._alive = False
            for q in self._pending.values():
                q.put({"_dead": True})

    def _dispatch(self, msg: dict):
        if "id" in msg and ("result" in msg or "error" in msg):
            q = self._pending.get(msg["id"])
            if q is not None:
                q.put(msg)
            return
        if "method" in msg and "id" in msg:
            self._handle_agent_request(msg)

    def _handle_agent_request(self, msg: dict):
        if msg.get("method") == "session/request_permission":
            opts = msg.get("params", {}).get("options", [])
            pick = next(
                (o for o in opts if "allow" in str(o.get("kind", ""))),
                opts[0] if opts else None,
            )
            self._send(
                {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "result": {
                        "outcome": {
                            "outcome": "selected",
                            "optionId": pick["optionId"] if pick else "",
                        }
                    },
                }
            )
        else:
            self._send(
                {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {msg.get('method')}",
                    },
                }
            )

    def _send(self, obj: dict):
        try:
            self.proc.stdin.write(json.dumps(obj).encode("utf-8") + b"\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def request(self, method: str, params: dict | None = None, timeout: float = 30.0):
        rid = self._next_id
        self._next_id += 1
        q: queue.Queue = queue.Queue()
        self._pending[rid] = q
        self._send({"jsonrpc": "2.0", "id": rid, "method": method,
                    **({"params": params} if params is not None else {})})
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return {"_timeout": True, "method": method}
        finally:
            self._pending.pop(rid, None)

    def stderr_tail(self, n: int = 8) -> list[str]:
        lines = []
        while True:
            try:
                s = self._stderr.get_nowait()
            except queue.Empty:
                break
            if s is not None:
                lines.append(s)
        return lines[-n:]

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass


# --- Helpers ------------------------------------------------------------------
def _resolve_cmd(cmd: list[str]) -> list[str]:
    """Resolve the executable; on Windows a .cmd/.bat needs cmd.exe /c."""
    exe = shutil.which(cmd[0])
    if exe is None:
        return cmd  # let Popen raise; caller reports not_installed
    resolved = [exe] + cmd[1:]
    if IS_WIN and exe.lower().endswith((".cmd", ".bat")):
        resolved = ["cmd.exe", "/c"] + resolved
    return resolved


def _cred_probe(spec: dict) -> bool | None:
    """Run the row's credential probe. True=creds present, False=missing,
    None=no probe defined (caller decides)."""
    cp = spec.get("credProbe")
    if not cp:
        return None
    if cp.get("type") == "file":
        return os.path.isfile(os.path.expanduser(cp["path"]))
    if cp.get("type") == "command":
        cmd = _resolve_cmd(list(cp["cmd"]))
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=20, text=True,
                               encoding="utf-8", errors="replace")
        except (OSError, subprocess.TimeoutExpired):
            return False
        if "expectJson" in cp:
            try:
                data = json.loads(r.stdout)
            except (json.JSONDecodeError, TypeError):
                return False
            return all(data.get(k) == v for k, v in cp["expectJson"].items())
        return r.returncode == cp.get("expectExit", 0)
    return None


def _models(session_result: dict, spec: dict) -> dict:
    """Extract the live model/effort lists from configOptions."""
    options = session_result.get("configOptions") or []
    model_id = spec.get("modelOptionId", "model")
    effort_id = spec.get("effortOptionId")
    out = {"models": [], "current_model": None, "efforts": [],
           "current_effort": None, "model_option_id": model_id,
           "effort_option_id": effort_id}
    for opt in options:
        vals = [o.get("value", o.get("name")) for o in opt.get("options", [])
                if isinstance(o, dict)]
        if opt.get("category") == "model" or opt.get("id") == model_id:
            out["models"] = vals
            out["current_model"] = opt.get("currentValue")
        elif effort_id and opt.get("id") == effort_id:
            out["efforts"] = vals
            out["current_effort"] = opt.get("currentValue")
    return out


def _auth_methods(init_result: dict) -> list[dict]:
    raw = init_result.get("authMethods") or []
    return [
        {
            "id": m.get("id"),
            "name": m.get("name"),
            "type": m.get("type"),
            "args": m.get("args"),
            "description": m.get("description"),
        }
        for m in raw
        if isinstance(m, dict)
    ]


def _is_auth_error(resp: dict) -> bool:
    err = resp.get("error") or {}
    msg = str(err.get("message", "")).lower()
    return err.get("code") == -32000 or "auth" in msg or "login" in msg


def _build_launch(row: dict) -> tuple[list[str], dict]:
    """Merge a registry row into (cmd argv, env dict) for this platform."""
    command = row.get("command", "")
    args = list(row.get("args") or [])
    env = dict(row.get("env") or {})
    win = row.get("windows") or {}
    if IS_WIN and win:
        command = win.get("command", command)
        args = list(win.get("args", args))
        env.update(win.get("env") or {})
        env.update(win.get("env_extra") or {})
    merged_env = dict(os.environ)
    merged_env.update(env)
    for var, binary in (row.get("resolveEnv") or {}).items():
        if var not in env:
            found = shutil.which(binary)
            if found:
                merged_env[var] = found
    return _resolve_cmd([command] + args), merged_env


def probe_target(tid: str, row: dict, prompt_check: bool,
                 handshake_timeout: float) -> dict:
    rep: dict = {"target": tid, "state": None, "detail": "",
                 "models": [], "current_model": None, "efforts": [],
                 "current_effort": None, "authMethods": [],
                 "login": row.get("authHint"), "cmd": None}

    cmd, env = _build_launch(row)
    rep["cmd"] = " ".join(cmd)
    if shutil.which(cmd[0]) is None:
        rep["state"] = "not_installed"
        rep["detail"] = f"executable not found on PATH: {cmd[0]}"
        return rep

    cwd = tempfile.mkdtemp(prefix=f"rosterprobe-{tid}-")
    try:
        proc = AcpProbe(cmd, env=env, cwd=cwd)
    except OSError as exc:
        rep["state"] = "not_installed"
        rep["detail"] = f"spawn failed: {exc}"
        return rep

    try:
        init = proc.request("initialize", INIT_PARAMS, timeout=handshake_timeout)
        if init.get("_timeout") or init.get("_dead") or "error" in init:
            rep["state"] = "error"
            rep["detail"] = (
                "initialize failed: "
                + json.dumps(init.get("error", init), ensure_ascii=False)[:200]
            )
            rep["stderr_tail"] = proc.stderr_tail()
            return rep
        init_res = init.get("result") or {}
        rep["authMethods"] = _auth_methods(init_res)
        rep["protocolVersion"] = init_res.get("protocolVersion")

        sess = proc.request("session/new", {"cwd": cwd, "mcpServers": []},
                            timeout=handshake_timeout)
        if sess.get("_timeout") or sess.get("_dead"):
            rep["state"] = "error"
            rep["detail"] = "session/new timed out or transport died"
            rep["stderr_tail"] = proc.stderr_tail()
            return rep
        if "error" in sess:
            rep["state"] = "needs_login" if _is_auth_error(sess) else "error"
            rep["detail"] = json.dumps(sess["error"], ensure_ascii=False)[:300]
            return rep
        sess_res = sess.get("result") or {}
        rep["sessionId"] = sess_res.get("sessionId")
        rep.update(_models(sess_res, row))

        creds = _cred_probe(row)
        if creds is True:
            rep["state"] = "available"
            rep["detail"] = "handshake ok; cached credentials present"
        elif creds is False:
            rep["state"] = "needs_login"
            rep["detail"] = (
                "handshake ok; credential probe failed — "
                f"run: {row.get('authHint', 'see authMethods')}"
            )
        else:
            # No credProbe defined: authMethods is the only signal.
            if not rep["authMethods"]:
                rep["state"] = "available"
                rep["detail"] = "handshake ok; agent advertises no authMethods"
            else:
                rep["state"] = "unknown"
                rep["detail"] = (
                    "handshake ok but auth state is uncertain — "
                    "re-run with --prompt-check or log in manually"
                )

        if prompt_check and rep["state"] in ("needs_login", "unknown", "available"):
            check = proc.request(
                "session/prompt",
                {
                    "sessionId": rep["sessionId"],
                    "prompt": [{"type": "text", "text": PROMPT_CHECK_TEXT}],
                },
                timeout=90,
            )
            if _is_auth_error(check):
                rep["state"] = "needs_login"
                rep["detail"] = (
                    "session/prompt → "
                    + json.dumps(check.get("error"), ensure_ascii=False)[:200]
                    + f" — run: {row.get('authHint', 'see authMethods')}"
                )
            elif (check.get("result") or {}).get("stopReason"):
                rep["state"] = "available"
                rep["detail"] = (
                    "session/prompt completed "
                    f"(stopReason={check['result']['stopReason']})"
                )
            elif check.get("_timeout") or check.get("_dead"):
                rep["detail"] += " | prompt-check inconclusive (timeout)"
        return rep
    finally:
        proc.close()
        try:
            shutil.rmtree(cwd, ignore_errors=True)
        except Exception:
            pass


def load_registry(path: str | None) -> dict:
    if not path:
        return dict(DEFAULT_REGISTRY)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        rows = data.get("agents", data)
        return {k: v for k, v in rows.items() if isinstance(v, dict)}
    if isinstance(data, list):
        return {r["id"]: r for r in data if isinstance(r, dict) and r.get("id")}
    raise SystemExit(f"unrecognized registry shape in {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", help="probe one registry id only")
    ap.add_argument("--registry", help="path to the CLI's acp-agents.json")
    ap.add_argument("--prompt-check", action="store_true",
                    help="escalate with a trivial session/prompt to settle "
                         "auth state (slower, definitive)")
    ap.add_argument("--timeout", type=float, default=30.0,
                    help="per-request handshake timeout seconds (default 30; "
                         "first npx run may need the package fetched)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    registry = load_registry(args.registry)
    targets = [args.target] if args.target else list(registry)
    reports = []
    for tid in targets:
        row = registry.get(tid)
        if row is None:
            reports.append({"target": tid, "state": "not_installed",
                            "detail": "no registry row", "models": []})
            continue
        reports.append(probe_target(tid, row, args.prompt_check, args.timeout))

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return

    icon = {"available": "[ok] 可用 available", "needs_login": "[!] 需预登录 needs-login",
            "not_installed": "[x] 未安装 not-installed", "unknown": "[?] 待确认 unknown",
            "error": "[!] 握手失败 error"}
    for r in reports:
        print(f"[{icon.get(r['state'], r['state'])}] {r['target']}")
        print(f"    cmd:    {r.get('cmd')}")
        print(f"    detail: {r.get('detail')}")
        if r.get("models"):
            print(f"    models: {', '.join(str(m) for m in r['models'])}"
                  f"  (current: {r.get('current_model')})")
        if r.get("efforts"):
            print(f"    effort: {', '.join(str(e) for e in r['efforts'])}"
                  f"  (current: {r.get('current_effort')})")
        if r["state"] == "needs_login" and r.get("login"):
            print(f"    login:  {r['login']}")
        if r.get("authMethods"):
            kinds = ", ".join(
                f"{m.get('id')}({m.get('type') or 'agent'})"
                for m in r["authMethods"]
            )
            print(f"    authMethods: {kinds}")
        print()


if __name__ == "__main__":
    sys.exit(main())
