from queue import Queue
from time import sleep
import streamlit as st
import base64
from tempfile import NamedTemporaryFile
from audiorecorder import audiorecorder
from coordinator import Coordinator


@st.cache_resource
def load_coordinator():
    """Create and return a coordinator instance to control
    prompt and response flow and management
    :return: Coordinator object
    """
    print("Creating coordinator")
    coord = Coordinator()
    print("Coordinator created!")
    return coord


def set_models(coord):
    """Create and return a coordinator instance to control
    prompt and response flow and management
    :return: Coordinator object
    """
    print("Loading models and settings selections")
    coord.set_models()
    print("Loading complete!")


def audio_play(file_path: str) -> None:
    """Wrap audio data for in-browser playback
    """
    with open(file_path, "rb") as f:
        data = f.read()
    markdown = f"""
        <audio controls autoplay="true">
        <source src="data:audio/wav;base64,{base64.b64encode(data).decode()}" type="audio/wav">
        </audio>
        """
    st.markdown(markdown, unsafe_allow_html=True)

def chunk_player(chunk_thread, wav_q) -> None:
    """Wrap audio data for in-browser playback
    """
    data_fp, duration = wav_q.get()
    while 'complete' != duration:
        data = data_fp.read()
        markdown = f"""
            <audio controls autoplay="true">
            <source src="data:audio/wav;base64,{base64.b64encode(data).decode()}" type="audio/wav">
            </audio>
            """
        audio_bubble = st.markdown(markdown, unsafe_allow_html=True)
        data_fp.close()
        sleep(duration)
        data_fp, duration = wav_q.get(block=True)
        audio_bubble.empty()

    chunk_thread.join()


# Begin Streamlit page code
with st.sidebar:
    # Get coordinator
    coordinator = load_coordinator()
    # Enable audio capture button
    audio = audiorecorder("Click to send voice message", "Recording... Click when you're done", key="recorder")

    st.title("Home Bot 1.1")
    # Select models and settings
    coordinator.llm_model_selection = st.selectbox("LLM", coordinator.available_llm_models, index=0)
    coordinator.image_model_selection = st.selectbox("Images", coordinator.available_image_model, index=0)
    coordinator.precision_selection = st.selectbox("STT Precision", coordinator.available_precision, index=1)
    coordinator.voice_enabled = st.toggle('Voice', value=True)
    coordinator.quick_play = st.toggle('Quick play', value=True)
    coordinator.tts_selection = st.selectbox("TTS Model", coordinator.available_tts_models, index=0)
    coordinator.speaker_selection = st.selectbox("Speaker", coordinator.available_speakers, index=0)

    # Load the selected models and settings
    set_models(coordinator)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if (prompt := st.chat_input("Your message")) or len(audio):
    # If it's coming from the audio recorder transcribe
    if not prompt and len(audio)>0:
        prompt = coordinator.stt_object.transcription(audio)

    # Display user message in chat message container and add to chat history
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Pass prompt to the LLM coordinator and collect text response
    response = coordinator.run(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response['msg'])
        if coordinator.voice_enabled:
            if coordinator.quick_play:
                chunk_thread, wav_q = coordinator.tts_object.audio_chunker(response['msg'])
                chunk_player(chunk_thread, wav_q)
            else:
                with NamedTemporaryFile(suffix=".wav") as temp:
                    tts = coordinator.tts_object.speak(response['msg'], temp.name)
                    # tts.save(temp.name)
                    audio_play(temp.name)

    # Add assistant response to chat history
    history = {"role": "assistant", "content": response['msg']}
    if 'image' in response.keys():
        history['image'] = response['image']
        try:
            caption = response['msg'].split("-")[1]
        except IndexError as e:
            caption = prompt
        st.chat_message("assistant").image(response['image'], caption=caption, use_container_width=True)
    st.session_state.messages.append(history)
