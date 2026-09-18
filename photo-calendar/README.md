# 📷 우리 반 하루 한 장 사진 캘린더 (바이브코딩 7칸)

바이브코딩 사다리 **7칸(서버 활용 — 날짜별 사진 캘린더)**의 의도와 제약 조건을 충실히 구현한 실습용 웹 애플리케이션입니다.

---

## 🎯 7칸 핵심 제약 조건 구현 사항

1. **하루 한 장 고정 & 교체 확인**:
   - 한 날짜에는 오직 하나의 사진만 등록됩니다.
   - 이미 등록된 날짜에 새 사진을 올리려고 하면 먼저 교체 여부를 확인(Confirm)합니다.
2. **브라우저 내 512px 정사각형 JPEG 리사이징**:
   - 사진을 업로드하면 서버로 보내기 전, 브라우저 `<canvas>`에서 자동으로 중앙 기준 정사각형 크롭 및 `512×512`, `JPEG 품질 0.7`로 압축합니다.
   - 원본 사진이 수 MB여도 약 **60~110KB** 크기로 안전하게 압축됩니다.
3. **Cloud Storage 없이 Firestore Base64 직접 저장**:
   - 2026년 2월 이후 유료 결제 계정이 필요한 Firebase Storage 대신, Firestore 문서의 `photo` 필드(문자열)에 Base64 형태로 직접 저장합니다. (Firestore 문서 한도 1MB 대비 약 1/10 수준으로 넉넉합니다.)
4. **얼굴 사진 금지 안내 상시 표시**:
   - 학급 및 공개 링크 환경에서 초상권 보호를 위해 **"학생 얼굴이 나온 사진은 올리지 않는다"**는 주의 배너를 상단 및 모달 창에 상시 표시합니다.
5. **실시간 동시 동기화 (`onSnapshot`)**:
   - Firestore 실시간 리스너를 통해 다른 학생이나 교사가 사진을 올리거나 변경하면 새로고침 없이 즉시 달력 화면에 반영됩니다.
6. **로컬 모드 Fallback 지원**:
   - Firebase 설정이 없는 상태에서도 로컬스토리지(LocalStorage) 모드로 자동 작동하여 오프라인에서도 모든 기능(달력, 리사이징, 사진 보기/삭제)을 미리 체험해 볼 수 있습니다.

---

## 🚀 실행 방법

### 방법 1. 로컬 웹 서버로 열기 (권장)

ES Module(Firebase SDK) 로드를 위해 로컬 웹 서버 환경에서 여는 것을 권장합니다:

```bash
# 터미널에서 프로젝트 루트 디렉터리로 이동 후 실행
python -m http.server 8000
```

브라우저 주소창에 다음 주소를 입력합니다:
👉 **`http://localhost:8000/photo-calendar/`**

---

## 🔌 Firebase 서버 연결 방법

### 방법 A. 웹 화면에서 바로 붙여넣기 (가장 편리함)
1. 브라우저에서 캘린더 페이지(`http://localhost:8000/photo-calendar/`)를 엽니다.
2. 우측 상단의 **[⚙️ 서버 설정]** 버튼을 누릅니다.
3. Firebase 콘솔이나 AI Studio Build에서 복사한 `firebaseConfig` 객체(JSON 형태)를 붙여넣고 **[저장 및 연결]**을 누릅니다.
4. 페이지가 새로고침되며 즉시 **🟢 Firebase 실시간 연결** 상태로 전환됩니다.

### 방법 B. `firebase-config.js` 파일에 직접 넣기
[`photo-calendar/firebase-config.js`](file:///c:/Users/권준구/Downloads/vibecoding/photo-calendar/firebase-config.js) 파일을 열고 프로젝트 설정을 채워 넣습니다:

```javascript
export const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "my-classroom-app.firebaseapp.com",
  projectId: "my-classroom-app",
  storageBucket: "my-classroom-app.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef"
};
```

---

## 🛡️ Firebase 콘솔 필수 체크리스트 (6칸/7칸 공통)

1. **Authentication (익명 로그인 켜기)**:
   - Firebase 콘솔 → **빌드(Build) / 보안(Security)** → **Authentication**
   - **Sign-in method (로그인 방법)** 탭 → **익명(Anonymous)** 제공업체를 **사용 설정(사용)**으로 켭니다.
   - *(익명이 꺼져 있으면 `auth/admin-restricted-operation` 에러가 발생합니다.)*

2. **Firestore 데이터베이스 및 보안 규칙 배포**:
   - Firebase 콘솔 → **Firestore Database** 생성
   - **규칙(Rules)** 탭에 [`photo-calendar/firestore.rules`](file:///c:/Users/권준구/Downloads/vibecoding/photo-calendar/firestore.rules) 파일의 내용을 붙여넣고 **게시(Publish)**합니다:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /calendar_photos/{dateId} {
         allow read: if true;
         allow write: if request.auth != null;
       }
     }
   }
   ```
