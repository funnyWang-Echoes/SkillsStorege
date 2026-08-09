"""
详情抓取脚本：调用 Skill 自带的 get-feed-detail，
针对三种内容类型（纯文本 / 图文 / 视频）做规范化输出。

设计要点：
- 不开新 tab（用 --reuse-existing-tab）
- 不调用 Page.navigate（避免开新页面）
- 调用 Skill 原生命令拿 raw noteData
- 在 Python 层规范化三种内容类型
- 输出去重、扁平、可入数据库的 JSON
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_json_from_mixed_output(raw: str):
    """从 Skill 命令输出中提取 JSON（Skill 会把 [cdp_publish] 日志打到 stdout）

    第五轮 P2 fix：失败时返回 dict with reason：
    - {"error": "EMPTY"}: stdout 为空
    - {"error": "NO_BRACE"}: 没有 { 或 }
    - {"error": "PARSE_FAIL", "preview": "..."}: brace 匹配后仍解析失败
    - 成功：返回 parsed dict
    """
    if not raw or not raw.strip():
        return {"error": "EMPTY"}
    i = raw.find('{')
    j = raw.rfind('}')
    if i < 0 or j < 0:
        return {"error": "NO_BRACE", "preview": raw[:120]}
    try:
        return json.loads(raw[i:j+1])
    except json.JSONDecodeError:
        depth = 0
        start = i
        end = -1
        for k in range(i, len(raw)):
            if raw[k] == '{':
                depth += 1
            elif raw[k] == '}':
                depth -= 1
                if depth == 0:
                    end = k
                    break
        if end > 0:
            try:
                return json.loads(raw[start:end+1])
            except json.JSONDecodeError as e:
                return {"error": "PARSE_FAIL", "msg": str(e)[:120], "preview": raw[start:start + 120]}
        return {"error": "PARSE_FAIL", "preview": raw[i:i + 120]}


def run_get_feed_detail(note_id: str, xsec_token: str, reuse_tab: bool = True) -> dict | None:
    """调用 Skill 子命令拿一条笔记的完整 noteData"""
    cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'cdp_publish.py'),
    ]
    if reuse_tab:
        cmd.append('--reuse-existing-tab')
    cmd += ['get-feed-detail', '--feed-id', note_id, '--xsec-token', xsec_token]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        parsed = parse_json_from_mixed_output(result.stdout)
        # 第五轮 P2 fix：失败时打印分类信息
        if isinstance(parsed, dict) and "error" in parsed:
            print(f'  [FAIL] {note_id[:12]}…: {parsed["error"]} {parsed.get("msg", "")[:60]}')
            return None
        return parsed
    except subprocess.TimeoutExpired:
        print(f'  [TIMEOUT] {note_id[:12]}…')
        return None
    except Exception as e:
        print(f'  [ERROR] {note_id[:12]}…: {type(e).__name__}: {e}'[:100])
        return None


def classify_note(note: dict) -> str:
    """判断笔记类型"""
    if note.get('type') == 'video' and note.get('video'):
        return 'video'
    if note.get('imageList') and len(note['imageList']) > 0:
        return 'image_text'  # 含图（可能也含文字）
    if note.get('desc') or note.get('title'):
        return 'text_only'
    return 'unknown'


def extract_images(note: dict) -> list[dict]:
    """规范化图片列表 — 处理 url/urlDefault/urlPre 三种字段"""
    imgs = []
    for img in note.get('imageList') or []:
        if not isinstance(img, dict):
            continue
        # urlDefault 通常是 CDN 默认尺寸; urlPre 是无水印原图前缀; url 是带水印
        imgs.append({
            'fileId': img.get('fileId'),
            'width': img.get('width'),
            'height': img.get('height'),
            'urlWatermarked': img.get('url'),  # 带小红书水印
            'urlClean': img.get('urlDefault'),  # 通常无水印
            'urlPrefix': img.get('urlPre'),     # 用于拼多尺寸
            'isLivePhoto': bool(img.get('livePhoto')),
        })
    return imgs


def extract_video(note: dict) -> dict | None:
    """规范化视频字段 — 选最高清的 stream"""
    video = note.get('video')
    if not video:
        return None

    media = video.get('media', {})
    stream = media.get('stream', {})

    # 优先级：EF7 > EF6 > EF5 > EF4 (清晰度降序)
    candidates = []
    for quality in ['EF7', 'EF6', 'EF5', 'EF4']:
        for s in stream.get(quality, []):
            candidates.append((quality, s))

    chosen = None
    if candidates:
        # 选 highest quality, defaultStream 优先
        chosen = candidates[0]
        for q, s in candidates:
            if s.get('defaultStream') == 1:
                chosen = (q, s)
                break

    return {
        'videoId': media.get('videoId'),
        # 第二轮 P1-A3 fix（与 boundary 子代理发现 P1-3 同源）：
        # 去掉 `if False else` 死分支。
        'duration': (chosen[1].get('duration') / 1000) if chosen else None,
        'coverUrl': (video.get('image') or {}).get('urlDefault') if isinstance(video.get('image'), dict) else None,
        'bestQuality': chosen[0] if chosen else None,
        'width': chosen[1].get('width') if chosen else None,
        'height': chosen[1].get('height') if chosen else None,
        'bitrate': chosen[1].get('avgBitrate') if chosen else None,
        'size': chosen[1].get('size') if chosen else None,
        'masterUrl': chosen[1].get('masterUrl') if chosen else None,
        'backupUrls': chosen[1].get('backupUrls') if chosen else [],
        'format': chosen[1].get('format') if chosen else None,
    }


def extract_tags(note: dict) -> list[str]:
    """提取话题标签

    第二轮 P1-B9 fix：小红书不同版本 API 字段名不一致（name / tagName / tag_name），
    之前只取 tag.get('name')，遇到 tagName 字段就 0 tag。
    """
    tags = []
    for tag in note.get('tagList') or []:
        if isinstance(tag, dict):
            name = (
                tag.get('name')
                or tag.get('tagName')
                or tag.get('tag_name')
            )
            if name:
                tags.append(name)
    return tags


def extract_mentions(note: dict) -> list[str]:
    """提取 @ 用户"""
    mentions = []
    for m in note.get('atUserList') or []:
        if isinstance(m, dict):
            nick = m.get('nickname') or m.get('nickName')
            if nick:
                mentions.append(nick)
    return mentions


def normalize(detail_resp: dict) -> dict:
    """把 Skill 原始响应规范化为统一格式"""
    if not detail_resp or 'detail' not in detail_resp:
        return None

    note = detail_resp['detail'].get('note', {})
    if not note:
        return None

    user = note.get('user') or {}
    interact = note.get('interactInfo') or {}

    normalized = {
        'noteId': note.get('noteId'),
        'type': classify_note(note),
        'title': note.get('title', '').strip(),
        'desc': note.get('desc', '').strip(),
        'descLength': len(note.get('desc', '') or ''),
        'time': note.get('time'),
        'lastUpdateTime': note.get('lastUpdateTime'),
        'ipLocation': note.get('ipLocation'),

        # 作者
        'author': {
            'userId': user.get('userId'),
            'nickname': user.get('nickname') or user.get('nickName'),
            'avatar': user.get('avatar'),
            # P1-5 fix: 不持久化作者的 xsecToken（与原 note 的 token 分开，但同样敏感）
        },

        # 互动
        'interact': {
            'liked': interact.get('liked'),
            'likedCount': interact.get('likedCount'),
            'collected': interact.get('collected'),
            'collectedCount': interact.get('collectedCount'),
            'commentCount': interact.get('commentCount'),
            'shareCount': interact.get('shareCount'),
        },

        # 标签 / @用户
        'tags': extract_tags(note),
        'mentions': extract_mentions(note),

        # 内容（按类型）
        'images': extract_images(note) if note.get('type') != 'video' else [],
        'video': extract_video(note) if note.get('type') == 'video' else None,

        # 元
        'fetchedAt': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    return normalized


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='collection_*.json 路径')
    parser.add_argument('--limit', type=int, default=3, help='最多抓多少条')
    parser.add_argument('--output', default=None, help='输出 JSON 路径')
    parser.add_argument('--offset', type=int, default=0, help='从第几条开始')
    args = parser.parse_args()

    # 读已有收藏清单
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            coll = json.load(f)
    except FileNotFoundError:
        print(f'[ERR] 找不到输入文件: {args.input}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'[ERR] 输入 JSON 解析失败: {args.input}: {e}')
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f'[ERR] 输入文件编码错误: {args.input}: {e}')
        sys.exit(1)
    notes_meta = coll.get('notes', [])
    if not notes_meta:
        print('[ERR] input has no notes')
        sys.exit(1)

    target = notes_meta[args.offset:args.offset + args.limit]
    print(f'[OK] 准备抓 {len(target)} 条详情 (offset={args.offset}, limit={args.limit})')

    results = []
    for i, meta in enumerate(target):
        note_id = meta['noteId']
        xsec = meta['xsecToken']
        print(f'  [{i+1}/{len(target)}] {meta["title"][:30]}...')

        detail_resp = run_get_feed_detail(note_id, xsec, reuse_tab=True)
        if not detail_resp:
            print('    [SKIP] fetch failed')
            continue

        norm = normalize(detail_resp)
        if norm:
            norm['sourceMeta'] = {
                'originalTitle': meta['title'],
                'cover': meta.get('cover'),
                'authorFromList': meta.get('author'),
                'feedUrl': meta.get('feedUrl'),  # 修复：写入完整 feed URL（含 xsec_token）
            }
            results.append(norm)
            print(f'    type={norm["type"]} | imgs={len(norm["images"])} | '
                  f'desc={norm["descLength"]} | '
                  f'video={"yes" if norm["video"] else "no"}')
        else:
            print('    [SKIP] normalize failed')

        # 防风控间隔
        time.sleep(1.5)

    # 输出
    out_path = args.output or os.path.join(
        SCRIPT_DIR, '..', 'outputs', 'feed-detail',
        f'details_{time.strftime("%Y%m%d_%H%M%S")}.json'
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetchedAt': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'count': len(results),
            'byType': {
                t: sum(1 for r in results if r['type'] == t)
                for t in ['text_only', 'image_text', 'video', 'unknown']
            },
            'notes': results,
        }, f, ensure_ascii=False, indent=2)

    print(f'\n[OK] {len(results)} 条 → {out_path}')
    by_type = {}
    for r in results:
        by_type[r['type']] = by_type.get(r['type'], 0) + 1
    print(f'     类型分布: {by_type}')


if __name__ == '__main__':
    main()