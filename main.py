#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ruby Heart Chat 应用程序

这是一个基于PyQt5和Gemini API的互动聊天应用，
展示了一个会对用户输入做出反应的可爱心形界面。
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from views.main_window import MainWindow


def setup_resources():
    """确保所需资源目录存在"""
    # 确保sounds目录存在
    sounds_dir = os.path.join("resources", "sounds")
    os.makedirs(sounds_dir, exist_ok=True)
    
    # 添加占位声音文件，如果它们不存在
    sound_files = [
        "poke.wav", "pop.wav", "swoosh.wav", "jiggle.wav",
        "heartbeat_soft.wav", "heartbeat_fast.wav", 
        "message.wav", "click.wav"
    ]
    
    # 为了示例目的，创建空的WAV文件以避免找不到文件的错误
    # 实际应用中，你应该使用真实的声音文件
    for sound_file in sound_files:
        sound_path = os.path.join(sounds_dir, sound_file)
        if not os.path.exists(sound_path):
            try:
                with open(sound_path, 'wb') as f:
                    # 创建一个最小有效的WAV文件头
                    # RIFF标头 (4字节) + 文件大小 (4字节) + WAVE标识 (4字节) +
                    # fmt子块ID (4字节) + 子块大小 (4字节) + 音频格式 (2字节) +
                    # 通道数 (2字节) + 采样率 (4字节) + 字节率 (4字节) +
                    # 块对齐 (2字节) + 位每样本 (2字节) + data子块ID (4字节) +
                    # 数据大小 (4字节) + 0数据点 (0字节)
                    f.write(b'RIFF')
                    f.write((36).to_bytes(4, 'little'))  # 文件大小 (头部大小 + 数据大小)
                    f.write(b'WAVE')
                    f.write(b'fmt ')
                    f.write((16).to_bytes(4, 'little'))  # 子块大小
                    f.write((1).to_bytes(2, 'little'))   # 音频格式 (1 = PCM)
                    f.write((1).to_bytes(2, 'little'))   # 通道数
                    f.write((44100).to_bytes(4, 'little'))  # 采样率
                    f.write((44100 * 1 * 16 // 8).to_bytes(4, 'little'))  # 字节率
                    f.write((1 * 16 // 8).to_bytes(2, 'little'))  # 块对齐
                    f.write((16).to_bytes(2, 'little'))  # 位每样本
                    f.write(b'data')
                    f.write((0).to_bytes(4, 'little'))   # 数据大小
                print(f"Created placeholder sound file: {sound_path}")
            except Exception as e:
                print(f"Warning: Could not create placeholder sound file {sound_path}: {e}")


def main():
    """主函数，创建并启动应用程序"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 确保资源文件存在
    setup_resources()
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()