from datetime import datetime
from Tasks import image_generation
from Tasks.tool_utils import tool_caller
from Tasks import core_tools_llm
from Audio import listener, speaker


class Coordinator:
    def __init__(self, messages=None):
        # Always on models
        self.available_llm_models = core_tools_llm.AVAILABLE_MODELS
        self.llm_model_selection = None
        self.llm_object = None

        self.available_precision = listener.AVAILABLE_MODELS
        self.precision_selection = None
        self.stt_object = None

        self.available_tts_models = speaker.AVAILABLE_MODELS
        self.tts_selection = None
        self.available_speakers = speaker.AVAILABLE_SPEAKERS[speaker.AVAILABLE_MODELS[0]]
        self.speaker_selection = None
        self.voice_enabled = False
        self.quick_play = True
        self.tts_object = None

        # On demand models
        self.available_image_model = ["stabilityai/stable-diffusion-2", "stabilityai/stable-diffusion-xl-base-1.0"]
        self.image_model_selection = None
        self.image_object = None

        # Conversation memory
        self.initial_prompt = [
                {
                    "role":
                        "system",
                    "content":
                        f"You are Qwen, You are a helpful assistant who acts like a sassy movie "
                        f"director from the 1980s.\n\nCurrent Date: {datetime.today().strftime('%Y-%m-%d')}"
                },
            ]
        if not messages:
            messages = self.initial_prompt
        self.messages = messages

    def set_models(self):
        """
        Recreates the models if any user selection changes were made. Removes TTS from
        memory if the voice is toggled off
        """
        if not self.llm_object or self.llm_model_selection != self.llm_object.model_name:
            self.llm_object = core_tools_llm.CoreLLM(self.llm_model_selection)
            print("LLM updated")
        else:
            print("No LLM changes")

        if not self.stt_object or self.precision_selection != self.stt_object.selection:
            self.stt_object = listener.SpeechToText(self.precision_selection)
            print("STT updated")
        else:
            print("No STT changes")

        # Remove TTS from memory if voice is disabled
        if not self.voice_enabled and self.tts_object:
            del self.tts_object
            self.tts_object = None
            print("TTS unloaded")
        elif not self.tts_object or self.tts_selection != self.tts_object.model:
            self.tts_object = speaker.TextToSpeech(self.tts_selection)
            self.available_speakers = speaker.AVAILABLE_SPEAKERS[self.tts_selection]
            print("TTS updated")
        else:
            print("No TTS changes")

        if self.tts_object and self.speaker_selection != self.tts_object.speaker:
            self.tts_object.set_speaker(self.speaker_selection)  # Set the voice for the model
            print("TTS voice updated")
        else:
            print("No voice change")

    def run(self, user_prompt):
        if not self.llm_object:
            return {"msg": "Please select an LLM model first"}

        self.messages.append({"role": "user", "content": user_prompt},)
        self.message_maintenance()
        output_text = self.llm_object.generator(self.messages)

        if tool_calls := self.messages[-1].get("tool_calls", None):
            tool_caller(tool_calls, self.messages)
            output_text = self.llm_object.generator(self.messages)

        return {"msg": output_text}

    def message_maintenance(self):
        if len(self.messages) > 40:
            self.messages = self.messages[-40:]


