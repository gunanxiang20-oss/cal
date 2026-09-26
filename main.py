from kivy.app import App
from kivy.uix.label import Label

class CalendarApp(App):
    def build(self):
        return Label(text="日历工具箱测试成功！")

if __name__ == '__main__':
    CalendarApp().run()

#!/usr/bin/env python3
"""
日历工具箱 APK 包装器
启动时执行同目录下的 calendar.sh，将输出显示在终端风格界面中。
"""

import os
import subprocess
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp

# 让 APK 中的工作目录指向应用数据目录
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(APP_DIR, "calendar.sh")


class CalToolboxApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        # 标题
        title = Label(
            text="[b]📅  日历工具箱[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(36),
            color=(0.3, 0.9, 1, 1),
        )
        root.add_widget(title)

        # 输出显示区
        self.output = Label(
            text="正在启动...",
            halign="left",
            valign="top",
            size_hint_y=None,
            font_size=dp(11),
            color=(0.85, 0.9, 0.95, 1),
        )
        self.output.bind(
            width=lambda *x: setattr(self.output, "text_size", (self.output.width, None))
        )

        scroll = ScrollView()
        scroll.add_widget(self.output)
        root.add_widget(scroll)

        # 按钮行
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))

        self.btn_run = Button(text="启动工具箱", background_color=(0.15, 0.5, 0.8, 1))
        self.btn_run.bind(on_release=self.run_script)

        btn_clear = Button(text="清屏", background_color=(0.3, 0.3, 0.35, 1))
        btn_clear.bind(on_release=lambda *x: setattr(self.output, "text", ""))

        btn_row.add_widget(self.btn_run)
        btn_row.add_widget(btn_clear)
        root.add_widget(btn_row)

        # 启动时自动执行一次
        Clock.schedule_once(lambda dt: self.run_script(), 0.5)

        return root

    def run_script(self, *args):
        """在后台线程执行 bash 脚本，避免阻塞 UI。"""
        self.btn_run.disabled = True
        self.output.text = "正在执行 calendar.sh ...\n"

        def worker():
            try:
                # 确保脚本有执行权限
                os.chmod(SCRIPT_PATH, 0o755)

                proc = subprocess.run(
                    ["bash", SCRIPT_PATH],
                    cwd=APP_DIR,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                out = proc.stdout or ""
                err = proc.stderr or ""
                if err:
                    out += "\n[stderr]\n" + err
                if not out.strip():
                    out = "(脚本执行完毕，无输出)"
            except subprocess.TimeoutExpired:
                out = "脚本执行超时（60秒）。calendar.sh 中可能存在需要交互输入的命令。"
            except Exception as e:
                out = f"执行出错：{e}"

            # 回到主线程更新 UI
            Clock.schedule_once(lambda dt: self._update(out), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _update(self, text):
        self.output.text = text
        self.btn_run.disabled = False


if __name__ == "__main__":
    CalToolboxApp().run()

