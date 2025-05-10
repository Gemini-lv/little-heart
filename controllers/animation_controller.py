import random
import time
from PyQt5.QtCore import QObject, QPointF, QTimer, QRectF
from PyQt5.QtGui import QColor

from controllers.sound_controller import SoundController

class AnimationController(QObject):
    """管理心形的各种动画效果"""
    
    def __init__(self, sound_controller: SoundController = None):
        super().__init__()
        self.sound_controller = sound_controller
        self.random_action_timer = QTimer()
        self.random_action_timer.setSingleShot(True)
        
    def connect_heart_widget(self, heart_widget):
        """连接到心形部件
        
        Args:
            heart_widget: 心形部件实例
        """
        self.heart_widget = heart_widget
        self.random_action_timer.timeout.connect(self._execute_random_heart_action)
        self._schedule_random_heart_action()
        
    def _schedule_random_heart_action(self):
        """调度随机心形动画"""
        # 8-15秒内随机执行一次动画
        interval_ms = random.randint(8000, 15000)
        self.random_action_timer.start(interval_ms)
        
    def _execute_random_heart_action(self):
        """执行随机动画操作"""
        if (self.heart_widget.isVisible() and 
                not self.heart_widget._is_any_major_animation_active() and 
                not getattr(self.heart_widget, 'long_dialogue_is_visible_externally', False)):
            
            # 随机选择一种动画效果
            action_type = random.choice(["shiver", "pop", "spin", "glow", "jiggle"])
            
            if action_type == "shiver":
                self.heart_widget.random_action_shiver()
            
            elif action_type == "pop":
                self.heart_widget.random_action_pop()
                if self.sound_controller:
                    self.sound_controller.play_sound("pop")
            
            elif action_type == "spin":
                self.heart_widget.random_action_spin()
                if self.sound_controller:
                    self.sound_controller.play_sound("spin")
            
            elif action_type == "glow":
                self.heart_widget.random_action_glow()
            
            elif action_type == "jiggle":
                self.heart_widget.random_action_jiggle()
                if self.sound_controller:
                    self.sound_controller.play_sound("jiggle", volume=0.4)
        
        # 调度下一次动画
        self._schedule_random_heart_action()
        
    def trigger_poke_animation(self):
        """触发戳一下的动画"""
        self.heart_widget.random_action_jiggle()
        if self.sound_controller:
            self.sound_controller.play_sound("poke")
            
    def emit_mood_particles(self, frequency_hz: float, dialogue: str, color_hex: str):
        """根据情绪生成粒子效果
        
        Args:
            frequency_hz: 频率
            dialogue: 对话文本
            color_hex: 颜色
        """
        if not hasattr(self.heart_widget, 'emit_particles'):
            return
            
        # 根据情绪生成不同的粒子效果
        if frequency_hz > 4.0 and ("开心" in dialogue or "兴奋" in dialogue or "耶" in dialogue):
            self.heart_widget.emit_particles(
                random.randint(7, 15), 
                self.heart_widget.geometry(), 
                QColor(color_hex), 
                "sparkle"
            )
        elif frequency_hz < 1.0 and ("悲伤" in dialogue or "难过" in dialogue or "呜" in dialogue):
            self.heart_widget.emit_particles(
                random.randint(3, 7), 
                self.heart_widget.geometry(), 
                QColor(color_hex), 
                "teardrop"
            )
    
    def stop_animations(self):
        """停止所有动画"""
        if self.random_action_timer.isActive():
            self.random_action_timer.stop()