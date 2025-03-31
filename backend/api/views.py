from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def generate_music(request):
    # 处理语音生成音乐的逻辑
    return Response({"lyrics": "生成的歌词", "music_url": "/media/music.mp3"})