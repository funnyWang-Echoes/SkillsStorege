"""
精简版 CDP 客户端 — 仅用于 get-feed-detail
基于 Angin/Post-to-xhs 上游代码裁剪而来，去掉所有 publish/comment/search/account 相关代码。

用法（CLI）：
    python cdp_publish.py get-feed-detail --feed-id NOTE_ID --xsec-token TOKEN

用法（库）：
    from cdp_publish import XiaohongshuPublisher
    publisher = XiaohongshuPublisher(host="127.0.0.1", port=9222)
    publisher.connect(reuse_existing_tab=True)
    detail = publisher.get_feed_detail(feed_id, xsec_token)
"""
import argparse
import json
import os
import random
import sys
import time
from itertools import count
from typing import Any

import requests
import websockets.sync.client as ws_client

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from feed_explorer import (
    FeedExplorer,
    FeedExplorerError,
    make_feed_detail_url,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222

# Xiaohongshu URLs (only what we need)
XHS_HOME_URL = "https://www.xiaohongshu.com"
FEED_INACCESSIBLE_KEYWORDS = (
    "当前笔记暂时无法浏览",
    "该内容因违规已被删除",
    "该笔记已被删除",
    "内容不存在",
    "笔记不存在",
    "已失效",
    "私密笔记",
    "仅作者可见",
    "因用户设置，你无法查看",
    "因违规无法查看",
)

# Timing
PAGE_LOAD_WAIT = 3
MAX_TIMING_JITTER_RATIO = 0.7
CDP_COMMAND_TIMEOUT = 15.0


class CDPError(Exception):
    pass


def _is_local_host(host: str) -> bool:
    return host.strip().lower() in {"127.0.0.1", "localhost", "::1"}


class XiaohongshuPublisher:
    """精简版 — 只保留 get-feed-detail 需要的 CDP 调用"""

    def __init__(
        self,
        host: str = CDP_HOST,
        port: int = CDP_PORT,
        timing_jitter: float = 0.25,
    ):
        # 第二轮 P0-S1 fix：强制 host 必须是 localhost（防 CDP 流量外泄 + 防 SSRF）。
        # bugfix_log.md 第一轮就把这个列为 P2 待办但没做；现在升级为 P0 必修。
        if not _is_local_host(host):
            raise CDPError(
                f"CDP host must be localhost for security (got {host!r}). "
                f"Pass --host 127.0.0.1 or --host localhost."
            )
        self.host = host
        self.port = port
        self.timing_jitter = max(0.0, min(MAX_TIMING_JITTER_RATIO, float(timing_jitter)))
        self.ws: Any = None
        self.target_id: str | None = None
        # 第五轮 P2 fix：用单调递增计数器替代 time.time() % 100000
        # 避免 1ms 内并发撞 id
        self._msg_id_counter = count(1)

    # ---------- 工具 ----------

    def _sleep(self, base_seconds: float, minimum_seconds: float = 0.05):
        """带随机抖动的 sleep"""
        base = max(minimum_seconds, float(base_seconds))
        if self.timing_jitter <= 0:
            time.sleep(base)
            return
        delta = base * self.timing_jitter
        low = max(minimum_seconds, base - delta)
        high = max(low, base + delta)
        time.sleep(random.uniform(low, high))

    def _send(self, method: str, params: dict | None = None, timeout: float = CDP_COMMAND_TIMEOUT):
        """发送 CDP 命令"""
        if not self.ws:
            raise CDPError("Not connected. Call connect() first.")
        msg_id = next(self._msg_id_counter)
        deadline = time.time() + timeout
        while time.time() < deadline:
            remaining = deadline - time.time()
            raw = self.ws.recv(timeout=max(0.5, min(2.0, remaining)))
            data = json.loads(raw)
            if data.get("id") == msg_id:
                if "error" in data:
                    raise CDPError(f"CDP error: {data['error']}")
                return data.get("result", {})
        raise CDPError(f"CDP timeout for {method}")

    def _evaluate(self, expression: str) -> Any:
        """执行 JS 并返回结果值"""
        result = self._send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        remote_obj = result.get("result", {})
        if remote_obj.get("subtype") == "error":
            raise CDPError(f"JS error: {remote_obj.get('description', remote_obj)}")
        return remote_obj.get("value")

    def _navigate(self, url: str):
        """导航到 URL 并等待加载"""
        self._send("Page.enable")
        self._send("Page.navigate", {"url": url})
        self._sleep(PAGE_LOAD_WAIT, minimum_seconds=1.0)

    # ---------- 连接管理 ----------

    def _get_targets(self) -> list[dict]:
        """拿 CDP targets 列表"""
        url = f"http://{self.host}:{self.port}/json"
        for attempt in range(2):
            try:
                resp = requests.get(
                    url, timeout=5,
                    proxies={"http": None, "https": None} if _is_local_host(self.host) else None,
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == 0:
                    if _is_local_host(self.host):
                        from chrome_launcher import ensure_chrome
                        ensure_chrome(port=self.port)
                    self._sleep(2, minimum_seconds=1.0)
                else:
                    raise CDPError(f"Cannot reach Chrome on {self.host}:{self.port}: {e}")

    def _find_or_create_tab(self, reuse_existing_tab: bool = False) -> str:
        """找到或创建 tab，返回 targetId

        第二轮 P0-B4 fix：之前只看 URL 含 'xiaohongshu.com' 就复用，但用户
        可能同时打开了 explore/search/创作中心等多个 xhs tab —— 复用错的
        tab 会让 _navigate 把用户正在浏览的 tab 强制跳走。
        现在优先匹配「收藏 tab」（URL 含 /user/profile 且 tab=fav），
        其次含 xhs 的任意 tab，最后新建 tab。
        """
        targets = self._get_targets()
        pages = [t for t in targets if t.get("type") == "page"]

        if reuse_existing_tab and pages:
            # 第一优先：收藏 tab
            for t in pages:
                url = t.get("url", "")
                if "xiaohongshu.com" in url and "/user/profile" in url and "tab=fav" in url:
                    self.target_id = t["id"]
                    return self.target_id
            # 第二优先：其他 xhs tab（兜底，避免误用）
            for t in pages:
                url = t.get("url", "")
                if "xiaohongshu.com" in url:
                    self.target_id = t["id"]
                    return self.target_id
            # 没有任何 xhs tab — 不随便用用户的页面，新建一个
            pass

        # 创建新 tab（默认 about:blank，避免影响用户当前页）
        target_id = self._send("Target.createTarget", {"url": "about:blank"}).get("targetId")
        self.target_id = target_id
        return target_id

    def connect(self, reuse_existing_tab: bool = False):
        """连接到一个 tab — 直接用 page target 的 webSocketDebuggerUrl"""
        target_id = self._find_or_create_tab(reuse_existing_tab=reuse_existing_tab)
        # 拿 page target 的 webSocketDebuggerUrl 直接连（无需 attach session）
        targets = self._get_targets()
        ws_url = None
        for t in targets:
            if t.get("id") == target_id:
                ws_url = t.get("webSocketDebuggerUrl")
                break
        if not ws_url:
            raise CDPError(f"No WebSocket URL for target {target_id}")
        self.target_id = target_id
        self.ws = ws_client.connect(ws_url, max_size=50 * 1024 * 1024)

    def disconnect(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None

    # ---------- 主页登录检查 ----------

    def check_home_login(self) -> bool:
        """检查主站登录态（cookie 检测）"""
        if not self.ws:
            raise CDPError("Not connected. Call connect() first.")

        self._send("Page.enable")
        self._send("Page.navigate", {"url": XHS_HOME_URL})
        self._sleep(3, minimum_seconds=1.5)

        current_url = self._evaluate("location.href") or ""
        # 登录后的标志: 主站导航栏不会有"登录"按钮
        has_login_button = self._evaluate("""
            (() => {
                const loginLinks = document.querySelectorAll('a[href*="login"], .login-btn, [class*="login-trigger"]');
                if (loginLinks.length > 0) return true;
                const bodyText = (document.body.innerText || '').slice(0, 3000);
                return bodyText.includes('登录后推荐更懂你的笔记');
            })()
        """)
        if has_login_button:
            return False
        return True

    # ---------- get-feed-detail ----------

    def get_feed_detail(
        self,
        feed_id: str,
        xsec_token: str,
    ) -> dict[str, Any]:
        """获取单条笔记的完整 noteData

        第二轮 P1-A6 fix：去掉 `load_all_comments`/`limit`/`click_more_replies`/
        `reply_limit`/`scroll_speed` 5 个参数和对应的 `_load_feed_detail_comments`
        函数 —— 本 Skill 不抓评论（SKILL.md 明说），这些参数永远没人用。
        """
        if not self.ws:
            raise CDPError("Not connected. Call connect() first.")

        feed_id = feed_id.strip()
        xsec_token = xsec_token.strip()
        if not feed_id:
            raise CDPError("feed_id cannot be empty.")
        if not xsec_token:
            raise CDPError("xsec_token cannot be empty.")

        url = make_feed_detail_url(feed_id, xsec_token)
        self._navigate(url)
        self._sleep(2, minimum_seconds=1.0)

        # 检测笔记是否可访问
        if not self._check_feed_page_accessible():
            raise CDPError(f"Feed {feed_id} is inaccessible.")

        # 从 window.__INITIAL_STATE__ 提取 noteData
        explorer = FeedExplorer(self._evaluate, self._sleep)
        try:
            detail = explorer.get_feed_detail(feed_id=feed_id)
        except FeedExplorerError as e:
            raise CDPError(str(e)) from e

        return {"detail": detail}

    def _check_feed_page_accessible(self) -> bool:
        """DOM 关键字检查：笔记是否被删除/违规/私密"""
        page_text = self._evaluate("(document.body.innerText || '').slice(0, 5000)") or ""
        for kw in FEED_INACCESSIBLE_KEYWORDS:
            if kw in page_text:
                return False
        return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=CDP_HOST)
    parser.add_argument("--port", type=int, default=CDP_PORT)
    parser.add_argument("--reuse-existing-tab", action="store_true")
    parser.add_argument("--account", default=None, help="(保留兼容但不使用)")
    parser.add_argument("--timing-jitter", type=float, default=0.25)

    sub = parser.add_subparsers(dest="command", required=True)

    # get-feed-detail
    p = sub.add_parser("get-feed-detail")
    p.add_argument("--feed-id", required=True)
    p.add_argument("--xsec-token", required=True)

    args = parser.parse_args()

    if args.command != "get-feed-detail":
        print(f"Error: only get-feed-detail is supported in this Skill. Got: {args.command}",
              file=sys.stderr)
        sys.exit(2)

    publisher = XiaohongshuPublisher(
        host=args.host, port=args.port, timing_jitter=args.timing_jitter,
    )
    try:
        publisher.connect(reuse_existing_tab=args.reuse_existing_tab)
        if not publisher.check_home_login():
            print("NOT_LOGGED_IN: 主站未登录，请先在 Chrome 中登录 xiaohongshu.com",
                  file=sys.stderr)
            sys.exit(1)
        result = publisher.get_feed_detail(
            feed_id=args.feed_id,
            xsec_token=args.xsec_token,
        )
        # 输出 JSON 主体：与原 Skill CLI 一致的 {detail: {note: {...}}} 包装
        print(json.dumps({"detail": result["detail"]}, ensure_ascii=False))
    except CDPError as e:
        print(f"CDPError: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(4)
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()