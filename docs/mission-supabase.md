# 미션: 공용 캘린더를 내 Supabase로 옮기기

완성 예시: https://a-iroom.vercel.app/calandar
입장코드 1111과 이름으로 들어가서 월 달력에 한 줄씩 적는 공용 캘린더입니다. 내가 적은 것만 30분 안에 지울 수 있습니다.

이 미션의 목표는 같은 앱을 내 Supabase 프로젝트, 내 GitHub 저장소, 내 Vercel 배포로 옮기는 것입니다. 설치는 하지 않습니다. 브라우저만 씁니다.

준비물: 구글 계정 하나, 30분.

---

## 미션 1. Supabase 프로젝트 만들기

**지금 할 일**
데이터가 저장될 내 데이터베이스를 하나 만듭니다.

**어디를 누르나**
1. https://supabase.com 접속, 오른쪽 위 `Start your project`
2. `Continue with GitHub` 또는 `Continue with Google`로 로그인
3. `New project`
4. Name 칸에 `calendar`, Database Password 칸에 비밀번호를 적고 따로 메모
5. Region은 `Northeast Asia (Seoul)` 선택
6. `Create new project`, 2분 정도 기다립니다

**붙여넣을 것**
없습니다. 대신 다음 화면의 값 두 개를 메모장에 복사해 둡니다. 왼쪽 아래 `Settings` → `API`에서 `Project URL`과 `anon public` 키입니다. 미션 5에서 씁니다.

**이러면 성공입니다**
화면 위에 초록색 점과 함께 프로젝트 이름이 보입니다. `Project URL`이 `https://...supabase.co` 형태로 복사됩니다.

**막히면** 무료 프로젝트는 이레 동안 아무도 안 쓰면 잠깁니다. `Restore` 버튼을 누르면 다시 켜집니다.

---

## 미션 2. events 테이블 만들기

**지금 할 일**
캘린더 한 줄이 들어갈 표를 만듭니다.

**어디를 누르나**
1. 왼쪽 메뉴 `SQL Editor`
2. `New query`
3. 아래 내용을 붙여넣기
4. 오른쪽 아래 `Run`

**붙여넣을 것**
```sql
create table public.events (
  id bigint generated always as identity primary key,
  day date not null,
  title text not null,
  author text not null,
  owner text not null,
  created_at timestamptz not null default now()
);

create index events_day_idx on public.events (day);
```

**이러면 성공입니다**
아래에 `Success. No rows returned`이 뜹니다. 왼쪽 메뉴 `Table Editor`에 `events` 표가 보이고 열 이름이 day, title, author, owner, created_at입니다.

**막히면** `relation "events" already exists`가 뜨면 이미 만든 것입니다. 다시 만들지 말고 미션 3으로 갑니다.

---

## 미션 3. RLS 켜고 정책 만들기

**지금 할 일**
누구나 볼 수 있고, 짧은 글만 쓸 수 있고, 30분 안에만 지울 수 있게 규칙을 겁니다.

**어디를 누르나**
1. 왼쪽 메뉴 `SQL Editor`
2. `New query`
3. 아래 내용을 붙여넣기
4. `Run`

**붙여넣을 것**
```sql
alter table public.events enable row level security;

create policy "events_select_all"
on public.events
for select
to anon
using (true);

create policy "events_insert_short"
on public.events
for insert
to anon
with check (
  char_length(title) between 1 and 40
  and char_length(author) between 1 and 12
  and char_length(owner) between 1 and 64
);

create policy "events_delete_30min"
on public.events
for delete
to anon
using (created_at > now() - interval '30 minutes');

alter publication supabase_realtime add table public.events;
```

맨 끝 한 줄은 다른 사람이 적은 것이 새로고침 없이 뜨게 하는 설정입니다. 이 줄이 없으면 앱은 만들어지지만 남이 적은 것이 안 보입니다.

