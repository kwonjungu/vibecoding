# 바이브코딩 사다리

코딩을 몰라도 앱을 만들 수 있을까요. **브라우저만으로, 무료로, 쉬운 것부터 어려운 것까지** 여덟 칸을 차례로 오르는 초등 교사용 실습 페이지입니다.

배포 주소: `https://kwonjungu.github.io/vibecoding/`

## 아홉 칸

| 칸 | 제목 | 도구 | 끝나면 남는 것 |
|---|---|---|---|
| 0 | 준비물 챙기기 | GitHub · AI Studio · Firebase | 계정 3개 |
| 1 | 더 나은 바이브코딩을 위한 배경지식 | 개념 칸 | 시작하기 전의 판단 기준 |
| 2 | 웹페이지 디자인 | Gemini Canvas · getdesign.md | 디자인이 입혀진 내 활동지 |
| 3 | 재료 만들어 붙이기 | AI Studio · 이미지 생성 | 그림이 들어간 `assets` 폴더 |
| 4 | 주소 만들기 | GitHub Pages · ai.studio | QR 찍으면 열리는 내 앱 |
| 5 | 서버 체험 — 게임과 기록표 | AI Studio Build · Firebase | 링크만 공유하면 동시 접속 |
| 6 | 서버 활용 — 날짜별 사진 캘린더 | Firestore | 하루 한 장, 규격 고정 |
| 7 | 앱이 AI를 부르게 | AI Studio Build | 힌트 버튼, 키는 서버에만 |

CLI·IDE 계열 도구(Claude Code·Antigravity·Cursor 등)는 설치가 필요해 연수장에서 쓸 수 없으므로 이름만 소개합니다.

## 파일

| 파일 | 내용 |
|---|---|
| `index.html` | 페이지 (조각을 이어 붙여 생성된 결과물) |
| `styles.css` | 디자인 시스템 토큰과 컴포넌트 |
| `DESIGN.md` | **레이아웃 규칙 설계서.** 페이지를 고치기 전에 읽는다 |
| `build/*.html` | 섹션 조각. **실제로 고치는 곳은 여기다** |
| `demo/worksheet-before.html` | 2칸에서 쓰는 "전형적인 바이브코딩 결과물" 표본 |
| `assets/shot/` | 화면 캡처 |
| `tools/build_index.py` | 조각을 이어 붙여 `index.html` 생성 |
| `tools/check_layout.py` | `DESIGN.md` 규칙 L01~L15 자동 검사 |
| `tools/harness.html` | 360 · 768 · 1280px 동시 미리보기 |
| `docs/superpowers/specs/` | 내용 설계 문서 |

## 고치는 법

`index.html` 을 직접 고치지 않습니다. 이 파일은 생성물입니다.

```bash
# 1. build/ 안의 해당 조각을 고친다
# 2. 다시 이어 붙인다
python tools/build_index.py

# 3. 규칙을 지켰는지 검사한다
python tools/check_layout.py

# 4. 여러 폭에서 눈으로 확인한다
python -m http.server 8000
#    그 다음 http://localhost:8000/tools/harness.html
```

`check_layout.py` 가 전부 PASS 가 아니면 고치기 전 상태다. 규칙 자체를 바꿔야 한다면 `DESIGN.md` 와 `check_layout.py` 를 **함께** 고칩니다. 둘이 어긋나면 `DESIGN.md` 가 기준입니다.

## 캡처 채우기

`assets/shot/` 에 이미 들어 있는 것:

- `rung3-assets-before.png` / `rung3-assets-after.png` — 같은 게임의 기본 이모지 상태와 생성 이미지 적용 상태
- `rung6-firebase-01~04*.png` — Firebase 익명 로그인 활성화 4단계

아직 비어 있는 자리는 `<figure class="guide-shot">` 로 표시해 두었습니다. 로그인해야 나오는 화면이라 연수 전에 직접 촬영해 채웁니다.

## 배포

저장소 **Settings → Pages → Branch: `main` / `(root)`** 저장.

## 안전

공개 저장소입니다. 학생 이름과 얼굴 사진, 교과서 지문과 삽화, API 키를 넣지 않습니다.
