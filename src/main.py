import tkinter as tk
from tkinter import font, ttk
import time
import threading
import winsound  # Windowsでの音声通知用
import os
import sys
# from win10toast import ToastNotifier  # Windows通知用

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("タイマーアプリ - マウスホイール調整")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        # # 通知用オブジェクト
        # self.toaster = ToastNotifier()
        
        # タイマー状態変数
        self.seconds_left = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_thread = None
        
        # 時間設定用変数
        self.hours = tk.IntVar(value=0)
        self.minutes = tk.IntVar(value=0)
        self.seconds = tk.IntVar(value=0)
        
        # 表示用フォント
        self.display_font = font.Font(family="Arial", size=48, weight="bold")
        self.button_font = font.Font(family="Arial", size=14)
        self.label_font = font.Font(family="Arial", size=16, weight="bold")
        self.time_font = font.Font(family="Arial", size=32, weight="bold")
        
        # メインフレーム（レスポンシブデザイン用）
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイマー表示部分
        self.display_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.display_frame.pack(fill=tk.X, pady=20)
        
        self.time_display = tk.Label(
            self.display_frame, 
            text="00:00:00", 
            font=self.display_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        self.time_display.pack()
        
        # 状態表示部分
        self.status_display = tk.Label(
            self.display_frame, 
            text="マウスホイールで時間を調整してください", 
            font=font.Font(family="Arial", size=14), 
            bg="#f0f0f0", 
            fg="#666666"
        )
        self.status_display.pack(pady=10)
        
        # 時間設定部分
        self.create_time_input()
        
        # コントロールボタン部分
        self.create_control_buttons()
        
        # キーボードイベントをバインド
        self.root.bind("<Key>", self.keyboard_input)
        
        # ウィンドウサイズ変更イベントをバインド
        self.root.bind("<Configure>", self.on_window_resize)
        
        # 時間変数の変更を監視
        self.hours.trace('w', self.on_time_change)
        self.minutes.trace('w', self.on_time_change)
        self.seconds.trace('w', self.on_time_change)
        
    def create_time_input(self):
        """マウスホイールで調整可能な時間入力エリアを作成"""
        input_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=20)
        
        # タイトル
        title_label = tk.Label(
            input_frame,
            text="時間設定（マウスホイールで調整）",
            font=self.label_font,
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 10))
        
        # 時間設定エリア
        time_input_frame = tk.Frame(input_frame, bg="#f0f0f0")
        time_input_frame.pack()
        
        # 時間部分
        self.create_time_unit(time_input_frame, "時間", self.hours, 0, 23, 0)
        
        # コロン1
        tk.Label(time_input_frame, text=":", font=self.time_font, bg="#f0f0f0", fg="#333333").grid(row=1, column=1, padx=5)
        
        # 分部分
        self.create_time_unit(time_input_frame, "分", self.minutes, 0, 59, 2)
        
        # コロン2
        tk.Label(time_input_frame, text=":", font=self.time_font, bg="#f0f0f0", fg="#333333").grid(row=1, column=3, padx=5)
        
        # 秒部分
        self.create_time_unit(time_input_frame, "秒", self.seconds, 0, 59, 4)
        
    def create_time_unit(self, parent, label_text, var, min_val, max_val, column):
        """時間単位の入力エリアを作成"""
        # ラベル
        label = tk.Label(parent, text=label_text, font=self.button_font, bg="#f0f0f0", fg="#666666")
        label.grid(row=0, column=column, padx=10)
        
        # 値表示とホイール入力エリア
        value_frame = tk.Frame(parent, bg="#ffffff", relief=tk.RAISED, bd=2)
        value_frame.grid(row=1, column=column, padx=10, pady=5)
        
        # 値表示ラベル
        value_label = tk.Label(
            value_frame,
            textvariable=var,
            font=self.time_font,
            bg="#ffffff",
            fg="#333333",
            width=3,
            height=1
        )
        value_label.pack(padx=10, pady=10)
        
        # マウスホイールイベントをバインド
        value_frame.bind("<Button-4>", lambda e: self.wheel_up(var, max_val))  # Linux
        value_frame.bind("<Button-5>", lambda e: self.wheel_down(var, min_val))  # Linux
        value_frame.bind("<MouseWheel>", lambda e: self.mouse_wheel(e, var, min_val, max_val))  # Windows/Mac
        
        value_label.bind("<Button-4>", lambda e: self.wheel_up(var, max_val))
        value_label.bind("<Button-5>", lambda e: self.wheel_down(var, min_val))
        value_label.bind("<MouseWheel>", lambda e: self.mouse_wheel(e, var, min_val, max_val))
        
        # フォーカス設定（ホイールイベントを受け取るため）
        value_frame.bind("<Button-1>", lambda e: value_frame.focus_set())
        value_label.bind("<Button-1>", lambda e: value_frame.focus_set())
        
        # 増減ボタン（タッチデバイス向け）
        button_frame = tk.Frame(value_frame, bg="#ffffff")
        button_frame.pack()
        
        up_button = tk.Button(
            button_frame,
            text="▲",
            font=font.Font(family="Arial", size=10),
            bg="#e0e0e0",
            fg="#333333",
            width=2,
            height=1,
            command=lambda: self.wheel_up(var, max_val)
        )
        up_button.pack(side=tk.LEFT, padx=2)
        
        down_button = tk.Button(
            button_frame,
            text="▼",
            font=font.Font(family="Arial", size=10),
            bg="#e0e0e0",
            fg="#333333",
            width=2,
            height=1,
            command=lambda: self.wheel_down(var, min_val)
        )
        down_button.pack(side=tk.LEFT, padx=2)
        
    def mouse_wheel(self, event, var, min_val, max_val):
        """マウスホイールイベント処理"""
        if not self.timer_running:
            if event.delta > 0:  # 上方向
                self.wheel_up(var, max_val)
            else:  # 下方向
                self.wheel_down(var, min_val)
                
    def wheel_up(self, var, max_val):
        """ホイール上方向（値増加）"""
        if not self.timer_running:
            current = var.get()
            if current < max_val:
                var.set(current + 1)
            else:
                var.set(0)  # 循環
                
    def wheel_down(self, var, min_val):
        """ホイール下方向（値減少）"""
        if not self.timer_running:
            current = var.get()
            if current > min_val:
                var.set(current - 1)
            else:
                # 最大値に循環
                if var == self.hours:
                    var.set(23)
                else:
                    var.set(59)
                    
    def on_time_change(self, *args):
        """時間設定が変更されたときの処理"""
        if not self.timer_running:
            # 秒数を計算
            total_seconds = self.hours.get() * 3600 + self.minutes.get() * 60 + self.seconds.get()
            self.seconds_left = total_seconds
            
            # 表示を更新
            time_str = f"{self.hours.get():02d}:{self.minutes.get():02d}:{self.seconds.get():02d}"
            self.time_display.config(text=time_str)
            
            # ステータス表示を更新
            if total_seconds > 0:
                time_text = self.format_time_message(total_seconds)
                self.status_display.config(text=f"設定時間: {time_text}")
            else:
                self.status_display.config(text="マウスホイールで時間を調整してください")
            
    def create_control_buttons(self):
        control_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=20)
        
        # ボタン用のコンテナを作成して中央に配置
        button_container = tk.Frame(control_frame, bg="#f0f0f0")
        button_container.pack()
        
        # スタートボタン
        self.start_button = tk.Button(
            button_container,
            text="スタート",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            width=10,
            height=2,
            command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=10)
        
        # 一時停止ボタン
        self.pause_button = tk.Button(
            button_container,
            text="一時停止",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=self.pause_timer
        )
        self.pause_button.grid(row=0, column=1, padx=10)
        
        # リセットボタン
        self.reset_button = tk.Button(
            button_container,
            text="リセット",
            font=self.button_font,
            bg="#F44336",
            fg="white",
            width=10,
            height=2,
            command=self.reset_timer
        )
        self.reset_button.grid(row=0, column=2, padx=10)
        
        # 音響テストボタンを追加
        self.sound_test_button = tk.Button(
            button_container,
            text="🔊 音テスト",
            font=self.button_font,
            bg="#9C27B0",
            fg="white",
            width=10,
            height=2,
            command=self.test_sound
        )
        self.sound_test_button.grid(row=1, column=1, padx=10, pady=10)
    
    def on_window_resize(self, event):
        # ウィンドウサイズが変わったときにフォントサイズを調整
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 最小サイズを確保
        if window_width < 400 or window_height < 300:
            return
            
        # ディスプレイフォントのサイズを調整
        display_size = int(min(window_width / 10, window_height / 10))
        display_size = max(24, min(display_size, 60))  # 最小24、最大60
        self.display_font.configure(size=display_size)
        
        # ボタンフォントのサイズを調整
        button_size = int(min(window_width / 40, window_height / 30))
        button_size = max(10, min(button_size, 16))  # 最小10、最大16
        self.button_font.configure(size=button_size)
        
        # 時間フォントのサイズを調整
        time_size = int(min(window_width / 20, window_height / 15))
        time_size = max(20, min(time_size, 40))  # 最小20、最大40
        self.time_font.configure(size=time_size)
        
    def keyboard_input(self, event):
        # タイマーが実行中でなければキーボード入力を処理
        if not self.timer_running:
            if event.keysym == "Return":
                # Enterキーでタイマー開始
                self.start_timer()
            elif event.keysym == "space":
                # スペースキーで一時停止/再開
                if self.timer_running:
                    self.pause_timer()
            elif event.keysym == "r":
                # rキーでリセット
                self.reset_timer()
            # 数字キーで直接時間設定
            elif event.char in "0123456789":
                # フォーカスされている時間単位に応じて値を設定
                pass  # 必要に応じて実装
        elif event.keysym == "Escape":
            # タイマー実行中でもEscapeキーでリセット
            self.reset_timer()
        elif event.keysym == "space":
            # スペースキーで一時停止/再開
            self.pause_timer()
            
    def format_time_message(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        time_parts = []
        if hours > 0:
            time_parts.append(f"{hours}時間")
        if minutes > 0:
            time_parts.append(f"{minutes}分")
        if seconds > 0 or (hours == 0 and minutes == 0):
            time_parts.append(f"{seconds}秒")
            
        return "".join(time_parts)
    
    def start_timer(self):
        if self.timer_paused:
            # 一時停止から再開
            self.timer_paused = False
            self.status_display.config(text="タイマー実行中...")
            self.pause_button.config(text="一時停止")
            print("タイマー再開")
        elif not self.timer_running and self.seconds_left > 0:
            # 新しいタイマー開始
            self.timer_running = True
            self.status_display.config(text="タイマー実行中...")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            
            print(f"タイマー開始: {self.seconds_left}秒")
            
            # タイマー処理をスレッドで実行
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
        else:
            print(f"タイマー開始できません - 実行中: {self.timer_running}, 時間: {self.seconds_left}")
    
    def pause_timer(self):
        if self.timer_running and not self.timer_paused:
            self.timer_paused = True
            self.status_display.config(text="タイマー一時停止中")
            self.pause_button.config(text="再開")
        else:
            self.start_timer()  # 再開処理
    
    def reset_timer(self):
        # タイマーがアクティブな状態だったかチェック（音を鳴らさないため）
        was_running = self.timer_running
        
        self.timer_running = False
        self.timer_paused = False
        self.seconds_left = 0
        
        # 時間設定をリセット
        self.hours.set(0)
        self.minutes.set(0)
        self.seconds.set(0)
        
        self.time_display.config(text="00:00:00")
        self.status_display.config(text="マウスホイールで時間を調整してください")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="一時停止")
    
    def run_timer(self): 
        print("タイマースレッド開始")
        while self.timer_running and self.seconds_left > 0:
            if not self.timer_paused:
                # 1秒待機
                time.sleep(1)
                if self.timer_running:  # 途中でリセットされていないかチェック
                    self.seconds_left -= 1
                    print(f"残り時間: {self.seconds_left}秒")
                    
                    # UIの更新はメインスレッドで行う
                    self.root.after(0, self.update_timer_display)
                    
                    # タイマー終了チェック
                    if self.seconds_left <= 0:
                        print("タイマー完了！timer_complete呼び出し")
                        self.root.after(0, self.timer_complete)
                        return  # ループを抜ける
            else:
                # 一時停止中は短い間隔で状態をチェック
                time.sleep(0.1)
        print("タイマースレッド終了")
    
    def update_timer_display(self):
        hours = self.seconds_left // 3600
        minutes = (self.seconds_left % 3600) // 60
        seconds = self.seconds_left % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_display.config(text=time_str)
    
    def timer_complete(self):
        print("timer_complete呼び出し開始")
        
        # タイマー完了処理
        self.timer_running = False
        self.timer_paused = False
        self.seconds_left = 0
        
        # UI表示を更新
        self.time_display.config(text="00:00:00", fg="#FF0000")  # 赤色で強調
        self.status_display.config(text="🎉 タイマー終了！ 🎉", fg="#FF0000")
        
        # ボタン状態をリセット
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="一時停止")
        
        # 複数の音響手法を試す
        self.play_completion_sound()
        
        # 3秒後に表示色を元に戻す
        self.root.after(3000, lambda: (
            self.time_display.config(fg="#333333"),
            self.status_display.config(text="マウスホイールで時間を調整してください", fg="#666666")
        ))
        
        print("timer_complete処理完了")
        
    def play_completion_sound(self):
        """確実に聞こえる方法で音を鳴らす"""
        print("=== タイマー完了音再生開始 ===")
        
        # 方法3が聞こえることが確認されたので、これをメインにする
        try:
            print("方法3: winsound.PlaySound で音再生")
            # 3回異なるシステム音を鳴らす
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            time.sleep(0.5)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            time.sleep(0.5)
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            print("方法3: 音再生完了 ✅")
            
        except Exception as e:
            print(f"方法3エラー: {e}")
            
            # バックアップとして他の方法も試す
            try:
                print("バックアップ: winsound.MessageBeep")
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                time.sleep(0.3)
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                time.sleep(0.3)
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                print("バックアップ音再生完了 ✅")
            except Exception as e2:
                print(f"バックアップもエラー: {e2}")
                # 最終手段として視覚的通知
                print("🔔🔔🔔 タイマー完了！ 🔔🔔🔔")
        
        print("=== タイマー完了音再生終了 ===")
        
    def test_sound(self):
        """音響テスト用メソッド - 方法3を中心にテスト"""
        print("\n🔊 手動音響テスト開始 🔊")
        
        # 確認された方法3でテスト
        try:
            print("✨ 効果的な音再生方法でテスト中...")
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            time.sleep(0.4)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            time.sleep(0.4)
            winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
            print("✅ 音テスト完了！音が聞こえましたか？")
        except Exception as e:
            print(f"❌ 音テストエラー: {e}")
            print("💡 システム音設定を確認してください")
        
        print("🔊 手動音響テスト完了 🔊\n")

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(400, 300)  # 最小サイズを設定
    app = TimerApp(root)
    root.mainloop()