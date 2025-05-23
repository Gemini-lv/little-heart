# Ruby Heart Chat

Ruby Heart Chat是一个基于PyQt5和Gemini API的互动聊天应用，展示了一个会对用户输入做出反应的可爱心形界面。

## 功能特点

- 心形互动界面，可以通过点击、戳等方式与Ruby互动
- 情绪化的心形显示，会根据对话内容改变颜色和跳动频率
- 粒子效果系统，为不同情绪提供视觉反馈
- 利用Gemini AI API实现智能对话
- 多模块化设计，易于扩展

## 项目结构

- **models/**: 数据模型
- **views/**: UI组件
- **controllers/**: 业务逻辑控制器
- **utils/**: 工具类
- **resources/**: 资源文件

## 启动方法

1. 安装所需依赖：
```bash
pip install PyQt5 google-generativeai pydantic
```
2. 运行主程序：
```bash
python main.py
```

# 演示视频
<video width="320" height="240" controls>
    <source src="https://www.bilibili.com/video/BV1tEVdzREmb/" type="video/mp4">
</video>

## 注意事项

- 需要有效的Gemini API密钥（love\utils\constants.py）  
- 首次运行时会自动创建占位声音文件，可替换为真实声音文件以获得更好体验