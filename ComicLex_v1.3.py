import pyperclip
from pynput import keyboard, mouse
from pynput.keyboard import Key
from pynput.mouse import Listener as MouseListener
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time

def parse_clipboard_content_lines(content):
    text_boxes = []
    current = []
    for line in content.split('\n'):
        stripped_line = line.strip()
        if not stripped_line:
            if current:
                text_boxes.append('\n'.join(current))
                current = []
        else:
            current.append(line.rstrip('\n'))
    if current:
        text_boxes.append('\n'.join(current))
    return text_boxes

def parse_clipboard_content_oneline(content):
    text_boxes = []
    for line in content.split('\n'):
        stripped_line = line.strip()
        if stripped_line:
            text_boxes.append(stripped_line)
    return text_boxes

content = pyperclip.paste()
if not content:
    messagebox.showwarning("警告", "剪贴板为空，请复制一些文本后重试。")
    content = "默认文本"  # 或者设置一个默认值

# 弹出一个对话框让用户选择
if messagebox.askyesno("切词模式选择", "是否以单行模式切词？"):    
    text_boxes = parse_clipboard_content_oneline(content)
else:
    text_boxes = parse_clipboard_content_lines(content)

root = tk.Tk()
root.title("切词打标工具v1.3")
root.geometry("480x650")  # 调整窗口高度以容纳提示文字
root.attributes('-topmost', True)

current_text = tk.Text(root, wrap='word', width=30, height=5)
current_text.pack(pady=10)
current_text.config(state='disabled')

next_text = tk.Text(root, wrap='word', width=30, height=4)
next_text.pack(pady=10)
next_text.config(state='disabled')

current_index_var = tk.IntVar(value=0)

# 创建悬浮窗口
floating_window = tk.Toplevel(root)
floating_window.overrideredirect(True)  # 去掉窗口边框
floating_window.attributes('-alpha', 0.8)  # 设置透明度
floating_window.attributes('-topmost', True)  # 设置悬浮窗口始终置顶
floating_label = tk.Label(floating_window, text="", bg="white", wraplength=200, justify="left")
floating_label.pack()

# 鼠标点击监听相关
mouse_listener = None
is_listening = False
def update_floating_window():
    """更新悬浮窗口内容和位置"""
    if not text_boxes:
        floating_label.config(text="")
        return

    current_index = current_index_var.get()
    if current_index < len(text_boxes) and is_listening == False:
        next_content = text_boxes[current_index+1]
        floating_label.config(text=next_content)
    elif current_index < len(text_boxes) and is_listening == True:
        current_content = text_boxes[current_index]
        floating_label.config(text=current_content)
    else:
        floating_label.config(text="")

    # 获取鼠标位置并更新悬浮窗口位置
    mouse_x, mouse_y = pyautogui.position()
    floating_window.geometry(f"+{mouse_x + 10}+{mouse_y + 10}")  # 悬浮窗口在鼠标右下方

def update_display():
    if not text_boxes:
        current_text.config(state='normal')
        current_text.delete('1.0', tk.END)
        current_text.config(state='disabled')
        
        next_text.config(state='normal')
        next_text.delete('1.0', tk.END)
        next_text.config(state='disabled')
        return
    
    current_index = current_index_var.get()
    if current_index < 0 or current_index >= len(text_boxes):
        current_text.config(state='normal')
        current_text.delete('1.0', tk.END)
        current_text.config(state='disabled')
        
        next_text.config(state='normal')
        next_text.delete('1.0', tk.END)
        next_text.config(state='disabled')
        return
    
    current_content = text_boxes[current_index]
    current_text.config(state='normal')
    current_text.delete('1.0', tk.END)
    current_text.insert(tk.END, current_content)
    current_text.config(state='disabled')
    
    if current_index + 1 < len(text_boxes):
        next_content = text_boxes[current_index + 1]
        next_text.config(state='normal')
        next_text.delete('1.0', tk.END)
        next_text.insert(tk.END, next_content)
        next_text.config(state='disabled')
    else:
        next_text.config(state='normal')
        next_text.delete('1.0', tk.END)
        next_text.config(state='disabled')

    update_floating_window()

update_display()

def on_go(event):
    current_index = current_index_var.get()
    if current_index < len(text_boxes) - 1:
        current_index += 1
        current_index_var.set(current_index)
        pyperclip.copy(text_boxes[current_index].rstrip('\n'))
        update_display()

def on_back(event):
    current_index = current_index_var.get()
    if current_index > 0:
        current_index -= 1
        current_index_var.set(current_index)
        pyperclip.copy(text_boxes[current_index].rstrip('\n'))
        update_display()

def handle_key(key):
    # 检测 Ctrl 键是否按下
    if key == Key.ctrl_l or key == Key.ctrl_r:
        # 记录 Ctrl 键按下状态
        handle_key.ctrl_pressed = True
    elif key == Key.f7 and hasattr(handle_key, 'ctrl_pressed') and handle_key.ctrl_pressed:
        # 检测 Ctrl + F7 组合键
        start_stop_listening()
        # 重置 Ctrl 键状态
        handle_key.ctrl_pressed = False
    elif key == Key.insert:
        on_go(None)
    elif key == Key.delete:
        on_back(None)
    else:
        # 如果按下其他键，重置 Ctrl 键状态
        handle_key.ctrl_pressed = False

keyboard_listener = keyboard.Listener(on_press=handle_key)
keyboard_listener.start()

def on_click(x, y, button, pressed):
    if pressed and is_listening and button == mouse.Button.left:
        wait_time = wait_time_var.get()  # 获取滑块设置的等待时间
        time.sleep(wait_time)  # 使用滑块设置的等待时间
        pyautogui.hotkey('ctrl', 'v')  # 粘贴当前文本
        time.sleep(0.1)  # 等待
        pyautogui.hotkey('ctrl', 'enter')  # 提交修改
        on_go(None)  # 翻到下一句
    if not pressed and is_listening and button == mouse.Button.right:
        # 右键点击时返回上一句
        on_back(None)

def start_stop_listening():
    global is_listening, mouse_listener
    if is_listening:
        is_listening = False
        if mouse_listener:
            mouse_listener.stop()
        listen_button.config(text="开启鼠标连点")
        status_label.config(text="鼠标监听已停止。\n按 Ctrl+F7 启动监听。")
    else:
        is_listening = True
        mouse_listener = MouseListener(on_click=on_click)
        mouse_listener.start()
        listen_button.config(text="停止监听鼠标点击")
        status_label.config(text="鼠标监听已启动\n按 Ctrl+F7 停止监听。")

# 添加监听按钮
listen_button = tk.Button(root, text="鼠标连点模式", command=start_stop_listening)
listen_button.pack(pady=10)

# 添加状态提示文字
tip_label = tk.Label(root, text="上一句Delete,下一句Insert。", fg="red")
tip_label.pack(pady=1)
status_label = tk.Label(root, text="鼠标监听已停止。\n按 Ctrl+F7 启动监听。", fg="blue")
status_label.pack(pady=1)
wait_time_var = tk.DoubleVar(value=1)  
time_label = tk.Label(root, text="连点模式下LP中打标1s，\n在Acrobat中打标1.5s。\n手动模式下取决于手速。", fg="green")
time_label.pack(pady=1)

# 添加滑块控件
wait_time_slider = tk.Scale(root, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, 
                            label="等待时间 (秒)", variable=wait_time_var)
wait_time_slider.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", lambda: (keyboard_listener.stop(), root.destroy()))

# 定时更新悬浮窗口位置
def periodic_update():
    update_floating_window()
    root.after(100, periodic_update)

periodic_update()

root.mainloop()