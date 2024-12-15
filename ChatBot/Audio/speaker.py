import torch
import re
import threading
import queue
import wave
import nltk
from tempfile import NamedTemporaryFile
from TTS.api import TTS
from time import sleep

nltk.download('punkt')  # For splitting text into sentence like chunks

AVAILABLE_MODELS = ["tts_models/multilingual/multi-dataset/xtts_v2"]
AVAILABLE_SPEAKERS = {
    "tts_models/multilingual/multi-dataset/xtts_v2": ["David", "Morgan", "Scarlett"]
}


class TextToSpeech:
    def __init__(self, model):
        self.model = model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(self.model).to(self.device)
        self.speak = None
        self.speaker = None
        self.set_speaker(AVAILABLE_SPEAKERS[self.model][0])  # sets

    def set_speaker(self, voice):
        match voice:
            case "Morgan":
                self.speak = self.save_morgan
            case "Scarlett":
                self.speak = self.save_scarlett
            case "David" | _:
                self.speak = self.save_david
        self.speaker = voice

    # Text to speech to a wav array
    def speak_david(self, text, lang):
        return self.tts.tts(text=text, speaker_wav="voices/david_attenbourough.wav", language=lang) #, 24000
    def speak_morgan(self, text, lang):
        return self.tts.tts(text=text, speaker_wav="./voices/New_Morgan_Freeman.wav", language=lang) #, 24000
    def speak_scarlett(self, text, lang):
        return self.tts.tts(text=text, speaker_wav="./Audio_out/Scarlett_johanson.wav", language=lang) #, 24000

    # Text to speech to a file
    def save_david(self, text, file_path, lang='en', ):
        self.tts.tts_to_file(text=text, speaker_wav="voices/david_attenbourough.wav", language=lang, file_path=file_path)
    def save_morgan(self, text, file_path, lang='en', ):
        self.tts.tts_to_file(text=text, speaker_wav="voices/New_Morgan_Freeman.wav", language=lang, file_path=file_path)
    def save_scarlett(self, text, file_path, lang='en', ):
        self.tts.tts_to_file(text=text, speaker_wav="voices/Scarlett_johanson.wav", language=lang, file_path=file_path)

    def audio_chunker(self, text: str) -> tuple[threading, queue]:
        """
        Takes a string of the text to be rendered and spoken breaks it up into
        sentences and then starts a separate thread to render the chunks.
        then returns the thread object and the queue for playing

        args:
            text: string of text to be rendered

        return:
            a tuple of the thread rendering the audio and a queue containing
            (file pointer, duration) tuples of audio to be played.
        """
        wav_q = queue.Queue()  # Thread safe structure for populating while using
        # Clean text for speaking (acronyms and markups)
        text = self.speak_cleaner(text)
        # Break text into smaller chunks for rendering quicker
        chunks = nltk.tokenize.sent_tokenize(text, language='english')
        # Thread audio rendering to support quicker playback
        wav_generator = threading.Thread(target=self.chunk_renderer, args=(chunks, wav_q))
        wav_generator.start()
        # Wait for queue to have audio data before returning
        while not wav_q.not_empty:
            sleep(.1)
        return wav_generator, wav_q

    def chunk_renderer(self, chunks: list[str], wav_q: queue) -> None:
        """
        Creates a temp file to store the generate wav data and places it into
        a FIFO queue of (file pointer, clip duration) tuples for playing

        args:
            chunks: The list of strings to be rendered
            wav_q: The queue to insert the rendered chunks into
        :return:
        """
        for chunk in chunks:
            with NamedTemporaryFile(suffix=".wav") as temp:
                # Generate audio using objects set speaker voice
                self.speak(chunk, temp.name)
                # Add file pointer and audio duration to playback queue as a tuple
                wav_q.put((open(temp.name, 'rb'), self.file_duration(temp.name)))
        # Add indicator that all clips have been added to queue
        wav_q.put(("complete", "complete"))

    def file_duration(self, file_name) -> float:
        with wave.open(file_name, 'rb') as wav:
            # Determine the length of the audio clip for playback management
            length = round(wav.getnframes() / float(wav.getframerate()), 2)  # in 0.00 seconds format
        return length

    def speak_cleaner(self, text) -> str:
        '''
        uses regex to attempt to make the text more speakable
        '''
        replacements = {
            "°F": " degrees Fahrenheit",
            "°C": " degrees Celsius",
            "mph": " miles per hour",
            "km/h": " kilometers per hour",
            ":": ","
        }
        return re.sub(r'|'.join(replacements.keys()), lambda m: replacements[m.group(0)], text)