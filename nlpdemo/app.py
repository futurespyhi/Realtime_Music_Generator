import gradio as gr
import soundfile as sf
from dataclasses import dataclass, field
from typing import Any
import xxhash
import os
import groq

from tools.groq_client import client as groq_client
import spaces

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
    state.genre = genre_value
    state.mood = mood_value
    state.theme = theme_value

    file_name = f"/tmp/{xxhash.xxh32(bytes(audio[1])).hexdigest()}.wav"

    sf.write(file_name, audio[1], audio[0], format="wav")

    # Initialize Groq client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")
    client = groq.Client(api_key=api_key)

    # Transcribe the audio file
    transcription = transcribe_audio(client, file_name)
    if transcription:
        if transcription.startswith("Error"):
            transcription = "Error in audio transcription."

        # Append the user's message in the proper format
        state.conversation.append({"role": "user", "content": transcription})

        # Generate assistant response with current settings
        assistant_message = generate_chat_completion(client, state.conversation, state.genre, state.mood, state.theme)

        # Append the assistant's message in the proper format
        state.conversation.append({"role": "assistant", "content": assistant_message})

        print(state.conversation)

        # Optionally, remove the temporary file
        os.remove(file_name)

    return state, state.conversation


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

    state = gr.State(value=AppState())
    
    genre.change(update_state_settings, [state, genre, mood, theme], [state])
    mood.change(update_state_settings, [state, genre, mood, theme], [state])
    theme.change(update_state_settings, [state, genre, mood, theme], [state])
    
    stream = input_audio.start_recording(
        process_audio,
        [input_audio, state],
        [input_audio, state],
    )
    
    # Pass dropdown values to response function
    respond = input_audio.stop_recording(
        response, [state, input_audio, genre, mood, theme], [state, chatbot]
    )
    
    restart = respond.then(start_recording_user, [state], [input_audio]).then(
        lambda state: state, state, state, js=js_reset
    )

    # Reset button now creates a new AppState with default values
    cancel = gr.Button("New Song", variant="stop")
    cancel.click(
        lambda: (AppState(), gr.Audio(recording=False)),
        None,
        [state, input_audio],
        cancels=[respond, restart],
    )

    gr.Markdown("### How to use:\n1. Select your genre, mood, and theme preferences\n2. Just start talking about your song ideas\n3. The assistant will create lyrics based on your selections\n4. Give feedback to refine the lyrics\n5. Click 'New Song' to start over")


if __name__ == "__main__":
    demo.launch()