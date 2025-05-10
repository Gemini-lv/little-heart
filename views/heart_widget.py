import math
import random
import time
from typing import List, Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QTextOption
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal

from utils.constants import (
    HEART_PIXEL_MATRIX, HEART_MATRIX_HEIGHT, HEART_MATRIX_WIDTH,
    DEFAULT_HEART_COLOR, PARTICLE_UPDATE_INTERVAL_MS,
    COLOR_TRANSITION_STEPS, PULSATION_TIMER_INTERVAL_MS,
    QUICK_RESPONSES
)
from utils.particles import Particle


class HeartWidget(QWidget):
    """心形小部件，负责绘制并管理交互式心形"""
    
    # 当点击心形时发出信号
    clicked_on_heart = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)  # 心形的最小尺寸
        self.setMouseTracking(True)  # 启用鼠标跟踪以支持悬停效果

        # 基本属性
        self.scale_factor = 1.0
        self.angle = 0  # 用于脉动
        self.target_frequency_hz = 1.0
        self.current_frequency_hz = 1.0
        self._pulsation_timer_interval_ms = PULSATION_TIMER_INTERVAL_MS
        
        # 颜色设置
        self.base_color = QColor(DEFAULT_HEART_COLOR)
        self.highlight_color = self._derive_highlight_color(self.base_color)
        self.shadow_color = self._derive_shadow_color(self.base_color)
        self.target_base_color = QColor(self.base_color)
        self.color_transition_steps = COLOR_TRANSITION_STEPS
        self.current_color_step = 0
        
        # 显示文本
        self.display_text = "Ruby..."
        self.setAutoFillBackground(False)  # 对透明很重要
        self.long_dialogue_is_visible_externally = False

        # 定时器初始化
        self.pulsation_timer = QTimer(self)
        self.pulsation_timer.timeout.connect(self.update_pulsation)
        self.pulsation_timer.start(self._pulsation_timer_interval_ms)
        
        self.color_change_timer = QTimer(self)
        self.color_change_timer.timeout.connect(self.update_color_transition)

        # 动画状态
        self.shiver_active_until = 0.0
        self.shiver_intensity_factor = 0.0
        self.shiver_total_duration = 0.0

        self.pop_active_until = 0.0
        self.initial_pop_bonus = 0.15
        self.total_pop_duration_for_calc = 0.0

        self.spin_active_until = 0.0
        self.current_spin_angle = 0.0
        self.spin_total_duration = 0.0
        self.spin_target_angle = 360.0

        self.glow_active_until = 0.0
        self.glow_intensity = 0.0  # 0 to 1
        self.glow_total_duration = 0.0

        self.jiggle_active_until = 0.0
        self.jiggle_offset = QPointF(0, 0)
        self.jiggle_total_duration = 0.0
        self.jiggle_magnitude = 5.0  # pixels

        self.pressed_active_until = 0.0
        self.pressed_scale_factor = 0.90  # 按下时缩小

        # 悬停效果
        self.hover_scale_bonus = 0.0  # 添加到scale_factor
        self.is_hovering = False

        # 粒子效果
        self.particles: List[Particle] = []
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self._update_particles)
        self.particle_timer.start(PARTICLE_UPDATE_INTERVAL_MS)  # ~60 FPS for particles

    def _derive_highlight_color(self, color: QColor) -> QColor:
        """根据基色派生高光颜色"""
        h, s, v, a = color.getHsv()
        return QColor.fromHsv(h, max(0, s - 50), min(255, v + 70), a)

    def _derive_shadow_color(self, color: QColor) -> QColor:
        """根据基色派生阴影颜色"""
        h, s, v, a = color.getHsv()
        return QColor.fromHsv(h, min(255, s + 20), max(0, v - 50), a)

    def _update_particles(self):
        """更新粒子状态"""
        self.particles = [p for p in self.particles if p.update(self.particle_timer.interval())]
        if self.particles:  # 仅当有粒子时更新
            self.update()
            
    def emit_particles(self, count: int, origin_rect: QRectF, base_mood_color: QColor, particle_type: str = "sparkle"):
        """发射粒子效果
        
        Args:
            count: 粒子数量
            origin_rect: 起源矩形
            base_mood_color: 基础颜色
            particle_type: 粒子类型 (sparkle/teardrop)
        """
        for _ in range(count):
            start_x = origin_rect.center().x() + random.uniform(-origin_rect.width()*0.2, origin_rect.width()*0.2)
            start_y = origin_rect.center().y() + random.uniform(-origin_rect.height()*0.2, origin_rect.height()*0.2)
            
            if particle_type == "sparkle":
                vel_x = random.uniform(-30, 30) 
                vel_y = random.uniform(-50, -10)  # 向上
                life_ms = random.randint(500, 1500)
                s_color = QColor(base_mood_color)
                s_color.setAlpha(255)
                e_color = QColor(base_mood_color)
                e_color.setAlpha(0)
                s_size = random.uniform(2, 5)
                e_size = 0.5
            elif particle_type == "teardrop":
                vel_x = random.uniform(-10, 10)
                vel_y = random.uniform(20, 60)  # 向下
                life_ms = random.randint(800, 2000)
                s_color = QColor(0, 100, 255, 200)  # 蓝色
                e_color = QColor(0, 100, 255, 0)
                s_size = random.uniform(3, 6)
                e_size = 1
            else:  # 默认
                vel_x = random.uniform(-20, 20)
                vel_y = random.uniform(-20, 20)
                life_ms = random.randint(500, 1000)
                s_color = QColor(base_mood_color)
                s_color.setAlpha(200)
                e_color = QColor(base_mood_color)
                e_color.setAlpha(0)
                s_size = 3
                e_size = 0
            
            self.particles.append(Particle(
                QPointF(start_x, start_y), 
                QPointF(vel_x, vel_y), 
                life_ms, s_color, e_color, 
                s_size, e_size
            ))

    def paintEvent(self, event):
        """绘制心形和粒子效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if not HEART_MATRIX_WIDTH or not HEART_MATRIX_HEIGHT:
            return

        widget_w, widget_h = self.width(), self.height()
        current_time = time.time()

        # --- 处理活动动画 ---
        # 弹跳效果
        current_pop_bonus = 0.0
        if current_time < self.pop_active_until:
            remaining_pop_time = self.pop_active_until - current_time
            if self.total_pop_duration_for_calc > 0:
                current_pop_bonus = self.initial_pop_bonus * (remaining_pop_time / self.total_pop_duration_for_calc)
        else: 
            self.pop_active_until = 0
        
        # 按下效果
        current_pressed_scale = 1.0
        if current_time < self.pressed_active_until:
            current_pressed_scale = self.pressed_scale_factor
        else: 
            self.pressed_active_until = 0

        # 发光效果
        current_glow_intensity = 0.0
        if current_time < self.glow_active_until:
            progress = 1.0 - (self.glow_active_until - current_time) / self.glow_total_duration
            # 使用正弦波实现平滑的发光效果
            current_glow_intensity = self.glow_intensity * math.sin(progress * math.pi) 
        else: 
            self.glow_active_until = 0

        # 有效缩放比例: 脉动 + 弹跳 + 悬停 + 按下 + 发光
        effective_scale_factor = (self.scale_factor + current_pop_bonus + 
                                 self.hover_scale_bonus + 
                                 current_glow_intensity * 0.1) * current_pressed_scale
        
        pixel_w_float = (widget_w * 0.8 * effective_scale_factor) / HEART_MATRIX_WIDTH
        pixel_h_float = (widget_h * 0.8 * effective_scale_factor) / HEART_MATRIX_HEIGHT
        pixel_size = int(min(pixel_w_float, pixel_h_float))
        if pixel_size < 1: 
            pixel_size = 1

        heart_draw_width = HEART_MATRIX_WIDTH * pixel_size
        heart_draw_height = HEART_MATRIX_HEIGHT * pixel_size
        
        # 计算中心点并应用变换
        center_x, center_y = widget_w / 2, widget_h / 2
        
        painter.save()
        painter.translate(center_x, center_y)  # 移动原点到中心以便旋转/缩放

        # 旋转效果
        if current_time < self.spin_active_until:
            progress = (self.spin_total_duration - (self.spin_active_until - current_time)) / self.spin_total_duration
            eased_progress = 0.5 * (1 - math.cos(progress * math.pi))  # 缓入缓出
            self.current_spin_angle = self.spin_target_angle * eased_progress
            painter.rotate(self.current_spin_angle)
        elif self.spin_active_until > 0:  # 定时器刚结束时重置旋转
            self.current_spin_angle = 0
            self.spin_active_until = 0
        
        # 颤抖和抖动效果
        final_offset_x, final_offset_y = 0, 0
        if current_time < self.shiver_active_until and pixel_size > 0:
            remaining_shiver_time = self.shiver_active_until - current_time
            current_intensity_progress = (remaining_shiver_time / self.shiver_total_duration) if self.shiver_total_duration > 0 else 0
            effective_shiver_intensity = self.shiver_intensity_factor * current_intensity_progress
            s_dx = random.uniform(-effective_shiver_intensity, effective_shiver_intensity) * pixel_size * 0.5 
            s_dy = random.uniform(-effective_shiver_intensity, effective_shiver_intensity) * pixel_size * 0.5
            final_offset_x += s_dx
            final_offset_y += s_dy
        else: 
            self.shiver_active_until = 0

        if current_time < self.jiggle_active_until:
            progress = (self.jiggle_total_duration - (self.jiggle_active_until - current_time)) / self.jiggle_total_duration
            # 创建一个衰减的震荡效果
            oscillation = math.sin(progress * math.pi * 4) * (1 - progress)  # 4次震荡，振幅衰减
            self.jiggle_offset.setX(self.jiggle_magnitude * oscillation * random.choice([-1,1]))
            self.jiggle_offset.setY(self.jiggle_magnitude * oscillation * random.choice([-1,1]))
            final_offset_x += self.jiggle_offset.x()
            final_offset_y += self.jiggle_offset.y()
        else: 
            self.jiggle_active_until = 0

        # 应用组合偏移（相对于新的中心原点）
        offset_x = -heart_draw_width / 2 + final_offset_x
        offset_y = -heart_draw_height / 2 + final_offset_y

        painter.setPen(Qt.NoPen)
        
        # 应用发光效果
        current_base_color = QColor(self.base_color)
        if current_glow_intensity > 0:
            h, s, v, a = current_base_color.getHsv()
            v = min(255, v + int(50 * current_glow_intensity))  # 增加亮度
            s = max(0, s - int(30 * current_glow_intensity))    # 轻微降低饱和度以产生更亮的感觉
            current_base_color = QColor.fromHsv(h,s,v,a)

        current_highlight_color = self._derive_highlight_color(current_base_color)
        current_shadow_color = self._derive_shadow_color(current_base_color)

        # 绘制心形像素
        for r, row_data in enumerate(HEART_PIXEL_MATRIX):
            for c, cell_type in enumerate(row_data):
                if cell_type == 0: 
                    continue
                rect_x, rect_y = offset_x + c * pixel_size, offset_y + r * pixel_size
                pixel_rect = QRectF(int(rect_x), int(rect_y), pixel_size, pixel_size) 
                if cell_type == 1: 
                    painter.setBrush(QBrush(current_base_color))
                elif cell_type == 2: 
                    painter.setBrush(QBrush(current_highlight_color))
                elif cell_type == 3: 
                    painter.setBrush(QBrush(current_shadow_color))
                painter.drawRect(pixel_rect)

        # 绘制显示文本
        if self.display_text:
            text_rect_width = heart_draw_width * 0.8
            text_rect_height = heart_draw_height * 0.6
            text_rect_x = offset_x + (heart_draw_width - text_rect_width) / 2
            text_rect_y = offset_y + (heart_draw_height - text_rect_height) / 2
            text_rect = QRectF(text_rect_x, text_rect_y, text_rect_width, text_rect_height)
            
            font_size = int(pixel_size * 1.6)  # 稍微减小以更好地适应
            if heart_draw_height > 0 and text_rect_height > 0:
                font_size_by_height = int(text_rect_height * 0.3) 
                font_size = min(font_size, font_size_by_height if font_size_by_height > 0 else font_size)
            if font_size < 7: 
                font_size = 7
            font = QFont("Arial", font_size, QFont.Bold)
            painter.setFont(font)

            # 考虑发光效果的文本颜色
            text_color_base = QColor(Qt.white) if current_base_color.lightnessF() < 0.5 else QColor(Qt.black)
            if current_glow_intensity > 0:
                 # 发光期间文本更鲜艳
                text_color_base = QColor(Qt.white) if current_base_color.lightnessF() < 0.6 else QColor(Qt.black)

            painter.setPen(text_color_base)
            text_option = QTextOption()
            text_option.setAlignment(Qt.AlignCenter)
            text_option.setWrapMode(QTextOption.WordWrap)
            painter.drawText(text_rect, self.display_text, text_option)
        
        painter.restore()  # 从 translate(center_x, center_y) 恢复

        # 绘制粒子（在窗口坐标中，在主心形绘制之后）
        for particle in self.particles:
            particle.draw(painter)

    def update_pulsation(self):
        """更新脉动效果"""
        # 平滑频率过渡
        if abs(self.current_frequency_hz - self.target_frequency_hz) > 0.05:
            self.current_frequency_hz += (self.target_frequency_hz - self.current_frequency_hz) * 0.05  # 较慢的变化
        else: 
            self.current_frequency_hz = self.target_frequency_hz
        
        dt_sec = self._pulsation_timer_interval_ms / 1000.0
        self.angle += self.current_frequency_hz * (2 * math.pi) * dt_sec
        if self.angle > (2 * math.pi): 
            self.angle -= (2 * math.pi)

        self.scale_factor = 1.0 + 0.07 * math.sin(self.angle)  # 较小的脉动
        self.update()

    def set_pulsation(self, frequency_hz: float):
        """设置脉动频率
        
        Args:
            frequency_hz: 脉动频率 (Hz)
        """
        self.target_frequency_hz = max(0.3, min(frequency_hz, 8.0))  # 调整后的实用范围
        if not self.pulsation_timer.isActive(): 
            self.pulsation_timer.start(self._pulsation_timer_interval_ms)

    def set_heart_color(self, color_hex: str):
        """设置心形颜色
        
        Args:
            color_hex: 十六进制颜色代码
        """
        try:
            new_target_color = QColor(color_hex)
            if new_target_color.isValid(): 
                self.target_base_color = new_target_color
            else: 
                self.target_base_color = QColor(DEFAULT_HEART_COLOR)
        except Exception: 
            self.target_base_color = QColor(DEFAULT_HEART_COLOR)
        
        self.current_color_step = 0
        if not self.color_change_timer.isActive(): 
            self.color_change_timer.start(40)  # 更快的颜色变化

    def update_color_transition(self):
        """更新颜色过渡效果"""
        if self.current_color_step < self.color_transition_steps:
            self.current_color_step += 1
            r = self.base_color.red() + (self.target_base_color.red() - self.base_color.red()) * self.current_color_step / self.color_transition_steps
            g = self.base_color.green() + (self.target_base_color.green() - self.base_color.green()) * self.current_color_step / self.color_transition_steps
            b = self.base_color.blue() + (self.target_base_color.blue() - self.base_color.blue()) * self.current_color_step / self.color_transition_steps
            self.base_color.setRgb(int(r), int(g), int(b))
        else:
            self.base_color = QColor(self.target_base_color)
            self.color_change_timer.stop()
        
        # 立即更新派生颜色
        self.highlight_color = self._derive_highlight_color(self.base_color)
        self.shadow_color = self._derive_shadow_color(self.base_color)
        self.update()

    def set_display_text(self, text: str):
        """设置显示文本
        
        Args:
            text: 文本内容
        """
        self.display_text = text
        self.update()

    # --- 随机动作方法 ---
    def _is_any_major_animation_active(self):
        """检查是否有主要动画正在运行"""
        t = time.time()
        return t < self.shiver_active_until or \
               t < self.pop_active_until or \
               t < self.spin_active_until or \
               t < self.glow_active_until or \
               t < self.jiggle_active_until or \
               t < self.pressed_active_until

    def random_action_shiver(self):
        """触发颤抖动画"""
        if self._is_any_major_animation_active(): 
            return
        self.shiver_intensity_factor = 0.8  # 较小的强度
        self.shiver_total_duration = random.uniform(0.4, 0.7) 
        self.shiver_active_until = time.time() + self.shiver_total_duration
        self.update()

    def random_action_pop(self):
        """触发弹跳动画"""
        if self._is_any_major_animation_active(): 
            return
        self.total_pop_duration_for_calc = random.uniform(0.3, 0.6) 
        self.pop_active_until = time.time() + self.total_pop_duration_for_calc
        self.update()

    def random_action_spin(self):
        """触发旋转动画"""
        if self._is_any_major_animation_active(): 
            return
        self.spin_total_duration = random.uniform(0.5, 1.0)  # 旋转持续时间
        self.spin_target_angle = random.choice([-360.0, 360.0])  # 旋转方向
        self.spin_active_until = time.time() + self.spin_total_duration
        self.current_spin_angle = 0  # 重置新旋转
        self.update()

    def random_action_glow(self):
        """触发发光动画"""
        if self._is_any_major_animation_active(): 
            return
        self.glow_intensity = random.uniform(0.5, 1.0)
        self.glow_total_duration = random.uniform(0.8, 1.5)
        self.glow_active_until = time.time() + self.glow_total_duration
        self.update()
        self.emit_particles(random.randint(5,10), self.geometry(), self.base_color, "sparkle")

    def random_action_jiggle(self):
        """触发抖动动画"""
        if self._is_any_major_animation_active(): 
            return
        self.jiggle_magnitude = random.uniform(3.0, 7.0)
        self.jiggle_total_duration = random.uniform(0.3, 0.6)
        self.jiggle_active_until = time.time() + self.jiggle_total_duration
        self.update()

    # --- 直接交互方法 ---
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        if event.button() == Qt.LeftButton:
            # 检查点击是否在绘制的心形区域内（近似检查）
            if self.rect().contains(event.pos()):
                self.pressed_active_until = time.time() + 0.25
                
                # 保存当前文本，以便在不是Gemini响应时恢复
                self._text_before_click = self.display_text if self.display_text else "Ruby..."
                
                # 避免在显示Gemini响应时或动画正在改变文本时更改文本
                if not self.long_dialogue_is_visible_externally:
                    quick_responses = QUICK_RESPONSES
                    self.set_display_text(random.choice(quick_responses))
                    QTimer.singleShot(400, self._restore_text_after_click)

                self.update()
                self.clicked_on_heart.emit()  # 发出信号给MainWindow
        super().mousePressEvent(event)  # 允许父窗口处理（例如拖动）

    def _restore_text_after_click(self):
        """点击后恢复文本"""
        # 仅当是快速点击响应时恢复
        if self.display_text in QUICK_RESPONSES and hasattr(self, '_text_before_click'):
             self.set_display_text(self._text_before_click)

    def enterEvent(self, event):
        """鼠标进入事件处理"""
        self.is_hovering = True
        self.hover_scale_bonus = 0.03  # 悬停时轻微放大
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件处理"""
        self.is_hovering = False
        self.hover_scale_bonus = 0.0
        self.update()
        super().leaveEvent(event)
    
    def set_long_dialogue_visibility(self, is_visible: bool):
        """设置长对话是否可见
        
        Args:
            is_visible: 是否可见
        """
        self.long_dialogue_is_visible_externally = is_visible