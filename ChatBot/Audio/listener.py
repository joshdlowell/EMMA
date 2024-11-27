import warnings
import whisper
import torch
from tempfile import NamedTemporaryFile


warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

AVAILABLE_MODELS = ["whisper-tiny", "whisper-base", "whisper-small"]

class SpeechToText:
    def __init__(self, model):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.selection = model
        if model not in ['whisper-tiny', 'whisper-base']:
            self.model = whisper.load_model('small', device=self.device)
        else:
            self.model = whisper.load_model(model.split('-')[1], device=self.device)

    def wav_to_text(self, audio_path):
        return self.model.transcribe(audio_path)['text']

    def transcription(self, audio) -> str:
        """Save audio to a file and return the text transcription
        """
        with NamedTemporaryFile(suffix=".wav") as temp:
            audio.export(f"{temp.name}", format="wav")
            text = self.wav_to_text(f"{temp.name}")
        return text


