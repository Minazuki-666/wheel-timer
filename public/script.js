// タイマーアプリ - Web版 JavaScript

class TimerApp {
    constructor() {
        // タイマー状態
        this.hours = 0;
        this.minutes = 0;
        this.seconds = 0;
        this.secondsLeft = 0;
        this.timerRunning = false;
        this.timerPaused = false;
        this.timerInterval = null;
        this.timerCompleted = false;  // タイマー完了状態を追加
        this.soundInterval = null;   // 音響通知のインターバル用
        this.originalTime = 0;       // 元の設定時間を保存
        
        // DOM要素の取得
        this.timeDisplay = document.getElementById('timeDisplay');
        this.statusDisplay = document.getElementById('statusDisplay');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        
        // 時間表示要素
        this.hoursElement = document.getElementById('hours');
        this.minutesElement = document.getElementById('minutes');
        this.secondsElement = document.getElementById('seconds');
        
        // イベントリスナーの設定
        this.setupEventListeners();
        
        // 初期表示の更新
        this.updateDisplay();
        
        // デバッグ情報
        this.debugEnabled = false;
        this.debugLog = document.getElementById('debugLog');
    }
    
    setupEventListeners() {
        // マウスホイールイベント
        document.getElementById('hoursContainer').addEventListener('wheel', (e) => {
            e.preventDefault();
            if (!this.timerRunning) {
                const delta = e.deltaY > 0 ? -1 : 1;
                this.adjustTime('hours', delta);
            }
        });
        
        document.getElementById('minutesContainer').addEventListener('wheel', (e) => {
            e.preventDefault();
            if (!this.timerRunning) {
                const delta = e.deltaY > 0 ? -1 : 1;
                this.adjustTime('minutes', delta);
            }
        });
        
        document.getElementById('secondsContainer').addEventListener('wheel', (e) => {
            e.preventDefault();
            if (!this.timerRunning) {
                const delta = e.deltaY > 0 ? -1 : 1;
                this.adjustTime('seconds', delta);
            }
        });
        
        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !this.timerRunning) {
                this.startTimer();
            } else if (e.key === ' ') {
                e.preventDefault();
                if (this.timerRunning) {
                    this.pauseTimer();
                }
            } else if (e.key === 'Escape') {
                this.resetTimer();
            } else if (e.key === 'r' || e.key === 'R') {
                this.resetTimer();
            }
        });
        
        // デバッグモード切り替え (Ctrl+D)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                this.toggleDebug();
            }
        });
    }
    
    adjustTime(unit, delta) {
        if (this.timerRunning) return;
        
        let value;
        let max;
        
        switch (unit) {
            case 'hours':
                value = this.hours;
                max = 23;
                break;
            case 'minutes':
                value = this.minutes;
                max = 59;
                break;
            case 'seconds':
                value = this.seconds;
                max = 59;
                break;
        }
        
        value += delta;
        
        if (value > max) {
            value = 0;
        } else if (value < 0) {
            value = max;
        }
        
        // 値を更新
        switch (unit) {
            case 'hours':
                this.hours = value;
                break;
            case 'minutes':
                this.minutes = value;
                break;
            case 'seconds':
                this.seconds = value;
                break;
        }
        
        this.updateDisplay();
        this.log(`${unit}を${delta > 0 ? '増加' : '減少'}: ${value}`);
    }
    
    setQuickTime(totalSeconds) {
        if (this.timerRunning) return;
        
        this.hours = Math.floor(totalSeconds / 3600);
        this.minutes = Math.floor((totalSeconds % 3600) / 60);
        this.seconds = totalSeconds % 60;
        
        this.updateDisplay();
        this.log(`クイック設定: ${this.formatTime(totalSeconds)}`);
    }
    
    updateDisplay() {
        // 時間設定表示の更新
        this.hoursElement.textContent = this.hours;
        this.minutesElement.textContent = this.minutes;
        this.secondsElement.textContent = this.seconds;
        
        // メインタイマー表示の更新
        if (this.timerRunning) {
            const timeStr = this.formatTimeDisplay(this.secondsLeft);
            this.timeDisplay.textContent = timeStr;
        } else {
            const totalSeconds = this.hours * 3600 + this.minutes * 60 + this.seconds;
            const timeStr = this.formatTimeDisplay(totalSeconds);
            this.timeDisplay.textContent = timeStr;
            this.secondsLeft = totalSeconds;
            
            // ステータス表示の更新
            if (totalSeconds > 0) {
                const timeText = this.formatTimeMessage(totalSeconds);
                this.statusDisplay.textContent = `設定時間: ${timeText}`;
            } else {
                this.statusDisplay.textContent = "マウスホイールで時間を調整してください";
            }
        }
    }
    
    formatTimeDisplay(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    formatTimeMessage(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        const parts = [];
        if (hours > 0) parts.push(`${hours}時間`);
        if (minutes > 0) parts.push(`${minutes}分`);
        if (seconds > 0 || (hours === 0 && minutes === 0)) parts.push(`${seconds}秒`);
        
        return parts.join('');
    }
    
    formatTime(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        if (hours > 0) {
            return `${hours}時間${minutes}分${seconds}秒`;
        } else if (minutes > 0) {
            return `${minutes}分${seconds}秒`;
        } else {
            return `${seconds}秒`;
        }
    }
    
    startTimer() {
        if (this.timerCompleted) {
            // タイマー完了状態からの再開（ストップ処理）
            this.stopTimer();
            return;
        }
        
        if (this.timerPaused) {
            // 一時停止から再開
            this.timerPaused = false;
            this.statusDisplay.textContent = "タイマー実行中...";
            this.pauseBtn.textContent = "⏸ 一時停止";
            this.log("タイマー再開");
        } else if (!this.timerRunning && this.secondsLeft > 0) {
            // 新しいタイマー開始
            this.timerRunning = true;
            this.timerCompleted = false;
            this.originalTime = this.secondsLeft;  // 元の時間を保存
            this.statusDisplay.textContent = "タイマー実行中...";
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            this.pauseBtn.textContent = "⏸ 一時停止";
            
            this.log(`タイマー開始: ${this.secondsLeft}秒`);
            
            // タイマー実行
            this.timerInterval = setInterval(() => {
                this.runTimer();
            }, 1000);
        } else {
            this.log(`タイマー開始できません - 実行中: ${this.timerRunning}, 時間: ${this.secondsLeft}`);
        }
    }
    
    pauseTimer() {
        if (this.timerCompleted) {
            // タイマー完了状態からのストップ処理
            this.stopTimer();
            return;
        }
        
        if (this.timerRunning && !this.timerPaused) {
            this.timerPaused = true;
            this.statusDisplay.textContent = "タイマー一時停止中";
            this.pauseBtn.textContent = "▶ 再開";
            this.log("タイマー一時停止");
        } else {
            this.startTimer(); // 再開処理
        }
    }
    
    stopTimer() {
        this.log("タイマーストップ");
        
        // 音響通知を停止
        if (this.soundInterval) {
            clearInterval(this.soundInterval);
            this.soundInterval = null;
        }
        
        // タイマー停止
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        this.timerRunning = false;
        this.timerPaused = false;
        this.timerCompleted = false;
        
        // 元の設定時間に戻す
        this.secondsLeft = this.originalTime;
        
        // UI表示をリセット
        this.timeDisplay.classList.remove('completed');
        this.statusDisplay.classList.remove('completed');
        
        // ボタン状態をリセット
        this.startBtn.disabled = false;
        this.pauseBtn.disabled = true;
        this.pauseBtn.textContent = "⏸ 一時停止";
        
        this.updateDisplay();
    }
    
    resetTimer() {
        this.log("タイマーリセット");
        
        // 音響通知を停止
        if (this.soundInterval) {
            clearInterval(this.soundInterval);
            this.soundInterval = null;
        }
        
        // タイマー停止
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        this.timerRunning = false;
        this.timerPaused = false;
        this.timerCompleted = false;
        this.secondsLeft = 0;
        this.originalTime = 0;
        
        // 時間設定をリセット
        this.hours = 0;
        this.minutes = 0;
        this.seconds = 0;
        
        // UI表示をリセット
        this.timeDisplay.textContent = "00:00:00";
        this.timeDisplay.classList.remove('completed');
        this.statusDisplay.textContent = "マウスホイールで時間を調整してください";
        this.statusDisplay.classList.remove('completed');
        
        // ボタン状態をリセット
        this.startBtn.disabled = false;
        this.pauseBtn.disabled = true;
        this.pauseBtn.textContent = "⏸ 一時停止";
        
        this.updateDisplay();
    }
    
    runTimer() {
        if (!this.timerPaused && this.timerRunning) {
            this.secondsLeft--;
            this.log(`残り時間: ${this.secondsLeft}秒`);
            
            this.updateDisplay();
            
            if (this.secondsLeft <= 0) {
                this.log("タイマー完了！");
                this.timerComplete();
            }
        }
    }
    
    timerComplete() {
        this.log("timer_complete処理開始");
        
        // タイマー停止
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        this.timerRunning = false;
        this.timerPaused = false;
        this.timerCompleted = true;  // 完了状態をマーク
        this.secondsLeft = 0;
        
        // UI表示を更新（強調表示）
        this.timeDisplay.textContent = "00:00:00";
        this.timeDisplay.classList.add('completed');
        this.statusDisplay.textContent = "🎉 タイマー終了！ 音を止めるにはストップまたはリセットを押してください";
        this.statusDisplay.classList.add('completed');
        
        // ボタン状態を更新（ストップボタンに変更）
        this.startBtn.disabled = true;
        this.pauseBtn.disabled = false;
        this.pauseBtn.textContent = "⏹ ストップ";
        
        // 継続的な音響通知を開始
        this.startContinuousSound();
        
        this.log("timer_complete処理完了");
    }
    
    startContinuousSound() {
        this.log("=== 継続的音響通知開始 ===");
        
        // 最初の音を即座に再生
        this.playCompletionSound();
        
        // 1秒ごとに音を繰り返し再生
        this.soundInterval = setInterval(() => {
            if (this.timerCompleted) {
                this.playCompletionSound();
            } else {
                // 完了状態でなければ停止
                clearInterval(this.soundInterval);
                this.soundInterval = null;
                this.log("音響通知自動停止");
            }
        }, 2000);
        
        this.log("継続的音響通知設定完了");
    }
    
    playCompletionSound() {
        this.log("=== タイマー完了音再生開始 ===");
        
        try {
            // Web Audio APIを使用した音響生成
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // 3つの音を順番に再生
            const frequencies = [880, 659, 880]; // 高音→中音→高音
            const duration = 300; // 各音の長さ（ミリ秒）
            
            frequencies.forEach((freq, index) => {
                setTimeout(() => {
                    this.playBeep(audioContext, freq, duration);
                }, index * (duration + 100));
            });
            
            this.log("Web Audio API音再生完了 ✅");
            
        } catch (error) {
            this.log(`Web Audio APIエラー: ${error}`);
            
            // フォールバック: HTMLオーディオ要素
            try {
                this.playSystemSound();
            } catch (fallbackError) {
                this.log(`音響フォールバックエラー: ${fallbackError}`);
                // 視覚的通知のみ
                console.log("🔔🔔🔔 タイマー完了！ 🔔🔔🔔");
            }
        }
        
        this.log("=== タイマー完了音再生終了 ===");
    }
    
    playBeep(audioContext, frequency, duration) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration / 1000);
    }
    
    playSystemSound() {
        // data URIを使用した簡単な音の生成
        const audioData = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAdAjiR2OSjeGMfBiiB1eK9dSQGJHfE7duZTAUXaLjj2ZBEBhFdr+LhmmUVDEij5u6rY';
        const audio = new Audio(audioData);
        audio.play().catch(e => {
            console.log('Audio play failed:', e);
        });
    }
    
    toggleDebug() {
        this.debugEnabled = !this.debugEnabled;
        const debugSection = document.getElementById('debugSection');
        debugSection.style.display = this.debugEnabled ? 'block' : 'none';
        this.log(`デバッグモード: ${this.debugEnabled ? 'ON' : 'OFF'}`);
    }
    
    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logMessage = `[${timestamp}] ${message}`;
        console.log(logMessage);
        
        if (this.debugEnabled && this.debugLog) {
            this.debugLog.textContent += logMessage + '\n';
            this.debugLog.scrollTop = this.debugLog.scrollHeight;
        }
    }
}

// グローバル関数（HTMLから呼び出し用）
let timerApp;

function adjustTime(unit, delta) {
    timerApp.adjustTime(unit, delta);
}

function setQuickTime(totalSeconds) {
    timerApp.setQuickTime(totalSeconds);
}

function startTimer() {
    timerApp.startTimer();
}

function pauseTimer() {
    timerApp.pauseTimer();
}

function stopTimer() {
    timerApp.stopTimer();
}

function resetTimer() {
    timerApp.resetTimer();
}

// アプリケーションの初期化
document.addEventListener('DOMContentLoaded', () => {
    timerApp = new TimerApp();
    console.log('タイマーアプリ - Web版が起動しました');
    console.log('操作方法:');
    console.log('- マウスホイール: 時間調整');
    console.log('- クリック: ボタン操作');
    console.log('- Enter: タイマー開始');
    console.log('- Space: 一時停止/再開');
    console.log('- Escape/R: リセット');
    console.log('- Ctrl+D: デバッグモード切り替え');
});
