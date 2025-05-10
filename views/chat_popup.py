from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent

class ChatInputPopup(QLineEdit):
    """聊天输入弹窗，用于用户与Ruby聊天"""
    
    # 当用户提交输入时发出信号
    submitted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置弹窗的窗口标志和外观
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # 设置样式
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 220);
                color: white;
                border: 1px solid rgba(180, 180, 180, 200);
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
            }
        """)
        
        # 设置提示文本和尺寸
        self.setPlaceholderText("Chat with Ruby...")
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.setFixedHeight(45)
        
        # 连接回车信号
        self.returnPressed.connect(self._on_submit)
    
    def _on_submit(self):
        """处理提交操作"""
        text = self.text().strip()
        if text:
            self.submitted.emit(text)
        self.hide()
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """处理失去焦点事件"""
        self.hide()
        super().focusOutEvent(event)
    
    def showEvent(self, event):
        """处理显示事件"""
        super().showEvent(event)
        self.clear()
        self.setFocus(Qt.PopupFocusReason)
        # 增加一个延迟的焦点调用，确保输入正常工作
        QTimer.singleShot(100, self.setFocus)
    
    def hideEvent(self, event):
        """处理隐藏事件"""
        self.clear()
        super().hideEvent(event)