from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def generate_music(request):
    # Processing logic for speech-generated music
    return Response({"lyrics": "Generated lyrics", "music_url": "/media/music.mp3"})