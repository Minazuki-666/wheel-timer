import tkinter as tk
from tkinter import font, ttk
import time
import threading
import winsound  # Windowsでの音声通知用
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
        
    def create_keypad(self):
        keypad_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        keypad_frame.pack(fill=tk.BOTH, expand=True)
        
        # フレーム内でキーパッドを中央に配置
        keypad_inner_frame = tk.Frame(keypad_frame, bg="#f0f0f0")
        keypad_inner_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # キーパッド配置（電卓風の配置）- 00ボタン追加
        keypad_buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('00', 3, 1), ('⌫', 3, 2),
            ('C', 4, 1)
        ]
        
        self.keypad_button_widgets = []  # ボタンウィジェットを保存するリスト
        
        for (text, row, col) in keypad_buttons:
            button = tk.Button(
                keypad_inner_frame,
                text=text,
                font=self.keypad_font,
                width=5,
                height=2,
                bg="#ffffff",
                fg="#333333",
                relief=tk.RAISED,
                command=lambda t=text: self.keypad_press(t)
            )
            button.grid(row=row, column=col, padx=5, pady=5)
            self.keypad_button_widgets.append(button)
            
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
    
    def on_window_resize(self, event):
        # ウィンドウサイズが変わったときにフォントサイズを調整
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 最小サイズを確保
        if window_width < 300 or window_height < 450:
            return
            
        # ディスプレイフォントのサイズを調整
        display_size = int(min(window_width / 10, window_height / 15))
        display_size = max(24, min(display_size, 60))  # 最小24、最大60
        self.display_font.configure(size=display_size)
        
        # ボタンフォントのサイズを調整
        button_size = int(min(window_width / 40, window_height / 50))
        button_size = max(10, min(button_size, 16))  # 最小10、最大16
        self.button_font.configure(size=button_size)
        
        # キーパッドフォントのサイズを調整
        keypad_size = int(min(window_width / 25, window_height / 30))
        keypad_size = max(14, min(keypad_size, 22))  # 最小14、最大22
        self.keypad_font.configure(size=keypad_size)
        
    def keyboard_input(self, event):
        # タイマーが実行中でなければキーボード入力を処理
        if not self.timer_running:
            key = event.char
            if key in "0123456789":
                # 数字キーの処理
                self.keypad_press(key)
            elif event.keysym == "BackSpace":
                # バックスペースキーの処理
                self.keypad_press("⌫")
            elif event.keysym == "Delete" or event.keysym == "Escape":
                # Delete/Escキーでクリア
                self.keypad_press("C")
            elif event.keysym == "Return":
                # Enterキーでタイマー開始
                self.start_timer()
            elif event.keysym == "space":
                # スペースキーで一時停止/再開
                if self.timer_running:
                    self.pause_timer()
        elif event.keysym == "Escape":
            # タイマー実行中でもEscapeキーでリセット
            self.reset_timer()
            
    def keypad_press(self, key):
        if not self.timer_running:
            if key == "C":
                # クリア
                self.input_value = ""
                self.update_display()
            elif key == "⌫":
                # バックスペース
                self.input_value = self.input_value[:-1]
                self.update_display()
            elif key == "00":
                # 00キーの処理
                if len(self.input_value) <= 4:  # 最大6桁まで（hhmmss）
                    self.input_value += "00"
                    self.update_display()
            elif len(self.input_value) < 6:  # 最大6桁まで（hhmmss）
                # 数字が押された
                self.input_value += key
                self.update_display()
    
    def update_display(self):
        if self.input_value == "":
            # 入力がない場合
            self.time_display.config(text="00:00:00")
            self.input_display.config(text="時間を入力してください")
            return
            
        # 入力値から時間フォーマットに変換
        padded = self.input_value.zfill(6)
        hours = padded[0:2]
        minutes = padded[2:4]
        seconds = padded[4:6]
        
        self.time_display.config(text=f"{hours}:{minutes}:{seconds}")
        
        # 入力時間を秒数に変換
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        self.seconds_left = total_seconds
        
        # 入力状態メッセージ
        time_text = self.format_time_message(total_seconds)
        self.input_display.config(text=f"入力: {time_text}")
    
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
            self.input_display.config(text="タイマー実行中...")
            self.pause_button.config(text="一時停止")
        elif not self.timer_running and self.seconds_left > 0:
            # 新しいタイマー開始
            self.timer_running = True
            self.input_display.config(text="タイマー実行中...")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            
            # タイマー処理をスレッドで実行
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self):
        if self.timer_running and not self.timer_paused:
            self.timer_paused = True
            self.input_display.config(text="タイマー一時停止中")
            self.pause_button.config(text="再開")
        else:
            self.start_timer()  # 再開処理
    
    def reset_timer(self):
        # タイマーがアクティブな状態だったかチェック（音を鳴らさないため）
        was_running = self.timer_running
        
        self.timer_running = False
        self.timer_paused = False
        self.seconds_left = 0
        self.input_value = ""
        self.time_display.config(text="00:00:00")
        self.input_display.config(text="時間を入力してください")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        # 音を鳴らす処理は削除（タイマー完了時のみ鳴るように）
    
    def run_timer(self):
        while self.timer_running and self.seconds_left > 0:
            if not self.timer_paused:
                # 1秒待機
                time.sleep(1)
                self.seconds_left -= 1
                
                # UIの更新はメインスレッドで行う
                self.root.after(0, self.update_timer_display)
                
                # タイマー終了
                if self.seconds_left <= 0:
                    self.root.after(0, self.timer_complete)
                    break
    
    def update_timer_display(self):
        hours = self.seconds_left // 3600
        minutes = (self.seconds_left % 3600) // 60
        seconds = self.seconds_left % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_display.config(text=time_str)
    
    def timer_complete(self):
        self.time_display.config(text="00:00:00")
        self.input_display.config(text="タイマー終了！")
        self.timer_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
        # 通知音を鳴らす（タイマー完了時のみ）
        winsound.Beep(440, 1000)  # 440Hzで1秒間
        
        # # Windows通知を表示
        # self.toaster.show_toast(
        #     "タイマー終了",
        #     "設定したタイマーが完了しました。",
        #     icon_path=None,
        #     duration=5,
        #     threaded=True
        # )

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(300, 450)  # 最小サイズを設定
    app = TimerApp(root)
    root.mainloop()