from typing import List, Optional, Dict
import random

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QMenu, QAction, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QColor, QContextMenuEvent

from views.heart_widget import HeartWidget
from views.chat_popup import ChatInputPopup
from controllers.gemini_controller import GeminiController
from controllers.sound_controller import SoundController
from controllers.animation_controller import AnimationController
from models.gemini_models import RubyResponse
from utils.constants import (
    DEFAULT_HEART_COLOR, DEFAULT_PULSE_FREQUENCY, ERROR_HEART_COLOR,
    OUTPUT_HIDE_TIMEOUT_MS, ERROR_HIDE_TIMEOUT_MS
)


class MainWindow(QWidget):
    """主窗口类，负责管理整个应用程序的交互"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化控制器
        self.sound_controller = SoundController()
        self.sound_controller.init_sounds()
        
        self.gemini_controller = GeminiController()
        
        self.animation_controller = AnimationController(self.sound_controller)
        
        # 聊天历史
        self.chat_history: List[Dict[str, str]] = []
        self.current_interaction_context: Optional[str] = None  # 当前交互上下文，用于历史记录
        self.chat_input_popup: Optional[ChatInputPopup] = None
        
        # 初始化UI
        self.init_ui()
        
        # 连接动画控制器到心形部件
        self.animation_controller.connect_heart_widget(self.heart_widget)
        
        # 窗口拖动相关
        self._drag_pos = QPoint()
        
        # 设置心跳声音定时器
        self.heartbeat_sound_timer = QTimer(self)
        self.heartbeat_sound_timer.timeout.connect(self._play_heartbeat_sound)
        self._update_heartbeat_sound_interval(self.heart_widget.current_frequency_hz)
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Ruby Heart Chat")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 减小边距
        layout.setSpacing(8)
        
        # 心形部件
        self.heart_widget = HeartWidget(self)
        self.heart_widget.setFixedSize(280, 230)  # 稍小一些
        self.heart_widget.clicked_on_heart.connect(self._on_heart_clicked)
        self.heart_widget.set_long_dialogue_visibility(False)  # 初始化
        layout.addWidget(self.heart_widget, 0, Qt.AlignHCenter)
        
        # 长对话输出区域
        self.long_dialogue_output_area = QTextEdit(self)
        self.long_dialogue_output_area.setReadOnly(True)
        self.long_dialogue_output_area.setPlaceholderText("Ruby says...")
        self.long_dialogue_output_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(250, 250, 250, 200); /* 更亮、更透明 */
                color: #101010; 
                border: 1px solid rgba(180, 180, 180, 150);
                border-radius: 8px; /* 更圆润 */
                padding: 10px;
                font-size: 14px;
                font-family: sans-serif;
            }
            QTextEdit QScrollBar:vertical {
                border: none; background: rgba(200,200,200,100); width: 8px; margin: 0px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: rgba(120,120,120,150); min-height: 20px; border-radius: 4px;
            }
        """)
        self.long_dialogue_output_area.setVisible(False)
        self.long_dialogue_output_area.setFixedHeight(120)  # 更小的对话框
        layout.addWidget(self.long_dialogue_output_area)
        
        # 输出隐藏定时器
        self.output_hide_timer = QTimer(self)
        self.output_hide_timer.setSingleShot(True)
        self.output_hide_timer.timeout.connect(self._on_dialogue_hide_timeout)
        
        self.setLayout(layout)
        self.resize(320, 400)  # 调整总体大小
        self.center_window()
        
        # 设置初始状态
        self.heart_widget.set_heart_color(DEFAULT_HEART_COLOR)
        self.heart_widget.set_pulsation(DEFAULT_PULSE_FREQUENCY)
        self.heart_widget.set_display_text("Ruby...")
    
    def _on_heart_clicked(self):
        """处理点击心形的事件"""
        self.sound_controller.play_sound("ui_click", volume=0.5)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """处理右键菜单事件"""
        self.sound_controller.play_sound("ui_click", volume=0.3)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: rgba(50,50,50,230); color: white; border: 1px solid #555; border-radius: 5px; }
            QMenu::item { padding: 6px 20px 6px 20px; }
            QMenu::item:selected { background-color: #E81123; } /* 选择时的强调色 */
            QMenu::separator { height: 1px; background: #777; margin-left: 10px; margin-right: 5px; }
        """)
        
        chat_action = menu.addAction("Chat with Ruby")
        poke_action = menu.addAction("Poke Ruby")
        ask_mood_action = menu.addAction("Ask Ruby's Mood")
        menu.addSeparator()
        
        sound_toggle_action = menu.addAction(
            "Toggle Sounds (On)" if self.sound_controller.are_sounds_enabled() else "Toggle Sounds (Off)"
        )
        menu.addSeparator()
        quit_action = menu.addAction("Quit Ruby")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == chat_action:
            self.prompt_chat_input(self.mapToGlobal(event.pos()))
        elif action == poke_action:
            self.trigger_poke_ruby()
        elif action == ask_mood_action:
            self.trigger_ask_ruby_mood()
        elif action == sound_toggle_action:
            new_state = not self.sound_controller.are_sounds_enabled()
            self.sound_controller.enable_sounds(new_state)
            if not new_state:
                self.heartbeat_sound_timer.stop()
            else:
                self._update_heartbeat_sound_interval(self.heart_widget.current_frequency_hz)
        elif action == quit_action:
            self.close()
    
    def prompt_chat_input(self, position: QPoint):
        """显示聊天输入弹窗
        
        Args:
            position: 弹窗显示位置
        """
        if self.long_dialogue_output_area.isVisible():
            self._on_dialogue_hide_timeout()
        
        if self.chat_input_popup and self.chat_input_popup.isVisible():
            self.chat_input_popup.hide()  # 如果已经打开，先隐藏，然后重新创建/定位
        
        # 确保如果存在旧弹窗则删除它
        if self.chat_input_popup:
            self.chat_input_popup.deleteLater()
        
        self.chat_input_popup = ChatInputPopup(None)  # 无父窗口以获得顶层窗口效果
        self.chat_input_popup.submitted.connect(self._handle_chat_popup_submission)
        
        # 相对于主窗口或点击位置，让弹窗居中
        popup_width = self.chat_input_popup.width()
        popup_height = self.chat_input_popup.height()
        
        # 尝试将其放在主窗口下方或点击位置附近
        target_x = self.x() + (self.width() - popup_width) / 2
        target_y = self.y() + self.height() + 5  # 在主窗口下方
        
        # 确保弹窗在屏幕范围内
        screen_geo = QApplication.primaryScreen().availableGeometry()
        if target_y + popup_height > screen_geo.bottom():  # 如果太低，则放在上方
            target_y = self.y() - popup_height - 5
        if target_x < screen_geo.x():
            target_x = screen_geo.x()
        if target_x + popup_width > screen_geo.right():
            target_x = screen_geo.right() - popup_width
        
        self.chat_input_popup.move(int(target_x), int(target_y))
        self.chat_input_popup.show()
        self.chat_input_popup.activateWindow()
        self.chat_input_popup.raise_()
    
    def _handle_chat_popup_submission(self, text: str):
        """处理聊天输入弹窗的提交
        
        Args:
            text: 用户输入的文本
        """
        if self.chat_input_popup:
            self.chat_input_popup.hide()
        self.send_gemini_message(text, "chat")
    
    def trigger_poke_ruby(self):
        """触发戳Ruby的动作"""
        self.animation_controller.trigger_poke_animation()
        self.send_gemini_message("User poked you!", "poke_reaction", "[Action: Poked Ruby]")
    
    def trigger_ask_ruby_mood(self):
        """触发询问Ruby心情的动作"""
        self.send_gemini_message("User wants to know your mood.", "mood_query", "[Query: How are you feeling?]")
    
    def _on_dialogue_hide_timeout(self):
        """隐藏对话框的超时处理"""
        self.long_dialogue_output_area.setVisible(False)
        self.heart_widget.set_long_dialogue_visibility(False)
        if self.chat_input_popup and self.chat_input_popup.isVisible():
            self.chat_input_popup.hide()
        
        if not self.long_dialogue_output_area.isVisible():
            self.heart_widget.set_heart_color(DEFAULT_HEART_COLOR)
            self.heart_widget.set_display_text("Ruby...")
            self.heart_widget.set_pulsation(DEFAULT_PULSE_FREQUENCY)
    
    def center_window(self):
        """将窗口居中显示在屏幕上"""
        try:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
        except AttributeError:
            screen_geometry = QApplication.desktop().screenGeometry()  # 后备
        
        self.move(
            int((screen_geometry.width() - self.width()) / 2),
            int((screen_geometry.height() - self.height()) / 2)
        )
    
    def send_gemini_message(self, user_text_or_action: str, interaction_type: str, history_user_entry: Optional[str] = None):
        """发送消息到Gemini API
        
        Args:
            user_text_or_action: 用户文本或动作
            interaction_type: 交互类型 (chat/poke_reaction/mood_query)
            history_user_entry: 历史记录中的用户条目，可选
        """
        if not user_text_or_action:
            return
        
        if self.chat_input_popup and self.chat_input_popup.isVisible():
            self.chat_input_popup.hide()
        
        self.current_interaction_context = history_user_entry if history_user_entry else user_text_or_action
        self.heart_widget.set_display_text("...")  # 思考中...
        
        # 构建提示并发送到Gemini API
        full_prompt = self.gemini_controller.build_gemini_prompt(
            user_text_or_action, interaction_type, self.chat_history
        )
        
        self.gemini_controller.send_message(
            full_prompt, self.handle_gemini_response, self.handle_gemini_error
        )
    
    def handle_gemini_response(self, ruby_data: RubyResponse):
        """处理Gemini API的成功响应
        
        Args:
            ruby_data: Ruby响应数据
        """
        # 播放接收消息的声音
        self.sound_controller.play_sound("message_receive", volume=0.7)
        
        # 更新心形部件
        self.heart_widget.set_display_text(ruby_data.short_dialogue)
        self.heart_widget.set_heart_color(ruby_data.color_hex)
        self.heart_widget.set_pulsation(ruby_data.frequency_hz)
        
        # 更新心跳声音
        self._update_heartbeat_sound_interval(ruby_data.frequency_hz)
        
        # 根据情绪生成粒子效果
        self.animation_controller.emit_mood_particles(
            ruby_data.frequency_hz, 
            ruby_data.long_dialogue, 
            ruby_data.color_hex
        )
        
        # 显示长对话文本
        self.long_dialogue_output_area.setText(f"{ruby_data.long_dialogue}")
        self.long_dialogue_output_area.setVisible(True)
        self.heart_widget.set_long_dialogue_visibility(True)
        
        # 确保文本框滚动到底部
        QTimer.singleShot(0, lambda: self.long_dialogue_output_area.verticalScrollBar().setValue(
            self.long_dialogue_output_area.verticalScrollBar().maximum()
        ))
        
        # 设置隐藏定时器
        self.output_hide_timer.stop()
        self.output_hide_timer.start(OUTPUT_HIDE_TIMEOUT_MS)
        
        # 更新聊天历史
        if self.current_interaction_context:
            self.chat_history.append({
                "user": self.current_interaction_context,
                "ruby": ruby_data.long_dialogue
            })
            self.current_interaction_context = None
            
            # 限制历史记录长度
            max_history_exchanges = 6
            if len(self.chat_history) > max_history_exchanges:
                self.chat_history = self.chat_history[-max_history_exchanges:]
    
    def handle_gemini_error(self, error_message: str):
        """处理Gemini API的错误响应
        
        Args:
            error_message: 错误消息
        """
        self.heart_widget.set_display_text("Error!")
        self.heart_widget.set_heart_color(ERROR_HEART_COLOR)
        self.heart_widget.set_pulsation(0.5)
        self._update_heartbeat_sound_interval(0.5)
        
        self.long_dialogue_output_area.setText(
            f"Ruby Error: {error_message}\n(Check console for more details and ensure API key is correct)"
        )
        self.long_dialogue_output_area.setVisible(True)
        self.heart_widget.set_long_dialogue_visibility(True)
        
        QTimer.singleShot(0, lambda: self.long_dialogue_output_area.verticalScrollBar().setValue(
            self.long_dialogue_output_area.verticalScrollBar().maximum()
        ))
        
        self.output_hide_timer.stop()
        self.output_hide_timer.start(ERROR_HIDE_TIMEOUT_MS)  # 错误显示时间更长
        self.current_interaction_context = None
    
    def _play_heartbeat_sound(self):
        """播放心跳声音"""
        freq = self.heart_widget.current_frequency_hz
        if freq < 1.5:
            self.sound_controller.play_sound("heartbeat_soft", volume=0.3 + (freq * 0.1))
        else:
            self.sound_controller.play_sound("heartbeat_fast", volume=0.4 + (freq * 0.08))
        self._update_heartbeat_sound_interval(freq)
    
    def _update_heartbeat_sound_interval(self, frequency_hz: float):
        """更新心跳声音的间隔
        
        Args:
            frequency_hz: 频率 (Hz)
        """
        if frequency_hz <= 0:
            self.heartbeat_sound_timer.stop()
            return
        
        interval_ms = int(1000 / frequency_hz)
        self.heartbeat_sound_timer.start(max(150, interval_ms))  # 最小间隔
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        if event.button() == Qt.LeftButton:
            # 如果点击在弹窗外，隐藏弹窗
            if self.chat_input_popup and self.chat_input_popup.isVisible():
                popup_global_rect = self.chat_input_popup.frameGeometry()
                popup_global_rect.moveTopLeft(self.chat_input_popup.mapToGlobal(QPoint(0, 0)))
                if not popup_global_rect.contains(event.globalPos()):
                    self.chat_input_popup.hide()
            
            # 设置拖动位置
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件处理"""
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        self._drag_pos = QPoint()
        event.accept()
    
    def changeEvent(self, event: QEvent):
        """窗口状态变化事件处理"""
        super().changeEvent(event)
        
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.heart_widget.set_display_text("Zzz...")
                if self.sound_controller.are_sounds_enabled():
                    self.heartbeat_sound_timer.stop()
            elif self.windowState() == Qt.WindowNoState or self.windowState() == Qt.WindowActive:  # 恢复或聚焦
                # 根据对话框是否可见来恢复
                if not self.long_dialogue_output_area.isVisible():
                    self.heart_widget.set_display_text("Ruby...")
                # 否则保持当前Gemini文本
                if self.sound_controller.are_sounds_enabled():
                    self._update_heartbeat_sound_interval(self.heart_widget.current_frequency_hz)
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        print("Closing Ruby application...")
        # 停止所有定时器
        self.output_hide_timer.stop()
        self.heartbeat_sound_timer.stop()
        
        # 停止心形部件的定时器
        if self.heart_widget:
            self.heart_widget.pulsation_timer.stop()
            self.heart_widget.color_change_timer.stop()
            self.heart_widget.particle_timer.stop()
        
        # 停止动画控制器
        self.animation_controller.stop_animations()
        
        # 关闭聊天弹窗
        if self.chat_input_popup:
            self.chat_input_popup.close()
        
        # 等待线程结束
        if hasattr(self.gemini_controller, 'threadpool'):
            self.gemini_controller.threadpool.clear()  # 删除未开始的任务
            if not self.gemini_controller.threadpool.waitForDone(2000):  # 等待最多2秒
                print("Warning: Some threads did not finish in time.")
        
        super().closeEvent(event)
        self.deleteLater()  # 确保适当清理