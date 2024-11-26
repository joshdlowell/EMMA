import warnings
import whisper
import torch


warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

class SpeechToText:
    def __init__(self, model):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        if model not in ['whisper-tiny', 'whisper-base']:
            self.model = whisper.load_model('small', device=self.device)
        else:
            self.model = whisper.load_model(model.split('-')[1], device=self.device)

    def wav_to_text(self, audio_path):
        return self.model.transcribe(audio_path)['text']


