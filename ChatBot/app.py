import streamlit as st
import base64
from tempfile import NamedTemporaryFile
from audiorecorder import audiorecorder
import coordinator
from Audio.listener import SpeechToText
from Audio.speaker import TextToSpeech
from Tasks.conversation import CoreLLM


@st.cache_resource
def load_text_model(whisper_model) -> SpeechToText:
    """Create and return a SpeechToText class object
    :param whisper_model: a string of a valid whisper_model
    :return: SpeechToText object initialized with the model selected
    """
    print("Loading Speech to Text models")
    stt_obj = SpeechToText(whisper_model)
    print("Speech to Text models loaded!")
    return stt_obj


@st.cache_resource
def load_speech_model() -> TextToSpeech:
    """Create and return a TextToSpeech class object
    :return: TextToSpeech object initialized with the voice selected
    """
    print("Loading Text to Speech models")
    tts_obj = TextToSpeech()
    print("Text to Speech models loaded!")
    return tts_obj


@st.cache_resource
def load_core_LLM(llm_model):
    """Create and return a conversational LLM instance
    :param llm_model: The name of a huggingFace model to use
    :return: CoreLLM object initialized with the model selected
    """
    print("Loading Large Language models")
    llm_obj = CoreLLM(coordinator.task_list, llm_model)
    print("Large Language models loaded!")
    return llm_obj


def transcription(audio) -> str:
    """Save audio to a file and return the text transcription
    """
    with NamedTemporaryFile(suffix=".wav") as temp:
        audio.export(f"{temp.name}", format="wav")

        text = STT_object.wav_to_text(f"{temp.name}")
    return text


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


# Begin Streamlit page code
with st.sidebar:
    # Enable audio capture button
    audio = audiorecorder("Click to send voice message", "Recording... Click when you're done", key="recorder")

    st.title("Home Bot 1.0")
    llm_model = st.selectbox("LLM", ["Qwen/Qwen2.5-1.5B-Instruct", "meta-llama/Llama-3.2-1B", "deepseek-ai/DeepSeek-V2.5"], index=0)
    image_model = st.selectbox("Images", ["stabilityai/stable-diffusion-2", "stabilityai/stable-diffusion-xl-base-1.0"], index=0)
    LLM_object = load_core_LLM(llm_model)
    precision = st.selectbox("STT Precision", ["whisper-tiny", "whisper-base", "whisper-small"], index=1)
    STT_object = load_text_model(precision)
    TTS_object = load_speech_model()

    voice = st.toggle('Voice', value=True)
    speaker = st.selectbox("Speaker", ["David", "Morgan", "Scarlett"])
    TTS_object.set_speaker(speaker)

    args = {
        'llm_model': llm_model,
        'image_model': image_model
    }

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if (prompt := st.chat_input("Your message")) or len(audio):
    # If it's coming from the audio recorder transcribe the message with whisper.cpp
    if not prompt and len(audio)>0:
        prompt = transcription(audio)

    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # response = f"{prompt}"
    response = coordinator.run(prompt, LLM_object, **args)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response['msg'])
        if voice:
            # tts = TTS_object.speak(response, lang=lang)

            with NamedTemporaryFile(suffix=".wav") as temp:
                tts = TTS_object.speak(response['msg'], temp.name)
                # tts.save(temp.name)
                audio_play(temp.name)

    # Add assistant response to chat history
    history = {"role": "assistant", "content": response['msg']}
    if 'image' in response.keys():
        history['image'] = response['image']
    st.session_state.messages.append(history)

    if 'image' in response.keys():
        st.chat_message("assistant").image(response['image'], caption=prompt, use_container_width=True)
