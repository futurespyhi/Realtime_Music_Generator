import gradio as gr
import soundfile as sf
from dataclasses import dataclass, field
from typing import Any
import xxhash
import os
import groq
import numpy as np

from tools.groq_client import client as groq_client
import spaces

from tools.generate_lyrics import generate_structured_lyrics, format_lyrics_for_yue

@dataclass
class AppState:
    conversation: list = field(default_factory=list)
    stopped: bool = False
    model_outs: Any = None
    lyrics: str = ""
    genre: str = "pop"
    mood: str = "upbeat"
    theme: str = "love"


def process_whisper_response(completion):
    """
    Process Whisper transcription 
    Returns:
        str or None: Transcribed text if no_speech_prob <= 0.7, otherwise None
    """
    if completion.segments and len(completion.segments) > 0:
        no_speech_prob = completion.segments[0].get('no_speech_prob', 0)
        print("No speech prob:", no_speech_prob)

        if no_speech_prob > 0.7:
            print("No speech detected")
            return None
            
        return completion.text.strip()
    
    return None

def transcribe_audio(client, file_name):
    if file_name is None:
        return None

    try:
        with open(file_name, "rb") as audio_file:
            response = client.audio.transcriptions.with_raw_response.create(
                model="whisper-large-v3-turbo",
                file=("audio.wav", audio_file),
                response_format="verbose_json",
                language="en",
            )
            completion = process_whisper_response(response.parse())

        return completion
    except Exception as e:
        print(f"Error in transcription: {e}")
        return f"Error in transcription: {str(e)}"
    

def generate_chat_completion(client, history, genre, mood, theme):
    messages = []
    system_prompt = f"""You are a creative AI music generator assistant. Help users create song lyrics in the {genre} genre with a {mood} mood about {theme}.
When generating lyrics, create a chorus and at least one verse. Format lyrics clearly with VERSE and CHORUS labels.
Ask if they like the lyrics or want changes. Be conversational, friendly, and creative.
Keep the lyrics appropriate for the selected genre, mood, and theme unless the user specifically requests changes."""
    
    messages.append(
        {
            "role": "system",
            "content": system_prompt,
        }
    )

    for message in history:
        messages.append(message)

    try:
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=messages,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error in generating chat completion: {str(e)}"
    

theme_gradio = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="blue",
    font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
    radius_size="md",
    text_size="md",
    spacing_size="md",
)

def start_recording_user(state: AppState):
    return None

def process_audio(audio: tuple, state: AppState):
    return audio, state

def update_state_settings(state: AppState, genre_value, mood_value, theme_value):
    state.genre = genre_value
    state.mood = mood_value
    state.theme = theme_value
    return state


@spaces.GPU(duration=40, progress=gr.Progress(track_tqdm=True))
def response(state: AppState, audio: tuple, genre_value, mood_value, theme_value):
    if not audio:
        return AppState(), []
    
    # Update state with current dropdown values
    state.genre, state.mood, state.theme = genre_value, mood_value, theme_value

    file_name = f"/tmp/{xxhash.xxh32(bytes(audio[1])).hexdigest()}.wav"

    sf.write(file_name, audio[1], audio[0], format="wav")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")
    client = groq.Client(api_key=api_key)

    # Transcribe the audio file
    transcription = transcribe_audio(client, file_name)
    if transcription:
        if transcription.startswith("Error"):
            transcription = "Error in audio transcription."

        state.conversation.append({"role": "user", "content": transcription})

        assistant_message = generate_chat_completion(client, state.conversation, state.genre, state.mood, state.theme)

        state.conversation.append({"role": "assistant", "content": assistant_message})
        

        # print(state.conversation)

        os.remove(file_name)

    return state, state.conversation


