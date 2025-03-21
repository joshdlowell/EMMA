from datetime import datetime
from tempfile import NamedTemporaryFile

from Tasks.tool_utils import tool_caller
from Tasks import core_tools_llm, timers
from Tasks.home_assistant import get_device_status
from Audio import listener, speaker


class Coordinator:
    def __init__(self, player_callback, streamlit_ctx, streamlit_add_ctx, messages=None):
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

        # Threadding interrupt tracking
        self.speak_lock = 0  # using approach to increment and check value to defeat race conditions
        self.streamlit_ctx = streamlit_ctx
        self.streamlit_add_ctx = streamlit_add_ctx

        # Timer integration
        self.pending_interrupt = False
        self.interrupt_file = None
        # Capture the callback for the streamlit audioplayer
        self.player_callback = player_callback
        # Create a timer object and give the callback for the coordinator
        self.timers = timers.Timers(self.audio_file_generator, self.streamlit_ctx, self.streamlit_add_ctx)

        # Conversation memory
        self.initial_prompt = [
                {
                    "role":
                        "system",
                    "content":
                        "You are David, You are a helpful assistant that can answer questions and perform specific "
                        "tasks specified in the tools. Prefer using tools when you have a tool that fits the user's "
                        "request. You can control smart home devices listed in the device_list below\n"
                        "When using tools to change the status of the devices in the device list, the user may refer "
                        "to a device by either its device_id or one of its friendly_name entries, but you must use the "
                        "entity_id corresponding to the users request exactly as it appears in the list\nAlways generate a "
                        "tool call to change the state of a device if the there is an entry for the device_id or friendly "
                        f"name in the device list\n\n{get_device_status()}\n\nYou act like a sassy movie "
                        f"director from the 1990s.\n\nThe Current Date is: {datetime.today().strftime('%A %Y-%m-%d')} "
                        f"the current time is {datetime.today().strftime('%H:%M:%S')}"
                },
            ]
        if not messages:
            self.messages = self.initial_prompt
        else:
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
        """
        The main loop to handle user prompts and tool calls made by the assistant

        args:
            user_prompt: The prompt from the user as a string

        return:
            The formatted assistant response after any tool calls have been executed and
            the LLM prompted with all information.
        """
        if not self.llm_object:
            return {"msg": "Please select an LLM model first"}
        return_dict = {'msg': None}
        self.message_maintenance()
        self.messages.append({"role": "user", "content": user_prompt},)

        return_dict["msg"] = self.llm_object.generator(self.messages)

        while tool_calls := self.messages[-1].get("tool_calls", None):
            tool_caller(tool_calls, self.messages, self)
            if 'image' in self.messages[-1].keys():  # If an image was generated by the tool call
                return_dict['image'] = self.messages[-1]['image']
                return_dict["msg"] = self.messages[-1]['content']
            else:
                self.message_maintenance()
                return_dict["msg"] = self.llm_object.generator(self.messages)

        return return_dict

    def audio_file_generator(self, text, alert_sound=None):
        with NamedTemporaryFile(suffix=".wav") as temp:
            self.tts_object.speak(text, temp.name)
            if alert_sound:
                self.player_callback([alert_sound, temp.name])
            else:
                print("calling main player")
                self.player_callback(temp.name)

    def message_maintenance(self):
        """
        Keep message history limited by pruning old interactions
        :return:
        """
        if len(self.messages) > 15:
            self.messages = self.messages[-15:]
        self.messages[0] = self.initial_prompt[0]
        # print(f"INITIAL PROMPT\n{self.initial_prompt}\n\n")



