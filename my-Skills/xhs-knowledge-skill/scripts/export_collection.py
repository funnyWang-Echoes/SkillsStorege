"""
采集脚本：在用户当前收藏页 tab 上提取笔记元数据
- 不调用 Page.navigate（不污染 tab、不开新页面）
- 纯 DOM 扫描 + xsec_token 提取
- 输出结构化 JSON 到 outputs/

使用：
  1. 用户手动打开 https://www.xiaohongshu.com/user/profile/{uid}?tab=fav&subTab=note
  2. 等笔记渲染出来
  3. python export_collection.py --max 40
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import websockets.sync.client as ws_client

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_fav_tab(targets):
    """定位当前收藏 tab（不导航）"""
    for t in targets:
        if t.get('type') != 'page':
            continue
        url = t.get('url', '')
        if 'xiaohongshu.com/user/profile' in url and 'fav' in url:
            return t
    return None


def js_eval(ws, expr, max_size_mb=50):
    """在已连接的 WebSocket 上跑 JS"""
    mid = int(time.time() * 1000) % 100000
    ws.send(json.dumps({
        'id': mid,
        'method': 'Runtime.evaluate',
        'params': {'expression': expr, 'returnByValue': True, 'awaitPromise': True}
    }))
    while True:
        r = ws.recv(timeout=15)
        d = json.loads(r)
        # 第五轮 P2 fix：跳过 CDP event（Page.frameNavigated / Runtime.consoleAPICalled 等）
        # 这些消息没有 id 字段，原本会被忽略但要 continue 避免误判
        if 'id' not in d:
            continue
        if d.get('id') == mid:
            res = d.get('result', {}).get('result', {})
            if res.get('subtype') == 'error':
                return None, res.get('description', '')
            return res.get('value'), None


EXTRACT_JS = r"""
(() => {
    const cards = document.querySelectorAll('section.note-item');
    const out = [];
    cards.forEach((card) => {
        const noteId = card.getAttribute('data-note-id');
        if (!noteId) return;

        const titleEl = card.querySelector('a.title');
        const title = titleEl ? (titleEl.textContent || '').trim() : '';

        // 链接 href 里带 xsec_token
        const coverLink = card.querySelector('a.cover.mask') || card.querySelector('a.cover');
        const href = coverLink ? coverLink.getAttribute('href') : '';
        let xsecToken = '';
        if (href) {
            const m = href.match(/[?&]xsec_token=([^&]+)/);
            if (m) xsecToken = decodeURIComponent(m[1]);
        }

        // 封面图
        const img = card.querySelector('img');
        const cover = img ? img.getAttribute('src') : '';

        // 作者
        const authorEl = card.querySelector('.author-wrapper a, .author a');
        const author = authorEl ? authorEl.textContent.trim() : '';
        const authorHref = authorEl ? authorEl.getAttribute('href') : '';
        const authorId = authorHref ? (authorHref.match(/profile\/([^?]+)/) || [])[1] : '';

        // 点赞数 / 互动
        const likeEl = card.querySelector('.like-wrapper .count, [class*=like] .count');
        const likeCount = likeEl ? likeEl.textContent.trim() : '';

        out.push({
            noteId,
            xsecToken,
            title,
            author,
            authorId,
            cover,
            likeCount,
            sourceHref: href,
        });
    });
    return out;
})()
"""


SCROLL_JS = r"""
(() => {
    window.scrollBy(0, window.innerHeight * 2);
    return window.scrollY;
})()
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=40, help='最大抓取条数')
    parser.add_argument('--output', default=None, help='输出 JSON 路径')
    parser.add_argument('--scroll-rounds', type=int, default=0,
                        help='额外滚动次数（每次 ~2 屏，每轮间隔 1.5s）')
    args = parser.parse_args()

    # 1) 拿 targets，找 fav tab
    try:
        targets = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=5).read())
    except urllib.error.URLError as e:
        print('[ERR] 连不上 Chrome CDP (127.0.0.1:9222)')
        print(f'      原因：{e.reason if hasattr(e, "reason") else e}')
        print('      请先跑: python scripts/chrome_launcher.py')
        sys.exit(1)
    fav = find_fav_tab(targets)
    if not fav:
        print('[ERR] 没有找到收藏页 tab。请先在 Chrome 里打开：')
        print('      https://www.xiaohongshu.com/user/profile/<your-uid>?tab=fav&subTab=note')
        sys.exit(1)

    print(f'[OK] 锁定 fav tab: {fav["url"][:80]}')

    # 2) 连 WebSocket
    ws = ws_client.connect(fav['webSocketDebuggerUrl'], max_size=args.max * 1024 * 1024)
    try:
        # 3) 可选：额外滚动加载更多笔记
        for i in range(args.scroll_rounds):
            _, err = js_eval(ws, SCROLL_JS)
            if err:
                print(f'[WARN] 滚动失败: {err}')
                break
            time.sleep(1.5)
            print(f'[scroll] round {i + 1}/{args.scroll_rounds}')

        # 4) 一次性提取所有可见卡片
        notes, err = js_eval(ws, EXTRACT_JS)
        if err:
            print(f'[ERR] 提取失败: {err}')
            sys.exit(2)

        # 5) 去重（按 noteId）
        seen = set()
        uniq = []
        for n in notes:
            if n['noteId'] in seen:
                continue
            seen.add(n['noteId'])
            uniq.append(n)
        notes = uniq[:args.max]

        # 6) 拼上 URL 完整路径
        for n in notes:
            n['feedUrl'] = f'https://www.xiaohongshu.com/explore/{n["noteId"]}?xsec_token={n["xsecToken"]}&xsec_source=pc_collect'

        # 7) 输出
        out_path = args.output or os.path.join(
            SCRIPT_DIR, '..', 'outputs', 'list-feeds',
            f'collection_{time.strftime("%Y%m%d_%H%M%S")}.json'
        )
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'extractedAt': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'tabUrl': fav['url'],
                'count': len(notes),
                'notes': notes,
            }, f, ensure_ascii=False, indent=2)

        print(f'[OK] 抓到 {len(notes)} 条 → {out_path}')
        print(f'     前 3 条标题:')
        for n in notes[:3]:
            print(f'       - {n["title"][:40]} (noteId={n["noteId"][:12]}…)')

    finally:
        ws.close()


if __name__ == '__main__':
    main()