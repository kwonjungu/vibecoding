# -*- coding: utf-8 -*-
"""build/ 의 섹션 조각을 순서대로 이어 붙여 index.html 을 만든다.

    python tools/build_index.py

조각을 고친 뒤 이 명령을 다시 돌리면 index.html 이 갱신된다.
조각 순서는 DESIGN.md §3 페이지 골격을 따른다.
"""
import io
import os
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = [
    '01-hero-map.html',
    '02-rung-0-1.html',
    '03-rung-2-3.html',
    '04-rung-4.html',
    '05-rung-5-7.html',
    '06-rung-8.html',
    '07-tail.html',
]

HEAD = u'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>바이브 코딩 업그레이드 프로젝트!</title>
<meta name="description" content="브라우저만으로, 무료로, 쉬운 것부터 어려운 것까지. 초등 교사를 위한 바이브코딩 여덟 칸 실습 사다리." />
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

<script>
(function () {
  var items = [];
  var byId = {};
  var allBtn = null;

  function setOpen(item, open) {
    item.detail.classList.toggle('is-collapsed', !open);
    item.sec.classList.toggle('is-open', open);
    item.btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    item.btn.textContent = open ? '접기' : '자세히 보기';
  }

  // 모두 펼치기 버튼의 라벨은 실제 상태에서 끌어낸다.
  // 그래야 개별 토글로 몇 개 펼친 뒤에 눌러도 한 번에 반응한다.
  function syncAll() {
    if (!allBtn) { return; }
    var anyClosed = items.some(function (it) {
      return it.detail.classList.contains('is-collapsed');
    });
    allBtn.textContent = anyClosed ? '모두 펼치기' : '모두 접기';
    allBtn.setAttribute('aria-expanded', anyClosed ? 'false' : 'true');
  }

  Array.prototype.forEach.call(document.querySelectorAll('section.lecture'), function (sec) {
    var detail = sec.querySelector('.lecture-detail');
    var copy = sec.querySelector('.lecture-copy');
    if (!detail || !copy) { return; }

    detail.id = 'detail-' + sec.getAttribute('data-rung');
    detail.classList.add('is-collapsed');
    sec.classList.add('is-collapsible');

    // 머리 줄에 이미 있는 .lecture-actions 만 재활용한다.
    // 본문(.lecture-detail) 안의 .lecture-actions 는 접히면 같이 사라지므로 쓰지 않는다.
    var actions = null;
    for (var i = 0; i < copy.children.length; i += 1) {
      if (copy.children[i].className === 'lecture-actions') { actions = copy.children[i]; break; }
    }
    if (!actions) {
      actions = document.createElement('div');
      actions.className = 'lecture-actions';
      copy.appendChild(actions);
    }

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'lecture-toggle';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', detail.id);
    btn.textContent = '자세히 보기';
    actions.insertBefore(btn, actions.firstChild);

    var item = { sec: sec, detail: detail, btn: btn };
    items.push(item);
    byId[sec.id] = item;

    btn.addEventListener('click', function () {
      setOpen(item, detail.classList.contains('is-collapsed'));
      syncAll();
    });
  });

  // 모두 펼치기 / 모두 접기
  var map = document.getElementById('ladder-map');
  if (map && items.length) {
    var wrap = document.createElement('div');
    wrap.className = 'map-actions';
    allBtn = document.createElement('button');
    allBtn.type = 'button';
    allBtn.className = 'expand-all';
    allBtn.textContent = '모두 펼치기';
    allBtn.setAttribute('aria-expanded', 'false');
    wrap.appendChild(allBtn);
    map.appendChild(wrap);

    allBtn.addEventListener('click', function () {
      var opening = items.some(function (it) {
        return it.detail.classList.contains('is-collapsed');
      });
      items.forEach(function (it) { setOpen(it, opening); });
      syncAll();
    });
  }

  // 프롬프트 복사 버튼
  document.querySelectorAll('pre.prompt-box').forEach(function (box) {
    var bar = document.createElement('div');
    bar.className = 'prompt-bar';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'prompt-copy';
    btn.textContent = '복사';
    bar.appendChild(btn);
    box.parentNode.insertBefore(bar, box);

    btn.addEventListener('click', function () {
      copy(box.textContent).then(function (ok) {
        btn.textContent = ok ? '복사했습니다' : '직접 드래그해 복사하세요';
        btn.classList.toggle('is-done', ok);
        setTimeout(function () {
          btn.textContent = '복사';
          btn.classList.remove('is-done');
        }, 2000);
      });
    });
  });

  // https 에서는 클립보드 API 를 쓰고, file:// 로 열었을 때는 대체 방법을 쓴다
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text)
        .then(function () { return true; })
        .catch(function () { return legacy(text); });
    }
    return Promise.resolve(legacy(text));
  }

  function legacy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.className = 'offscreen';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  // 사다리 지도에서 칸을 고르면 그 칸만 펼친다.
  // 링크를 누르는 순간 먼저 펼쳐 두어야 브라우저가 최종 높이 기준으로 스크롤한다.
  Array.prototype.forEach.call(map ? map.querySelectorAll('a[href^="#rung-"]') : [], function (a) {
    a.addEventListener('click', function () {
      var item = byId[a.getAttribute('href').slice(1)];
      if (item) { setOpen(item, true); syncAll(); }
    });
  });

  function openFromHash(instant) {
    var id = window.location.hash.replace('#', '');
    if (!id) { return; }
    var item = byId[id];          // 칸이 아닌 해시(#safety 등)나 없는 해시면 그냥 넘어간다
    if (!item) { return; }
    var wasClosed = item.detail.classList.contains('is-collapsed');
    setOpen(item, true);
    syncAll();
    if (wasClosed && item.sec.scrollIntoView) {
      // 펼치면서 문서 높이가 늘어나므로 위치를 다시 맞춘다
      try {
        item.sec.scrollIntoView({ behavior: instant ? 'instant' : 'smooth', block: 'start' });
      } catch (e) {
        item.sec.scrollIntoView(true);
      }
    }
  }

  window.addEventListener('hashchange', function () { openFromHash(false); });
  openFromHash(true);
}());
</script>
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
    make_drop_zip()
    return 1 if missing else 0


def make_drop_zip():
    """4칸 길 C·D(버셀 드롭·넷틀리파이 드롭) 실습용 묶음을 만든다.

    배포에 필요한 것만 담는다. build/ tools/ docs/ 는 넣지 않는다.
    index.html 을 만들 때마다 다시 만들어지므로 낡지 않는다.
    """
    out = os.path.join(ROOT, 'assets', 'files', 'netlify-drop-practice.zip')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    picks = ['index.html', 'styles.css']
    for base in ('assets/logo', 'assets/shot', 'demo'):
        d = os.path.join(ROOT, base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            picks.append(base + '/' + name)
    total = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in picks:
            src = os.path.join(ROOT, rel)
            if os.path.isfile(src):
                z.write(src, '바이브코딩-사다리/' + rel)
                total += 1
    size = os.path.getsize(out) / 1024.0
    print('Netlify Drop 실습 묶음 — 파일 %d개, %.0fKB' % (total, size))





if __name__ == '__main__':
    sys.exit(main())
