import torch
from TTS.api import TTS


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

