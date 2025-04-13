import os
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from nlpdemo.tools.generate_lyrics import generate_structured_lyrics, format_lyrics
from dotenv import load_dotenv

load_dotenv()

def test_lyrics_generation():
    # Test conversation
    test_conversation = [
        {"role": "user", "content": "I want to write a love song"},
        {"role": "assistant", "content": "I'll help you create a love song. What style are you thinking of?"},
        {"role": "user", "content": "Something romantic and modern"},
        {"role": "assistant", "content": "Perfect! Here are the lyrics I've created:\n\nVERSE:\nSoft city lights paint the evening sky\nAs I think about you and I\nEvery moment we've shared feels right\nLike stars aligned in the night\n\nCHORUS:\nThis modern love, it's all we need\nBreaking rules and setting us free\nEvery text, every call, every memory\nMakes this love our reality"}
    ]
    
    try:
        song = generate_structured_lyrics(
            conversation=test_conversation,
            genre="pop",
            mood="romantic",
            theme="love"
        )
        
        print("\n=== Test Results ===")
        print("\nGenerated Song Structure:")
        print(song)
        print("\nFormatted Lyrics:")
        print(format_lyrics(song))
        print("\n==================")
        
        return True
        
    except Exception as e:
        print(f"\nError in test: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing lyrics generation...")
    success = test_lyrics_generation()
    print(f"\nTest {'passed' if success else 'failed'}")
