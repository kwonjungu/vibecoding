# -*- coding: utf-8 -*-
"""build/ 의 섹션 조각을 순서대로 이어 붙여 index.html 을 만든다.

    python tools/build_index.py

조각을 고친 뒤 이 명령을 다시 돌리면 index.html 이 갱신된다.
조각 순서는 DESIGN.md §3 페이지 골격을 따른다.
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = [
    '01-hero-map.html',
    '02-rung-0-1.html',
    '03-rung-2-3.html',
    '04-rung-4-5.html',
    '05-rung-6-8.html',
    '06-tail.html',
]

HEAD = u'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>바이브코딩 사다리 — 코딩 몰라도 앱을 만들 수 있을까요?</title>
<meta name="description" content="브라우저만으로, 무료로, 쉬운 것부터 어려운 것까지. 초등 교사를 위한 바이브코딩 아홉 칸 실습 사다리." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap" rel="stylesheet" />
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" rel="stylesheet" />
<link rel="stylesheet" href="styles.css" />
</head>
<body>
'''

FOOT = u'''
<footer class="pane">
  <p class="caption">바이브코딩 사다리 · 브라우저에서 무료로 되는 것만 담았습니다.</p>
</footer>
</body>
</html>
'''


def main():
    out = [HEAD]
    missing = []
    for name in PARTS:
        path = os.path.join(ROOT, 'build', name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        body = io.open(path, encoding='utf-8').read().strip()
        out.append(u'\n<!-- ===== %s ===== -->\n' % name)
        out.append(body)
        out.append(u'\n')
    if missing:
        print('빠진 조각: %s' % ', '.join(missing))
        print('그 부분을 뺀 채로 index.html 을 만듭니다.')
    out.append(FOOT)
    target = os.path.join(ROOT, 'index.html')
    io.open(target, 'w', encoding='utf-8').write(u''.join(out))
    lines = u''.join(out).count('\n') + 1
    print('index.html 생성 완료 — %d줄, 조각 %d개' % (lines, len(PARTS) - len(missing)))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
