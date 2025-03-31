from django.db import models

class MusicGeneration(models.Model):
    user_input = models.TextField()  # 用户语音转文本
    generated_lyrics = models.TextField()  # 生成的歌词
    music_file = models.FileField(upload_to='music/')  # 生成的音乐文件
    created_at = models.DateTimeField(auto_now_add=True)