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
    + ['safety', 'glossary', 'limits', 'beyond']
)
BLOCKS_PRACTICE = ['why', 'how', 'prompt', 'check', 'trouble']
BLOCKS_BY_RUNG = {0: ['cards', 'check'], 1: ['cards', 'checklist']}
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
          not [x for x in bad if not x.startswith(('rung-0', 'rung-1'))],
          '; '.join(x for x in bad if not x.startswith(('rung-0', 'rung-1'))))
    check('L06', '0칸·1칸이 지정된 예외 블록 구성을 따른다',
          not [x for x in bad if x.startswith(('rung-0', 'rung-1'))],
          '; '.join(x for x in bad if x.startswith(('rung-0', 'rung-1'))))

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
