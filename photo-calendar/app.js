// photo-calendar/app.js
import { dataService } from './firebase-service.js';

// DOM Elements
const currentMonthEl = document.getElementById('currentMonth');
const daysGridEl = document.getElementById('daysGrid');
const prevMonthBtn = document.getElementById('prevMonthBtn');
const nextMonthBtn = document.getElementById('nextMonthBtn');
const todayBtn = document.getElementById('todayBtn');
const statusChipEl = document.getElementById('statusChip');
const statusDotEl = document.getElementById('statusDot');
const statusTextEl = document.getElementById('statusText');
const btnOpenSettings = document.getElementById('btnOpenSettings');

// Modal Elements
const photoModal = document.getElementById('photoModal');
const modalTitle = document.getElementById('modalTitle');
const btnCloseModal = document.getElementById('btnCloseModal');
const previewContainer = document.getElementById('previewContainer');
const previewImg = document.getElementById('previewImg');
const photoMetaTag = document.getElementById('photoMetaTag');
const uploadDropzone = document.getElementById('uploadDropzone');
const fileInput = document.getElementById('fileInput');
const btnDeletePhoto = document.getElementById('btnDeletePhoto');
const btnReplacePhoto = document.getElementById('btnReplacePhoto');
const uploadProgress = document.getElementById('uploadProgress');

// Settings Modal Elements
const settingsModal = document.getElementById('settingsModal');
const btnCloseSettings = document.getElementById('btnCloseSettings');
const btnSaveConfig = document.getElementById('btnSaveConfig');
const btnResetConfig = document.getElementById('btnResetConfig');
const firebaseConfigInput = document.getElementById('firebaseConfigInput');
const currentConfigSource = document.getElementById('currentConfigSource');

// Application State
let currentDate = new Date();
let selectedDateStr = null;
let currentPhotos = {};
let currentStatus = { mode: 'local', isConnected: false };

