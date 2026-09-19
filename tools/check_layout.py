# -*- coding: utf-8 -*-
"""DESIGN.md 의 레이아웃 규칙(L01~L15)을 index.html / styles.css 에 대해 검사한다.

    python tools/check_layout.py

기준 문서는 DESIGN.md 다. 규칙을 바꾸면 두 파일을 함께 고친다.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
CSS = os.path.join(ROOT, 'styles.css')

SECTION_ORDER = (
    ['hero', 'ladder-map']
    + ['rung-%d' % i for i in range(9)]
    + ['safety', 'glossary', 'limits']
)
BLOCKS_PRACTICE = ['why', 'how', 'prompt', 'check', 'trouble']
BLOCKS_BY_RUNG = {0: ['cards', 'check'], 1: ['cards', 'checklist'],
                  8: ['cards', 'checklist']}
TOKENS = [
    '--ink', '--canvas', '--soft-cloud', '--hairline', '--hairline-soft',
    '--charcoal', '--ash', '--mute', '--stone', '--success', '--sale', '--info',
    '--font-display', '--font-ui', '--content-max', '--gutter',
    '--sp-sm', '--sp-md', '--sp-lg', '--sp-xl', '--sp-xxl', '--sp-section',
    '--rounded-none', '--rounded-lg', '--rounded-full',
]
BREAKPOINTS = {'1023px', '900px', '768px', '599px'}
EMOJI = re.compile(
    u'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\u2b00-\u2bff\ufe0f]'
)

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

results = []


def check(rule, title, ok, detail=''):
    results.append((rule, title, bool(ok), detail))


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def main():
    if not os.path.exists(HTML):
        print('index.html 이 아직 없습니다. 페이지를 만든 뒤 다시 실행하세요.')
        print('  기대 경로: %s' % HTML)
        return 2
    html = io.open(HTML, encoding='utf-8').read()
    css = io.open(CSS, encoding='utf-8').read() if os.path.exists(CSS) else ''

    # L01 섹션 순서
    ids = re.findall(r'<section[^>]*\bid="([^"]+)"', html)
    check('L01', '섹션 순서가 DESIGN.md §3 과 같다', ids == SECTION_ORDER,
          '' if ids == SECTION_ORDER else '실제: %s' % ' > '.join(ids or ['(없음)']))

    # L02 rung id + data-rung
    bad = []
    rungs = {}
    for m in re.finditer(r'<section\b[^>]*\bid="rung-(\d)"[^>]*>', html):
        n = int(m.group(1))
        tag = m.group(0)
        if 'data-rung="%d"' % n not in tag:
            bad.append('rung-%d' % n)
        rungs[n] = m.start()
    check('L02', '모든 칸에 id="rung-N" 과 data-rung="N" 이 있다',
          len(rungs) == 9 and not bad,
          'data-rung 누락: %s' % ', '.join(bad) if bad else
          ('칸 %d개만 발견' % len(rungs) if len(rungs) != 9 else ''))

    # 칸 본문 잘라두기
    # 각 칸의 본문은 '다음 <section' 직전까지다. 마지막 칸이 꼬리 섹션을
    # 삼키지 않도록 rung 뿐 아니라 모든 section 시작 위치를 경계로 쓴다.
    starts = [m.start() for m in re.finditer(r'<section\b', html)]
    tail = re.search(r'<footer', html)
    if tail:
        starts.append(tail.start())
        starts.sort()
    bodies = {}
    for n, start in rungs.items():
        nxt = [p for p in starts if p > start]
        bodies[n] = html[start:(nxt[0] if nxt else len(html))]

    # L03 lecture-row 구성
    bad = [n for n, b in bodies.items()
           if not (re.search(r'class="lecture-row\b', b)
                   and 'lecture-media' in b and 'lecture-copy' in b)]
    check('L03', '각 칸이 .lecture-row(.lecture-media + .lecture-copy) 를 갖는다',
          not bad, '누락: %s' % bad if bad else '')

    # L04 홀수 칸만 reverse
    bad = []
    for n, b in bodies.items():
        m = re.search(r'class="(lecture-row[^"]*)"', b)
        has = bool(m and 'reverse' in m.group(1))
        if has != (n % 2 == 1):
            bad.append('rung-%d(%s)' % (n, 'reverse 있음' if has else 'reverse 없음'))
    check('L04', 'reverse 가 홀수 칸에만 붙어 좌우 교차가 유지된다',
          not bad, ', '.join(bad))

    # L05 / L06 블록 순서
    bad = []
    for n, b in bodies.items():
        want = BLOCKS_BY_RUNG.get(n, BLOCKS_PRACTICE)
        got = re.findall(r'data-block="([a-z]+)"', b)
        if got != want:
            bad.append('rung-%d: %s (기대 %s)' % (n, got or ['(없음)'], want))
    check('L05', '실습 칸이 why > how > prompt > check > trouble 순서를 지킨다',
          not [x for x in bad if not x.startswith(('rung-0', 'rung-1', 'rung-8'))],
          '; '.join(x for x in bad if not x.startswith(('rung-0', 'rung-1', 'rung-8'))))
    check('L06', '0칸·1칸·8칸이 지정된 예외 블록 구성을 따른다',
          not [x for x in bad if x.startswith(('rung-0', 'rung-1', 'rung-8'))],
          '; '.join(x for x in bad if x.startswith(('rung-0', 'rung-1', 'rung-8'))))

    # L07 img alt
    noalt = [t for t in re.findall(r'<img\b[^>]*>', html) if not re.search(r'\balt=', t)]
    check('L07', '모든 <img> 에 alt 가 있다', not noalt,
          '%d개 누락' % len(noalt))

    # L08 사다리 지도
    m = re.search(r'<section[^>]*id="ladder-map".*?</section>', html, re.S)
    links = re.findall(r'href="#rung-(\d)"', m.group(0)) if m else []
    check('L08', '사다리 지도에 9칸 링크(#rung-0~8)가 모두 있다',
          sorted(set(links)) == [str(i) for i in range(9)],
          '발견: %s' % sorted(set(links)))

    # L09 제목 위계
    h1 = len(re.findall(r'<h1\b', html))
    badh2 = [n for n, b in bodies.items() if len(re.findall(r'<h2\b', b)) != 1]
    h4 = len(re.findall(r'<h[456]\b', html))
    check('L09', 'h1 은 1개, 칸마다 h2 1개, h4 이하 없음',
          h1 == 1 and not badh2 and h4 == 0,
          'h1=%d, h2 이상한 칸=%s, h4+=%d' % (h1, badh2, h4))

    # L10 인라인 style
    inline = re.findall(r'<[^>]+\sstyle="[^"]*"', html)
    check('L10', 'index.html 에 인라인 style 속성이 없다', not inline,
          '%d곳' % len(inline))

    # L11 색상 리터럴
    lit = re.findall(r'#[0-9a-fA-F]{6}\b|rgba?\(', html)
    check('L11', 'index.html 에 색상 리터럴이 없다 (토큰만 사용)', not lit,
          '%d곳: %s' % (len(lit), lit[:5]))

    # L12 AI 기본값 금지
    hits = []
    if 'linear-gradient' in css:
        hits.append('linear-gradient')
    if 'box-shadow' in css:
        hits.append('box-shadow')
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        if 'btn' in sel or 'full' in sel or 'avatar' in sel or ':root' in sel:
            continue
        for v in re.findall(r'border-radius:\s*([0-9]+)px', body):
            if int(v) >= 12:
                hits.append('border-radius %spx (%s)' % (v, sel.strip()[:40]))
    check('L12', 'styles.css 에 그라데이션·그림자·둥근 카드가 없다', not hits,
          ', '.join(hits[:6]))

    # L13 제목·버튼 이모지
    heads = re.findall(r'<h[123]\b[^>]*>(.*?)</h[123]>', html, re.S)
    btns = re.findall(r'<(?:a|button)\b[^>]*class="[^"]*btn[^"]*"[^>]*>(.*?)</(?:a|button)>',
                      html, re.S)
    bad = [strip_tags(t).strip()[:24] for t in heads + btns if EMOJI.search(strip_tags(t))]
    check('L13', '제목과 버튼 라벨에 이모지가 없다', not bad, ' / '.join(bad[:5]))

    # L14 토큰
    missing = [t for t in TOKENS if t + ':' not in css]
    check('L14', 'styles.css 에 필수 토큰이 모두 정의돼 있다', not missing,
          '누락: %s' % ', '.join(missing))

    # L15 브레이크포인트
    used = set(re.findall(r'@media[^{]*?(\d+px)', css))
    extra = used - BREAKPOINTS
    check('L15', '허용된 브레이크포인트(1023/900/768/599)만 쓴다', not extra,
          
          '추가 사용: %s' % ', '.join(sorted(extra)))

    # L16 칸 강조색
    miss = []
    for i in range(9):
        if '--rung-%d:' % i not in css or '--rung-%d-soft:' % i not in css:
            miss.append('--rung-%d' % i)
        if 'section[data-rung="%d"]' % i not in css:
            miss.append('data-rung=%d 매핑' % i)
    for name in ('safety', 'glossary', 'limits'):
        if '--pane-%s:' % name not in css:
            miss.append('--pane-%s' % name)
    check('L16', '칸마다 강조색과 바탕색이 정의·매핑돼 있다', not miss,
          '누락: %s' % ', '.join(miss[:6]))

    # L17 접기·펼치기
    need_html = ['lecture-toggle', 'aria-expanded', 'aria-controls',
                 'is-collapsed', 'is-collapsible', 'is-open', 'expand-all']
    gone = [t for t in need_html if t not in html]
    if '.lecture-detail.is-collapsed' not in css:
        gone.append('.lecture-detail.is-collapsed 스타일')
    if '.prompt-copy' not in css:
        gone.append('.prompt-copy 스타일')
    if 'is-collapsible' not in css or 'is-open' not in css:
        gone.append('접힌 칸의 .lecture-row 여백 규칙')
    check('L17', '접기·펼치기와 프롬프트 복사 버튼이 붙어 있다', not gone,
          '누락: %s' % ', '.join(gone))

    # L18 가로 정렬 — 독립 덩어리는 가운데, 제목 아래 리드는 왼쪽
    def rule_body(sel):
        m = re.search(re.escape(sel) + r'\s*\{([^}]*)\}', css)
        return m.group(1) if m else None

    def centered(body):
        return body is not None and ('margin-left: auto' in body or 'margin: 0 auto' in body)

    bad = []
    for sel in ['.lecture-detail', '.ladder-note', '.key-lead', '.key-foot']:
        if not centered(rule_body(sel)):
            bad.append('%s 는 가운데여야 한다' % sel)
    for sel in ['.hero .lead', '.pane .lead']:
        body = rule_body(sel)
        if body is None:
            bad.append('%s 규칙이 없다' % sel)
        elif centered(body):
            bad.append('%s 는 제목과 왼쪽을 맞춰야 한다' % sel)
    if 'justify-content: center' not in (rule_body('.lecture-detail .lecture-actions') or ''):
        bad.append('본문 안 버튼은 가운데로 모아야 한다')
    check('L18', '가운데 둘 것과 왼쪽에 맞출 것이 규칙대로다', not bad,
          '; '.join(bad))

    # L19 분량 상한
    CAPS = {'why': 320, 'how': 1300, 'check': 180, 'trouble': 650,
            'cards': 1000, 'checklist': 300}
    # 칸별 예외. 4칸은 길이 넷이라 how 안내도 넷이다 (DESIGN.md §6.5)
    CAPS_BY_RUNG = {(4, 'how'): 1800}
    PANE_CAP = 450

    def prose(x):
        x = re.sub(r'<table\b.*?</table>', '', x, flags=re.S)
        x = re.sub(r'<pre\b.*?</pre>', '', x, flags=re.S)
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x)).strip()

    over = []
    for n, b in bodies.items():
        marks = list(re.finditer(r'data-block="(\w+)"', b))
        for i, mk in enumerate(marks):
            e = marks[i+1].start() if i+1 < len(marks) else len(b)
            name = mk.group(1)
            size = len(prose(b[mk.start():e]))
            cap = CAPS_BY_RUNG.get((n, name), CAPS.get(name))
            if cap and size > cap:
                over.append('rung-%d/%s %d>%d' % (n, name, size, cap))
    for pane in ('safety', 'glossary', 'limits'):
        m = re.search(r'<section\b[^>]*id="%s".*?(?=<section\b|<footer\b|$)' % pane, html, re.S)
        if m:
            size = len(prose(m.group(0)))
            if size > PANE_CAP:
                over.append('%s %d>%d' % (pane, size, PANE_CAP))
    check('L19', '블록마다 분량 상한을 지킨다 (표·프롬프트 제외)', not over,
          ' / '.join(over))

    # 출력
    width = max(len(t) for _, t, _, _ in results)
    fails = 0
    print('')
    print('  DESIGN.md 레이아웃 규칙 검사')
    print('  ' + '-' * (width + 16))
    for rule, title, ok, detail in results:
        mark = 'PASS' if ok else 'FAIL'
        print('  %s  %s  %s' % (rule, mark, title))
        if not ok and detail:
            print('           %s' % detail)
        if not ok:
            fails += 1
    print('  ' + '-' * (width + 16))
    print('  %d개 중 %d개 통과' % (len(results), len(results) - fails))
    print('')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
