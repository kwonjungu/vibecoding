# DESIGN.md — 바이브코딩 사다리

이 문서는 두 가지 역할을 한다.

1. **AI에게 넘기는 디자인 명세.** 이 페이지를 고칠 때 이 파일을 함께 준다.
2. **하네스의 검사 기준.** 아래 `L##` 규칙은 `tools/check_layout.py`가 그대로 검사한다.

기반은 `kwonjungu/classroomaicontents`의 Nike 에디토리얼 시스템이다. 토큰과 컴포넌트 이름을 승계한다.

---

## 1. 원칙

- **검정·흰색·소프트클라우드가 화면의 95%.** 색으로 구분하지 않고 **크기와 여백**으로 구분한다.
- **평평하게.** 카드에 그림자와 라운드를 주지 않는다. 사진이 곧 카드다.
- **번호가 곧 표지판.** 9칸 사다리는 색이 아니라 큰 숫자(`01`~`08`, `00`)로 구분한다.
- **이 페이지는 2칸에서 "AI 기본값 디자인"을 비판한다.** 따라서 자기 자신이 보라색 그라데이션·둥근 카드·짙은 그림자·제목 이모지를 쓰면 안 된다. 이건 취향이 아니라 **자기모순 방지**다. §8에서 금지 규칙으로 못 박는다.

---

## 2. 토큰

`styles.css`의 `:root`에 아래를 모두 정의한다 (**L14**).

### 색

| 토큰 | 값 | 용도 |
|---|---|---|
| `--ink` | `#111111` | 본문·헤드라인 |
| `--canvas` | `#ffffff` | 기본 배경 |
| `--soft-cloud` | `#f5f5f5` | 섹션 교차 배경, 프롬프트 박스 |
| `--hairline` | `#cacacb` | 구분선 |
| `--hairline-soft` | `#e5e5e5` | 입력·카드 테두리 |
| `--charcoal` | `#39393b` | 본문 보조 |
| `--ash` | `#4b4b4d` | 캡션 |
| `--mute` | `#707072` | 키커·메타 |
| `--stone` | `#9e9ea0` | 비활성 |
| `--success` | `#007d48` | "이러면 성공입니다" |
| `--sale` | `#d30005` | "막히면"·경고·개인정보 |
| `--info` | `#1151ff` | 링크 강조 |

색은 이 12개가 전부다. 그 밖의 색상값을 새로 쓰지 않는다.

### 타이포

```
--font-display: "Black Han Sans", "Bebas Neue", "Pretendard", sans-serif;
--font-ui:      "Pretendard", "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
```

| 단계 | 크기 / 줄간격 | 글꼴 | 쓰는 곳 |
|---|---|---|---|
| display | 96px / 0.9 | display | 히어로 `h1` |
| rung-no | 120px / 0.8 | display | 칸 번호 |
| h2 | 44px / 1.05 | display | 칸 제목 |
| h3 | 20px / 1.3, 700 | ui | 블록 제목 |
| lead | 18px / 1.6 | ui | 칸 도입 문단 |
| body | 16px / 1.5 | ui | 본문 |
| kicker | 12px / 1.2, letter-spacing .12em, 대문자 | ui | `SECTION 01` |
| caption | 14px / 1.5 | ui | 캡션·각주 |

### 간격 · 라운드 · 레이아웃

8px 기준. `--sp-xxs 2 / --sp-xs 4 / --sp-sm 8 / --sp-md 12 / --sp-lg 18 / --sp-xl 24 / --sp-xxl 30 / --sp-section 48`.

`--rounded-none 0` (카드·박스 기본값) · `--rounded-lg 30px` (버튼) · `--rounded-full` (원형 아이콘). **카드에 라운드를 쓰지 않는다.**

`--content-max: 1440px` · `--gutter: 40px` (모바일 20px).

---

## 3. 페이지 골격 (순서 고정 — **L01**)

```
1  section.hero            질문형 헤드라인
2  section.ladder-map      9칸 지도 (탭 역할)
3  section.lecture#rung-0  준비물 챙기기
4  section.lecture#rung-1  배경지식
5  section.lecture#rung-2  웹페이지 디자인
6  section.lecture#rung-3  재료 만들어 붙이기
7  section.lecture#rung-4  주소 만들기
8  section.lecture#rung-5  결과 모으기
9  section.lecture#rung-6  서버 체험
10 section.lecture#rung-7  사진 캘린더
11 section.lecture#rung-8  앱이 AI를 부르게
12 section.safety          안전 한 장
13 section.glossary        용어 한 장
14 section.limits          무료 한도 표
15 section.beyond          더 멀리 가려면
```

- 칸 섹션은 `id="rung-N"`과 `data-rung="N"`을 함께 가진다 (**L02**).
- 순서를 바꾸거나 칸을 끼워 넣지 않는다. 사다리의 순서가 곧 내용이다.

---

## 4. 칸(rung) 내부 골격

### 4.1 머리 — `.lecture-row` (**L03**, **L04**)

```html
<div class="lecture-row">            <!-- 짝수 칸 -->
<div class="lecture-row reverse">    <!-- 홀수 칸 -->
  <div class="lecture-media"><span class="lecture-no">03</span><img ...></div>
  <div class="lecture-copy">
    <p class="lecture-kicker">STEP 03</p>
    <h2>재료 만들어 붙이기</h2>
    <p class="lead">…</p>
    <div class="lecture-actions">…</div>
  </div>
</div>
```

