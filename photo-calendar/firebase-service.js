// photo-calendar/firebase-service.js
import { firebaseConfig as fileConfig } from './firebase-config.js';

// Firebase v10 Modular SDK CDN
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js';
import { 
  getAuth, 
  signInAnonymously, 
  onAuthStateChanged 
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  deleteDoc, 
  onSnapshot, 
  serverTimestamp 
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js';

const LOCAL_STORAGE_DATA_KEY = 'vibecoding_local_photos';
const LOCAL_STORAGE_CONFIG_KEY = 'vibecoding_firebase_config';
const COLLECTION_NAME = 'calendar_photos';

class DataService {
  constructor() {
    this.app = null;
    this.auth = null;
    this.db = null;
    this.user = null;
    this.mode = 'local'; // 'firebase' | 'local'
    this.isConnected = false;
    this.errorMessage = null;
    this.statusListeners = [];
    this.photoListeners = [];
    this.photos = {};
    this.unsubscribeFirestore = null;
  }

  // 활성 설정 가져오기 (localStorage 우선, 그다음 파일 설정)
  getActiveConfig() {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_CONFIG_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.apiKey && parsed.projectId) {
          return { config: parsed, source: 'localStorage' };
        }
      }
    } catch (e) {
      console.warn('Failed to parse stored Firebase config:', e);
    }

    if (fileConfig && fileConfig.apiKey && fileConfig.projectId) {
      return { config: fileConfig, source: 'file' };
    }

    return null;
  }

  async init() {
    const active = this.getActiveConfig();

    if (!active) {
      console.log('💡 [캘린더] Firebase 설정이 없어 [로컬 저장소 모드]로 시작합니다.');
      this.mode = 'local';
      this.isConnected = false;
      this.errorMessage = 'Firebase 미설정 (브라우저 로컬 저장 모드)';
      this.loadLocalPhotos();
      this.notifyStatus();
      return;
    }

    try {
      this.app = initializeApp(active.config);
      this.auth = getAuth(this.app);
      this.db = getFirestore(this.app);

      // 익명 로그인 상태 감시
      onAuthStateChanged(this.auth, async (user) => {
        if (user) {
          this.user = user;
          this.mode = 'firebase';
          this.isConnected = true;
          this.errorMessage = null;
          console.log('✅ [Firebase] 익명 로그인 성공 UID:', user.uid);
          this.notifyStatus();
          this.startFirestoreSubscription();
        } else {
          try {
            await signInAnonymously(this.auth);
          } catch (authErr) {
            console.error('❌ [Firebase] 익명 로그인 실패:', authErr);
            this.handleAuthError(authErr);
          }
        }
      });
    } catch (err) {
      console.error('❌ [Firebase] 초기화 오류:', err);
      this.mode = 'local';
      this.isConnected = false;
      this.errorMessage = err.message || 'Firebase 초기화 실패';
      this.loadLocalPhotos();
      this.notifyStatus();
    }
  }

  handleAuthError(err) {
    this.isConnected = false;
    if (err.code === 'auth/admin-restricted-operation') {
      this.errorMessage = '익명 로그인이 꺼져 있습니다. Firebase 콘솔 Authentication에서 [익명]을 켜주세요.';
    } else {
      this.errorMessage = `인증 실패: ${err.message}`;
    }
    // 인증 실패 시에도 기본 데이터는 로컬에서 안전하게 보여줌
    this.mode = 'local';
    this.loadLocalPhotos();
    this.notifyStatus();
  }

  startFirestoreSubscription() {
    if (!this.db) return;
    if (this.unsubscribeFirestore) {
      this.unsubscribeFirestore();
    }

    const colRef = collection(this.db, COLLECTION_NAME);
    this.unsubscribeFirestore = onSnapshot(colRef, (snapshot) => {
      const updatedPhotos = {};
      snapshot.forEach((docSnap) => {
        const data = docSnap.data();
        if (data && data.photo) {
          updatedPhotos[docSnap.id] = {
            date: docSnap.id,
            photo: data.photo,
            updatedAt: data.updatedAt ? data.updatedAt.toDate() : new Date(),
            sizeKb: data.sizeKb || Math.round((data.photo.length * 3 / 4) / 1024)
          };
        }
      });
      this.photos = updatedPhotos;
      this.notifyPhotos();
    }, (err) => {
      console.error('❌ [Firestore] 실시간 동기화 오류:', err);
      if (err.code === 'permission-denied') {
        this.errorMessage = 'Firestore 보안 규칙 거부: firestore.rules를 확인하고 배포해 주세요.';
      } else {
        this.errorMessage = `Firestore 오류: ${err.message}`;
      }
      this.notifyStatus();
    });
  }

  // 로컬스토리지 백업 모드
  loadLocalPhotos() {
    try {
      const data = localStorage.getItem(LOCAL_STORAGE_DATA_KEY);
      this.photos = data ? JSON.parse(data) : {};
    } catch (e) {
      this.photos = {};
    }
    this.notifyPhotos();
  }

  saveLocalPhotos() {
    try {
      localStorage.setItem(LOCAL_STORAGE_DATA_KEY, JSON.stringify(this.photos));
    } catch (e) {
      console.error('Failed to save to localStorage:', e);
    }
    this.notifyPhotos();
  }

  // 사진 저장 (7칸 제약 조건: Cloud Storage 없이 Base64 문자열로 Firestore에 저장)
  async savePhoto(dateStr, base64Photo, sizeKb) {
    if (this.mode === 'firebase' && this.db && this.isConnected) {
      const docRef = doc(this.db, COLLECTION_NAME, dateStr);
      await setDoc(docRef, {
        date: dateStr,
        photo: base64Photo,
        sizeKb: sizeKb || Math.round((base64Photo.length * 3 / 4) / 1024),
        updatedAt: serverTimestamp(),
        authorUid: this.user ? this.user.uid : 'anonymous'
      });
      console.log(`✅ [Firestore] ${dateStr} 사진 저장 완료 (${sizeKb}KB)`);
    } else {
      // 로컬 모드 저장
      this.photos[dateStr] = {
        date: dateStr,
        photo: base64Photo,
        sizeKb: sizeKb || Math.round((base64Photo.length * 3 / 4) / 1024),
        updatedAt: new Date()
      };
      this.saveLocalPhotos();
      console.log(`💾 [Local] ${dateStr} 로컬 저장 완료 (${sizeKb}KB)`);
    }
  }

  // 사진 삭제
  async deletePhoto(dateStr) {
    if (this.mode === 'firebase' && this.db && this.isConnected) {
      const docRef = doc(this.db, COLLECTION_NAME, dateStr);
      await deleteDoc(docRef);
      console.log(`🗑️ [Firestore] ${dateStr} 사진 삭제 완료`);
    } else {
      delete this.photos[dateStr];
      this.saveLocalPhotos();
      console.log(`🗑️ [Local] ${dateStr} 사진 삭제 완료`);
    }
  }

  // Firebase 설정 저장 (UI에서 붙여넣었을 때)
  saveConfigFromUI(configObj) {
    localStorage.setItem(LOCAL_STORAGE_CONFIG_KEY, JSON.stringify(configObj));
    window.location.reload();
  }

  // Firebase 설정 초기화
  clearStoredConfig() {
    localStorage.removeItem(LOCAL_STORAGE_CONFIG_KEY);
    window.location.reload();
  }

  onPhotosUpdated(listener) {
    this.photoListeners.push(listener);
    listener(this.photos);
  }

  onStatusChanged(listener) {
    this.statusListeners.push(listener);
    listener(this.getStatus());
  }

  notifyPhotos() {
    for (const listener of this.photoListeners) {
      listener(this.photos);
    }
  }

  notifyStatus() {
    const status = this.getStatus();
    for (const listener of this.statusListeners) {
      listener(status);
    }
  }

  getStatus() {
    return {
      mode: this.mode,
      isConnected: this.isConnected,
      errorMessage: this.errorMessage,
      userUid: this.user ? this.user.uid : null,
      activeConfig: this.getActiveConfig()
    };
  }
}

export const dataService = new DataService();
