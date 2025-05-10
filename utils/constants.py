# 项目中使用的常量定义
from PyQt5.QtGui import QColor

# --- 心形像素矩阵定义 ---
HEART_PIXEL_MATRIX = [
    [0,0,0,0,3,3,0,0,3,3,0,0,0,0], [0,0,0,3,1,1,3,3,1,1,3,0,0,0], [0,0,3,1,2,1,1,1,1,2,1,3,0,0],
    [0,0,3,1,1,1,1,1,1,1,1,3,0,0], [0,3,1,1,1,1,1,1,1,1,1,1,3,0], [0,3,1,1,1,1,1,1,1,1,1,1,3,0],
    [0,3,1,1,1,1,1,1,1,1,1,1,3,0], [0,0,3,1,1,1,1,1,1,1,1,3,0,0], [0,0,0,3,1,1,1,1,1,1,3,0,0,0],
    [0,0,0,0,3,1,1,1,1,3,0,0,0,0], [0,0,0,0,0,3,1,1,3,0,0,0,0,0], [0,0,0,0,0,0,3,3,0,0,0,0,0,0]
]
HEART_MATRIX_HEIGHT = len(HEART_PIXEL_MATRIX)
HEART_MATRIX_WIDTH = len(HEART_PIXEL_MATRIX[0]) if HEART_MATRIX_HEIGHT > 0 else 0

# 默认颜色
DEFAULT_HEART_COLOR = "#FFC0CB"  # 粉色
ERROR_HEART_COLOR = "#AA0000"    # 深红色

# 动画和定时器相关常量
DEFAULT_PULSE_FREQUENCY = 1.0
DEFAULT_ANIMATION_DURATION_MS = 500
PARTICLE_UPDATE_INTERVAL_MS = 16  # ~60 FPS
COLOR_TRANSITION_STEPS = 20
PULSATION_TIMER_INTERVAL_MS = 30
OUTPUT_HIDE_TIMEOUT_MS = 12000
ERROR_HIDE_TIMEOUT_MS = 20000

# API相关
GEMINI_MODEL_NAME = 'gemini-2.0-flash-lite'
API_KEY = ""  # 实际应用中应通过环境变量获取

# 快速回复文本
QUICK_RESPONSES = ["Ouch!", "Hehe!", "Eep!", "Hmm?", ":)"]