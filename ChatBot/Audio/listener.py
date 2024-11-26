import warnings
import whisper
import torch


warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

class SpeechToText:
    def __init__(self, model):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        if model not in ['whisper-tiny', 'whisper-base']:
            model = 'small'
        else:
            model = model.split('-')[1]
        self.model = whisper.load_model(model, device=self.device)
        # get available languages
        # self.model.
        # self.language_codes = self.model.tokenizer.TO_LANGUAGE_CODE
        # self.language_codes = self.model.lan
        # # Create sorted list of available languages
        # self.language_list = sorted([language.capitalize() for language in self.language_codes.keys()])
        # # Insert automatic so that it appears first in the list
        # self.language_codes["automatic"] = "auto"
        # self.language_list.insert(0, "Automatic")

    def wav_to_text(self, audio_path):
        # segments, _ = self.model.transcribe(audio_path)
        # text = "".join(segment.text for segment in segments)
        # return text
        return self.model.transcribe(audio_path)['text']


