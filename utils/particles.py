# 粒子效果类，用于创建心形周围的视觉效果
import time
import random
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainter, QColor

class Particle:
    """粒子类，用于创建视觉效果"""
    def __init__(self, pos: QPointF, vel: QPointF, life_ms: int, start_color: QColor, end_color: QColor, start_size: float, end_size: float):
        self.pos = pos
        self.vel = vel
        self.life_max = life_ms
        self.life_current = life_ms
        self.start_color = start_color
        self.end_color = end_color
        self.start_size = start_size
        self.end_size = end_size
        self.creation_time = time.time()

    def update(self, dt_ms: int) -> bool: # Returns True if still alive
        """更新粒子状态，返回粒子是否仍然存活"""
        self.life_current -= dt_ms
        if self.life_current <= 0:
            return False
        self.pos += self.vel * (dt_ms / 1000.0)
        # Optional: add gravity or other forces
        # self.vel.setY(self.vel.y() + 0.05 * (dt_ms / 1000.0)) # Simple gravity
        return True

    def draw(self, painter: QPainter):
        """绘制粒子"""
        progress = (self.life_max - self.life_current) / self.life_max
        
        r = int(self.start_color.red() + (self.end_color.red() - self.start_color.red()) * progress)
        g = int(self.start_color.green() + (self.end_color.green() - self.start_color.green()) * progress)
        b = int(self.start_color.blue() + (self.end_color.blue() - self.start_color.blue()) * progress)
        a = int(self.start_color.alpha() + (self.end_color.alpha() - self.start_color.alpha()) * progress)
        current_color = QColor(r,g,b,a)
        
        current_size = self.start_size + (self.end_size - self.start_size) * progress
        
        painter.setBrush(current_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.pos, current_size, current_size)