`reverse`는 **홀수 칸에만** 붙어 좌우가 교차한다. 2열 그리드 `1fr 1fr`, 간격 `--sp-xxl`.

### 4.2 몸 — 5블록 고정 (**L05**)

`.lecture-detail` 안에 아래 다섯 블록이 **이 순서 그대로** 들어간다. 빠뜨리거나 순서를 바꾸지 않는다.

| 순서 | `data-block` | 제목 | 형태 |
|---|---|---|---|
| 1 | `why` | 왜 필요한가 | 문단 1~2개. 식당 비유로 연결 |
| 2 | `how` | 이렇게 합니다 | `<ol>`. 클릭할 위치까지 명시 |
| 3 | `prompt` | 복붙 프롬프트 | `.prompt-box` — `--soft-cloud` 배경, 등폭 글꼴, 라운드 없음 |
| 4 | `check` | 이러면 성공입니다 | `.check-list` 항목 3개. `--success` 불릿. **눈으로 보이는 것만** 쓴다 |
| 5 | `trouble` | 막히면 | `.trouble` — 접힌 `<details>`. 각 항목 `증상 → 원인 → 해결` 세 줄 |

**예외 (L06)**: `rung-1`(배경지식)은 실습이 없어 `cards`(핵심 카드 4개) + `checklist` 두 블록만 갖는다. `rung-0`(준비물)은 `cards`(계정 카드 3개) + `check`를 갖는다.

---

## 5. 컴포넌트 규격

| 클래스 | 규격 |
|---|---|
| `.ladder-map` | 9칸 그리드. 데스크톱 3열 × 3행, 768px 이하 1열. 각 항목은 `번호 · 제목 · 도구 · 남는 것` 4줄, `href="#rung-N"` (**L08**) |
| `.note-card` | 배경 `--soft-cloud`, 라운드 0, 그림자 없음, 패딩 `--sp-xl` |
| `.guide-key` / `.key-grid` | 3열(768px 이하 1열). 각 `.key-item`은 `.key-label`(kicker) + `.key-text` |
| `.prompt-box` | `--soft-cloud` 배경, 좌측 4px `--ink` 띠, `pre` 유지, 사용자가 드래그해 복사 |
| `.check-list` | `list-style:none`, 앞에 `✓` 의사요소, 색 `--success` |
| `.trouble` | `<details>` + `<summary>`. 좌측 4px `--sale` 띠 |
| `.btn` | pill(`--rounded-lg`). `.btn-primary`는 `--ink` 배경 / 흰 글씨, `.btn-secondary`는 테두리만 |
| `.guide-shot` | `<figure>`. 캡처 자리. 없을 땐 비워 두되 `figcaption`으로 "연수 전 촬영" 표시 |

---

## 6. 반응형 (**L15**)

브레이크포인트는 **네 개만** 쓴다: `1023px` · `900px` · `768px` · `599px`.

- `≤1023px` — `--gutter` 40 → 28px
- `≤900px` — `.lecture-row` 1열. `reverse`는 무효가 되고 **미디어가 항상 위**로 간다
- `≤768px` — `.ladder-map`·`.key-grid`·`.note-cards` 전부 1열
- `≤599px` — display 96 → 52px, rung-no 120 → 64px, h2 44 → 30px, `--gutter` 20px

가로 스크롤은 어떤 폭에서도 생기지 않는다. 넓은 표는 `.table-scroll`로 감싸 **그 안에서만** 가로 스크롤한다.

---

## 7. 접근성

- `h1`은 페이지에 하나. 칸 제목은 `h2`, 블록 제목은 `h3`. 단계를 건너뛰지 않는다 (**L09**)
- 모든 `<img>`에 `alt`. 장식용이면 `alt=""` (**L07**)
- 본문 대비 4.5:1 이상. `--stone`(#9e9ea0)은 흰 배경 본문에 쓰지 않는다 — 메타 정보 전용
- 접기/펼치기는 `<details>`를 쓰거나 `aria-expanded` + `aria-controls`를 붙인다
- 링크 텍스트는 "여기"가 아니라 목적지를 쓴다

---

## 8. 금지 (**L10**~**L13**)

| ID | 금지 | 이유 |
|---|---|---|
| **L10** | `index.html`의 인라인 `style=` 속성 | 규칙이 두 곳에 흩어진다 |
| **L11** | `index.html`의 색상 리터럴(`#rrggbb`, `rgb(`) | 토큰만 쓴다 |
| **L12** | `linear-gradient`로 칠한 배경, `border-radius ≥ 12px`인 카드, `box-shadow` | 2칸에서 비판하는 바로 그 AI 기본값 |
| **L13** | 제목(`h1`~`h3`)·버튼 라벨 안의 이모지 | 같은 이유. 이모지는 식당 비유 아이콘(홀·주방·주문서·건물)에만 허용하고 `<span class="emoji" aria-hidden="true">`로 감싼다 |

`demo/worksheet-before.html`은 **일부러 이 규칙을 전부 어긴 표본**이므로 검사 대상에서 제외한다.

---

## 9. 하네스

```
python tools/check_layout.py          # 규칙 L01~L15 검사
python -m http.server 8000            # 그 다음 tools/harness.html 을 연다
```

`tools/harness.html`은 `index.html`을 360 · 768 · 1280px 폭으로 나란히 띄워 **가로 스크롤과 1열 전환**을 눈으로 확인하게 한다.

규칙을 바꿀 때는 이 문서와 `tools/check_layout.py`를 **함께** 고친다. 둘이 어긋나면 이 문서가 기준이다.