// Format date to YYYY-MM-DD
function formatDateStr(year, month, day) {
  const m = String(month + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${year}-${m}-${d}`;
}

// 7칸 제약 조건 2: "브라우저에서 정사각형 512픽셀 JPEG로 줄이고 품질은 0.7로 한다."
function resizeImageToSquare512(file) {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith('image/')) {
      return reject(new Error('이미지 파일만 올릴 수 있습니다.'));
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // 가로/세로 중 짧은 쪽을 기준으로 중앙 크롭(Center Crop)
        const minSide = Math.min(img.width, img.height);
        const sx = (img.width - minSide) / 2;
        const sy = (img.height - minSide) / 2;

        // 고품질 보간 설정
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';

        // 512x512 캔버스에 그리기
        ctx.drawImage(img, sx, sy, minSide, minSide, 0, 0, 512, 512);

        // JPEG 0.7 품질로 압축 변환
        const base64Data = canvas.toDataURL('image/jpeg', 0.7);
        // 대략적인 바이트 크기 계산 (Firestore 1MB 문서 한도 검증)
        const sizeBytes = Math.round((base64Data.length * 3) / 4);
        const sizeKb = Math.round(sizeBytes / 1024);

        resolve({
          dataUrl: base64Data,
          sizeKb: sizeKb,
          originalWidth: img.width,
          originalHeight: img.height,
          originalSizeKb: Math.round(file.size / 1024)
        });
      };
      img.onerror = () => reject(new Error('이미지를 읽을 수 없습니다.'));
      img.src = e.target.result;
    };
    reader.onerror = () => reject(new Error('파일 읽기 실패'));
    reader.readAsDataURL(file);
  });
}

// Render Calendar
function renderCalendar() {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  currentMonthEl.textContent = `${year}년 ${month + 1}월`;

  const firstDayIndex = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();
  const prevLastDate = new Date(year, month, 0).getDate();

  const today = new Date();
  const isThisMonth = today.getFullYear() === year && today.getMonth() === month;
  const todayDate = today.getDate();

  daysGridEl.innerHTML = '';

  // 이전 달 날짜 채우기 (딤 처리)
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const dayNum = prevLastDate - i;
    const prevDateStr = formatDateStr(month === 0 ? year - 1 : year, month === 0 ? 11 : month - 1, dayNum);
    const cell = createDateCell(dayNum, prevDateStr, true, false);
    daysGridEl.appendChild(cell);
  }

  // 이번 달 날짜 채우기
  for (let d = 1; d <= lastDate; d++) {
    const dateStr = formatDateStr(year, month, d);
    const isToday = isThisMonth && d === todayDate;
    const dayOfWeek = (firstDayIndex + d - 1) % 7;
    const cell = createDateCell(d, dateStr, false, isToday, dayOfWeek);
    daysGridEl.appendChild(cell);
  }

  // 다음 달 날짜 채우기 (마지막 행 채우기)
  const totalCells = firstDayIndex + lastDate;
  const nextDays = (7 - (totalCells % 7)) % 7;
  for (let d = 1; d <= nextDays; d++) {
    const nextDateStr = formatDateStr(month === 11 ? year + 1 : year, month === 11 ? 0 : month + 1, d);
    const cell = createDateCell(d, nextDateStr, true, false);
    daysGridEl.appendChild(cell);
  }
}

function createDateCell(dayNum, dateStr, isOtherMonth, isToday, dayOfWeek) {
  const cell = document.createElement('div');
  cell.className = 'day-cell';
  if (isOtherMonth) cell.classList.add('other-month');
  if (isToday) cell.classList.add('today');
  if (dayOfWeek === 0) cell.classList.add('sunday');
  if (dayOfWeek === 6) cell.classList.add('saturday');

  const photoEntry = currentPhotos[dateStr];
  if (photoEntry && photoEntry.photo) {
    cell.classList.add('has-photo');
  }

  // Day Header (number)
  const header = document.createElement('div');
  header.className = 'day-header';
  const numSpan = document.createElement('span');
  numSpan.className = 'day-number';
  numSpan.textContent = dayNum;
  header.appendChild(numSpan);
  cell.appendChild(header);

  // Photo Thumbnail or Placeholder
  if (photoEntry && photoEntry.photo) {
    const thumbContainer = document.createElement('div');
    thumbContainer.className = 'photo-thumb-container';

    const img = document.createElement('img');
    img.className = 'photo-thumb';
    img.src = photoEntry.photo;
    img.alt = `${dateStr} 사진`;
    img.loading = 'lazy';

    const overlay = document.createElement('div');
    overlay.className = 'photo-overlay';
    overlay.innerHTML = '<span>🔍</span>';

    thumbContainer.appendChild(img);
    thumbContainer.appendChild(overlay);
    cell.appendChild(thumbContainer);
  } else {
    const placeholder = document.createElement('div');
    placeholder.className = 'empty-placeholder';
    placeholder.textContent = '+';
    cell.appendChild(placeholder);
  }

  cell.addEventListener('click', () => openPhotoModal(dateStr));
  return cell;
}

// Modal Handling
function openPhotoModal(dateStr) {
  selectedDateStr = dateStr;
  modalTitle.textContent = `📅 ${dateStr} 사진`;

  const existing = currentPhotos[dateStr];
  if (existing && existing.photo) {
    // 이미 사진이 있는 경우: 미리보기 모드
    previewContainer.style.display = 'flex';
    previewImg.src = existing.photo;
    photoMetaTag.textContent = `규격: 512×512px 정사각형 (${existing.sizeKb || '~80'}KB)`;
    btnDeletePhoto.style.display = 'inline-flex';
    btnReplacePhoto.style.display = 'inline-flex';
    uploadDropzone.style.display = 'none';
  } else {
    // 사진이 없는 경우: 즉시 업로드 모드
    previewContainer.style.display = 'none';
    btnDeletePhoto.style.display = 'none';
    btnReplacePhoto.style.display = 'none';
    uploadDropzone.style.display = 'block';
  }

  uploadProgress.style.display = 'none';
  photoModal.classList.add('active');
}

function closePhotoModal() {
  photoModal.classList.remove('active');
  selectedDateStr = null;
  fileInput.value = '';
}

// 7칸 제약 조건 1: "한 날짜에는 사진 한 장만 저장한다. 이미 있으면 바꿀지 먼저 물어본다."
async function handleFileSelected(file) {
  if (!file || !selectedDateStr) return;

  const existing = currentPhotos[selectedDateStr];
  if (existing && existing.photo) {
    const ok = confirm(`이미 ${selectedDateStr}에 등록된 사진이 있습니다.\n새 사진으로 바꾸시겠습니까?`);
    if (!ok) {
      fileInput.value = '';
      return;
    }
  }

  try {
    uploadProgress.style.display = 'block';
    uploadProgress.textContent = '⏳ 브라우저에서 512px 정사각형으로 줄이는 중...';

    // 512x512 JPEG 0.7 압축
    const resized = await resizeImageToSquare512(file);

    uploadProgress.textContent = `💾 저장 중 (${resized.sizeKb}KB)...`;

    // 7칸 제약 조건 3: Cloud Storage 없이 Firestore Base64로 저장
    await dataService.savePhoto(selectedDateStr, resized.dataUrl, resized.sizeKb);

    uploadProgress.textContent = '✅ 저장 완료!';
    setTimeout(() => {
      closePhotoModal();
    }, 400);
  } catch (err) {
    alert(`사진 업로드 실패: ${err.message}`);
    uploadProgress.style.display = 'none';
  } finally {
    fileInput.value = '';
  }
}

// Delete Photo
async function handleDeletePhoto() {
  if (!selectedDateStr) return;
  const ok = confirm(`${selectedDateStr} 사진을 삭제하시겠습니까?`);
  if (!ok) return;

  try {
    await dataService.deletePhoto(selectedDateStr);
    closePhotoModal();
  } catch (err) {
    alert(`삭제 실패: ${err.message}`);
  }
}

// Settings Modal Handling
function openSettingsModal() {
  const status = dataService.getStatus();
  currentConfigSource.textContent = status.activeConfig 
    ? (status.activeConfig.source === 'localStorage' ? '브라우저 설정(LocalStorage) 사용 중' : 'firebase-config.js 파일 설정 사용 중')
    : '설정 없음 (로컬 저장소 모드)';

  try {
    const stored = localStorage.getItem('vibecoding_firebase_config');
    firebaseConfigInput.value = stored ? JSON.stringify(JSON.parse(stored), null, 2) : '';
  } catch (e) {
    firebaseConfigInput.value = '';
  }

  settingsModal.classList.add('active');
}

function closeSettingsModal() {
  settingsModal.classList.remove('active');
}

function handleSaveConfig() {
  const raw = firebaseConfigInput.value.trim();
  if (!raw) {
    alert('Firebase 설정 JSON 객체를 입력하세요.');
    return;
  }

  try {
    let parsed;
    // 사용자 친화성: JS 객체 형태(키에 따옴표 없는 경우)도 처리
    if (!raw.startsWith('{')) {
      throw new Error('{ 로 시작하는 객체 형식이어야 합니다.');
    }
    // JS 객체 리터럴 파싱 지원
    try {
      parsed = JSON.parse(raw);
    } catch {
      // JSON 파싱 실패 시 함수 평가로 시도
      parsed = new Function(`return (${raw});`)();
    }

    if (!parsed || !parsed.apiKey || !parsed.projectId) {
      alert('설정에 apiKey와 projectId가 반드시 포함되어야 합니다.');
      return;
    }

    dataService.saveConfigFromUI(parsed);
  } catch (e) {
    alert(`설정 형식이 올바르지 않습니다: ${e.message}`);
  }
}

// Event Listeners
prevMonthBtn.addEventListener('click', () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar();
});

nextMonthBtn.addEventListener('click', () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar();
});

todayBtn.addEventListener('click', () => {
  currentDate = new Date();
  renderCalendar();
});

btnCloseModal.addEventListener('click', closePhotoModal);
photoModal.addEventListener('click', (e) => {
  if (e.target === photoModal) closePhotoModal();
});

btnOpenSettings.addEventListener('click', openSettingsModal);
statusChipEl.addEventListener('click', openSettingsModal);
btnCloseSettings.addEventListener('click', closeSettingsModal);
settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) closeSettingsModal();
});

btnSaveConfig.addEventListener('click', handleSaveConfig);
btnResetConfig.addEventListener('click', () => {
  if (confirm('저장된 Firebase 설정을 지우고 브라우저 로컬 모드로 복구하시겠습니까?')) {
    dataService.clearStoredConfig();
  }
});

btnDeletePhoto.addEventListener('click', handleDeletePhoto);
btnReplacePhoto.addEventListener('click', () => {
  uploadDropzone.style.display = 'block';
  previewContainer.style.display = 'none';
  btnDeletePhoto.style.display = 'none';
  btnReplacePhoto.style.display = 'none';
});

// Dropzone & File Input
uploadDropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files[0]) {
    handleFileSelected(e.target.files[0]);
  }
});

uploadDropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadDropzone.classList.add('dragover');
});

uploadDropzone.addEventListener('dragleave', () => {
  uploadDropzone.classList.remove('dragover');
});

uploadDropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadDropzone.classList.remove('dragover');
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    handleFileSelected(e.dataTransfer.files[0]);
  }
});

// Escape key closes modals
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closePhotoModal();
    closeSettingsModal();
  }
});

// Subscribe to Data Service
dataService.onPhotosUpdated((photos) => {
  currentPhotos = photos;
  renderCalendar();
});

dataService.onStatusChanged((status) => {
  currentStatus = status;

  statusChipEl.className = 'status-chip';
  if (status.mode === 'firebase' && status.isConnected) {
    statusChipEl.classList.add('firebase-connected');
    statusTextEl.textContent = '🟢 Firebase 실시간 연결';
    statusChipEl.title = `서버 연결됨 (UID: ${status.userUid || '익명'})`;
  } else if (status.errorMessage && status.errorMessage.includes('익명')) {
    statusChipEl.classList.add('error-mode');
    statusTextEl.textContent = '⚠️ 익명 로그인 꺼짐';
    statusChipEl.title = status.errorMessage;
  } else if (status.errorMessage && status.mode !== 'local') {
    statusChipEl.classList.add('error-mode');
    statusTextEl.textContent = '⚠️ 연결 오류';
    statusChipEl.title = status.errorMessage;
  } else {
    statusChipEl.classList.add('local-mode');
    statusTextEl.textContent = '🟡 로컬 모드 (서버 미설정)';
    statusChipEl.title = 'Firebase가 설정되지 않아 브라우저 로컬 저장소에 저장됩니다. (클릭하여 설정)';
  }
});

// Start application
dataService.init();
renderCalendar();
