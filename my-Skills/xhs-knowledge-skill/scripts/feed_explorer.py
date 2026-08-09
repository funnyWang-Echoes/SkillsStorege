"""
精简版 FeedExplorer — 仅保留 noteData 提取
基于 Angin/Post-to-xhs 上游代码裁剪而来，去掉所有 search/filter/navigation 逻辑。
"""
from __future__ import annotations

import json
import time
from typing import Any, Callable


FEED_DETAIL_URL_TEMPLATE = (
    "https://www.xiaohongshu.com/explore/{feed_id}"
    "?xsec_token={xsec_token}&xsec_source=pc_feed"
)


class FeedExplorerError(Exception):
    pass


def make_feed_detail_url(feed_id: str, xsec_token: str) -> str:
    feed_id = feed_id.strip()
    xsec_token = xsec_token.strip()
    if not feed_id:
        raise FeedExplorerError("feed_id cannot be empty.")
    if not xsec_token:
        raise FeedExplorerError("xsec_token cannot be empty.")
    return FEED_DETAIL_URL_TEMPLATE.format(feed_id=feed_id, xsec_token=xsec_token)


class FeedExplorer:
    """Reusable extractor for note detail pages."""

    def __init__(
        self,
        evaluate: Callable[[str], Any],
        sleep: Callable[..., None],
    ):
        self._evaluate = evaluate
        self._sleep = sleep

    def _wait_for_detail_state(self, timeout_seconds: float = 25.0, poll_seconds: float = 0.5) -> bool:
        """等 window.__INITIAL_STATE__.note.noteDetailMap 出现"""
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            try:
                ok = self._evaluate("""
                    (() => {
                        const state = window.__INITIAL_STATE__;
                        return !!(state && state.note && state.note.noteDetailMap);
                    })()
                """)
                if ok:
                    return True
            except Exception:
                pass
            self._sleep(poll_seconds, minimum_seconds=min(0.2, poll_seconds))
        return False

    def _extract_feed_detail(self, feed_id: str) -> dict[str, Any]:
        """从 noteDetailMap 拿一条笔记详情

        第二轮 P0-A7 fix：第一轮 P1-4 假修复。
        原 P1-4 写法 `keys.length === 1 && keys[0] === feedId` 在 keys.length===1 时
        `keys[0]` 就是唯一那个 key，所以 `keys[0] === feedId` 永远成立 —— 退化成
        「detailMap 有任意一条就 fallback」，没真正防住 SPA 误抓。

        现在：只在「目标 key 缺失、detailMap 恰好只有 1 个 key」时 fallback；
        detailMap 有 2+ key 时不主动猜，触发 FeedExplorerError 提示用户关其他 tab。
        """
        feed_literal = json.dumps(feed_id)
        raw = self._evaluate(f"""
            (() => {{
                const feedId = {feed_literal};
                const state = window.__INITIAL_STATE__;
                if (!state || !state.note || !state.note.noteDetailMap) {{
                    return "";
                }}

                const detailMap = state.note.noteDetailMap;
                if (detailMap[feedId]) {{
                    return JSON.stringify(detailMap[feedId]);
                }}

                // 第二轮 P0-A7 fix：只在「目标 key 缺失、detailMap 恰好只有 1 个 key」时 fallback
                const keys = Object.keys(detailMap || {{}});
                if (keys.length === 1 && detailMap[keys[0]]) {{
                    return JSON.stringify(detailMap[keys[0]]);
                }}
                return "";
            }})()
        """)

        if not raw:
            raise FeedExplorerError(
                f"Could not find feed detail for id '{feed_id}' in noteDetailMap."
            )

        if not isinstance(raw, str):
            raise FeedExplorerError("Feed detail payload is not a JSON string.")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FeedExplorerError(f"Failed to parse feed detail JSON: {exc}") from exc

        if not isinstance(parsed, dict):
            raise FeedExplorerError("Feed detail payload is not an object.")
        return parsed

    def get_feed_detail(self, feed_id: str) -> dict[str, Any]:
        """获取一条笔记的完整 noteData"""
        feed_id = feed_id.strip()
        if not feed_id:
            raise FeedExplorerError("feed_id cannot be empty.")
        if not self._wait_for_detail_state():
            raise FeedExplorerError(
                "Timed out waiting for feed detail in window.__INITIAL_STATE__."
            )
        return self._extract_feed_detail(feed_id)