# Function to generate music from lyrics
@spaces.GPU(duration=60, progress=gr.Progress(track_tqdm=True))
def generate_music_from_lyrics(state: AppState):
    # Extract the final lyrics from the conversation
    # Look for the latest assistant response containing lyrics
    lyrics = ""
    for message in reversed(state.conversation):
        if message["role"] == "assistant" and "verse" in message["content"].lower() and "chorus" in message["content"].lower():
            lyrics = message["content"]
            break
    
    if not lyrics:
        return None, "ERROR: No lyrics found to generate music. Please create lyrics first be sure that the AI generated at least one CHORUS and VERSE in ONE message."

    try:
        # TODO 1: From the chat history, ask an LLM To generate the complete lyrics with structure output, it could be gcloud, gemma 3 for example
        structured_lyrics = generate_structured_lyrics(
            conversation=state.conversation,
            genre=state.genre,
            mood=state.mood,
            theme=state.theme
        )
        
        # Format the structured lyrics into a string
        lyrics = format_lyrics_for_yue(structured_lyrics, state.genre, state.mood, state.theme)

        print(lyrics)

        # TODO 2: From the lyrics, generate music using a music generation model (YUE)

        # Save temporary audio file
        # tmp_file = f"/tmp/generated_music_{xxhash.xxh32(lyrics.encode()).hexdigest()}.wav"
        # sf.write(tmp_file, audio_data, sample_rate)
        
        # return tmp_file, f"Music generated for your {state.genre} song with {state.mood} mood about {state.theme}!"
        
    except Exception as e:
        error_msg = f"Error generating music: {str(e)}"
        print(error_msg)
        return None, error_msg


# load frontend.js
js = open("frontend.js").read()



js_reset = """
() => {
  var record = document.querySelector('.record-button');
  record.textContent = "Just Start Talking!"
  record.style = "width: fit-content; padding-right: 0.5vw;"
}
"""

with gr.Blocks(theme=theme_gradio, js=js) as demo:
    gr.HTML("""
    <style>
    #center-text {
        text-align: center;
    }
    </style>
    """)
    gr.Markdown("# 🎵 Hi, this is MiloMusic 🎵", elem_id="center-text")
    gr.Markdown("Just start talking to generate song lyrics. Select genre, mood, and theme below to customize your song.")
    
    # drop list
    with gr.Row():
        genre = gr.Dropdown(choices=["pop", "rock", "jazz", "hip-hop", "electronic"], value="pop", label="Genre")
        mood = gr.Dropdown(choices=["upbeat", "sad", "energetic", "chill", "romantic"], value="upbeat", label="Mood")
        theme = gr.Dropdown(choices=["love", "breakup", "party", "reflection", "adventure"], value="love", label="Theme")

    with gr.Row():
        input_audio = gr.Audio(
            label="Speak Your Musical Ideas",
            sources=["microphone"],
            type="numpy",
            streaming=False,
            waveform_options=gr.WaveformOptions(waveform_color="#B83A4B"),
        )
    with gr.Row():
        chatbot = gr.Chatbot(label="Creative Conversation", type="messages", height=400)

    with gr.Row():
        generate_btn = gr.Button("🎵 Generate Music from Lyrics", variant="primary")
    
    with gr.Row():
        music_output = gr.Audio(label="Generated Music", type="filepath")
        generation_status = gr.Textbox(label="Status", placeholder="Click the button above to generate music")

    state = gr.State(value=AppState())
    
    genre.change(update_state_settings, [state, genre, mood, theme], [state])
    mood.change(update_state_settings, [state, genre, mood, theme], [state])
    theme.change(update_state_settings, [state, genre, mood, theme], [state])
    
    stream = input_audio.start_recording(
        process_audio,
        [input_audio, state],
        [input_audio, state],
    )
    
    respond = input_audio.stop_recording(
        response, [state, input_audio, genre, mood, theme], [state, chatbot]
    )
    
    restart = respond.then(start_recording_user, [state], [input_audio]).then(
        lambda state: state, state, state, js=js_reset
    )

    generate_btn.click(
        generate_music_from_lyrics,
        [state],
        [music_output, generation_status]
    )

    # Reset button now creates a new AppState with default values
    cancel = gr.Button("New Song", variant="stop")
    cancel.click(
        lambda: (AppState(), gr.Audio(recording=False), None, "Start a new song"),
        None,
        [state, input_audio, music_output, generation_status],
        cancels=[respond, restart],
    )

    gr.Markdown("### How to use:\n1. Select your genre, mood, and theme preferences\n2. Just start talking about your song ideas\n3. The assistant will create lyrics based on your selections\n4. Give feedback to refine the lyrics\n5. When you're happy with the lyrics, click 'Generate Music from Lyrics'\n6. Listen to your generated song!")


if __name__ == "__main__":
    import tempfile
    if os.name == "nt":
        demo.launch(allowed_paths=[tempfile.gettempdir()])
    else:
        demo.launch(allowed_paths=["/tmp"])