**이러면 성공입니다**
`Success. No rows returned`이 뜹니다. `Table Editor`에서 `events` 표 이름 옆에 `RLS enabled` 표시가 붙습니다. 왼쪽 메뉴 `Authentication` → `Policies`에 정책 세 개가 보입니다.

**막히면** anon 키는 브라우저에 그대로 드러나는 공개 값입니다. 진짜 방어선은 이 정책입니다. `service_role` 키는 여기서 절대 쓰지 않습니다. 그것은 다른 미션의 이야기입니다.

---

## 미션 4. GitHub 저장소에 올리기

**지금 할 일**
앱 파일을 만들어 내 GitHub 저장소에 올립니다.

**어디를 누르나**
1. Google AI Studio의 Build 화면에 아래 프롬프트를 붙여넣고 앱을 만든 뒤 파일을 내려받습니다
2. https://github.com 접속, 오른쪽 위 `+` → `New repository`
3. Repository name에 `my-calendar`, `Public` 선택, `Create repository`
4. 다음 화면에서 `uploading an existing file` 글자를 클릭
5. 받은 파일을 화면에 끌어다 놓고 `Commit changes`

**붙여넣을 것**
```
Vite와 React로 공용 캘린더 웹앱을 만들어 줘.
- 입장 화면: 입장코드 1111과 이름을 입력하면 들어간다. 이름은 브라우저에 저장한다.
- 본 화면: 월 달력. 날짜 칸을 누르면 한 줄을 적어 저장한다.
- 저장소는 Supabase. 테이블 events, 열은 day(date), title(text 40자), author(text 12자), owner(text), created_at(timestamptz).
- owner에는 브라우저마다 다른 임의 문자열을 하나 만들어 저장하고 그 값을 넣는다.
- 내 owner와 같고 created_at이 30분 안인 줄에만 삭제 버튼을 보여 준다.
- Supabase 주소와 키는 환경변수 VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY에서 읽는다.
- .env 파일은 저장소에 올리지 않게 .gitignore에 넣어 줘.
전체 파일을 한 번에 내려받을 수 있게 정리해 줘.
```

**이러면 성공입니다**
저장소 첫 화면에 `package.json`, `index.html`, `src` 폴더가 보입니다.

**막히면** 파일 목록에 `.env`가 보이면 지웁니다. 키를 코드 안에 직접 적지 않습니다. 압축을 푼 뒤 **폴더 아이콘째** 끌어다 놓습니다. 폴더를 열어 안의 파일만 끌면 브라우저가 이름만 넘겨 `src` 같은 경로가 사라집니다.

---

## 미션 5. Vercel에 연결하고 환경변수 넣기

**지금 할 일**
저장소를 인터넷 주소로 만들고, Supabase 주소와 키를 알려 줍니다.

**어디를 누르나**
1. https://vercel.com 접속, `Continue with GitHub`로 로그인
2. `Add New...` → `Project`
3. `my-calendar` 줄의 `Import`
4. `Environment Variables` 펼치기
5. Key에 `VITE_SUPABASE_URL`, Value에 미션 1에서 복사한 Project URL, `Add`
6. Key에 `VITE_SUPABASE_ANON_KEY`, Value에 anon public 키, `Add`
7. `Deploy`, 1분 정도 기다립니다

**붙여넣을 것**
```
VITE_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
```

**이러면 성공입니다**
`https://my-calendar-....vercel.app` 주소가 나옵니다. 열어서 1111과 이름으로 들어가고, 한 줄 적으면 화면에 남습니다. Supabase `Table Editor`의 `events` 표에도 같은 줄이 보입니다.

**막히면** 이름 앞에 `VITE_`가 없으면 브라우저가 값을 읽지 못합니다. 환경변수를 넣거나 고친 뒤에는 반드시 다시 배포해야 반영됩니다. `Deployments` → 맨 위 줄 오른쪽 `...` → `Redeploy`를 누릅니다.
