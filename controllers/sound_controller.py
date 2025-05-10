from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl
import os

class SoundController:
    """管理应用程序的声音效果"""
    
    def __init__(self):
        self.sound_effects = {}
        self.sounds_enabled = True
        
    def init_sounds(self, sound_dir="resources/sounds"):
        """初始化声音文件
        
        Args:
            sound_dir: 声音文件所在目录
        """
        # 声音文件配置
        sound_files = {
            "poke": "poke.wav",
            "pop": "pop.wav",
            "spin": "swoosh.wav",
            "jiggle": "jiggle.wav",
            "heartbeat_soft": "heartbeat_soft.wav",  # 较低频率
            "heartbeat_fast": "heartbeat_fast.wav",  # 较高频率
            "message_receive": "message.wav",
            "ui_click": "click.wav"
        }
        
        for name, filename in sound_files.items():
            full_path = os.path.join(sound_dir, filename)
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(full_path))
            effect.setVolume(0.6)
            
            if effect.status() == QSoundEffect.Error:
                print(f"Warning: Could not load sound '{name}' from '{full_path}'. Status: {effect.status()}")
                self.sound_effects[name] = None  # 记录加载失败
            else:
                self.sound_effects[name] = effect
    
    def play_sound(self, name: str, volume: float = -1.0):
        """播放指定声音
        
        Args:
            name: 声音名称
            volume: 音量 (0.0-1.0)，-1表示使用默认音量
        """
        if not self.sounds_enabled:
            return
            
        if name in self.sound_effects and self.sound_effects[name]:
            sound = self.sound_effects[name]
            if sound.status() == QSoundEffect.Ready:
                if volume >= 0.0:
                    sound.setVolume(min(1.0, volume))
                sound.play()
    
    def enable_sounds(self, enabled=True):
        """启用或禁用声音
        
        Args:
            enabled: 是否启用声音
        """
        self.sounds_enabled = enabled
        
    def are_sounds_enabled(self):
        """返回声音是否启用
        
        Returns:
            声音是否启用
        """
        return self.sounds_enabled