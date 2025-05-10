from pydantic import BaseModel, Field
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal

class RubyResponse(BaseModel):
    """Pydantic模型，用于解析Gemini API的响应"""
    short_dialogue: str = Field(..., description="A very short phrase or a few words (max 3-5 words) for the heart display.")
    long_dialogue: str = Field(..., description="ruby's main, longer chat message as a playful little girl.")
    color_hex: str = Field(..., description="Hex color code (e.g., #FFC0CB) for the heart, based on ruby's mood.")
    frequency_hz: float = Field(..., description="Heartbeat frequency (0.5-15.0 Hz, but practically capped lower for display) based on ruby's mood.")


class GeminiSignals(QObject):
    """信号类，用于在线程间传递Gemini API响应"""
    result = pyqtSignal(RubyResponse)
    error = pyqtSignal(str)