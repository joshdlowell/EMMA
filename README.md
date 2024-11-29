# Speech-to-Speech ChatBot Example

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://echobot-whisper-gtts.streamlit.app/)

Example of a ChatBot able to receive either a voice message or a text message as a prompt and reply with a text message and a voice message.

Follow me [@alonsosilva](https://twitter.com/alonsosilva)

<a href="https://www.buymeacoffee.com/alonsosilva" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

# EMMA (Enhanced Multimodal Model Assistant)
Enhanced: Because of the audio web interface
Model: for the Local AI/LLM model
Multimodal: For multiple model integration
Assistant: for the interactive interface

This is a project that I built for myself it is designed to run on a GPU with 8Gb VRAM (or more).
To achieve this, some models are unloaded to make room for others when space is required. This causes
slower responses when calling functions that need different, larger, models and when returning to 
"normal" operation afterward. I have attempted to limit the impact as much as possible

# Tools

## Weather tool
The weather tool calls the [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
which provides weather forecast data for U.S. locations by grid coordinate.
The tool takes the location by name, and performs a lookup for the grid coordinates in a local CSV downloaded from
https://simplemaps.com/data/us-cities. I didn't want to use a web API for this. However, this implementation using
NWS and us-cities data does limit the weather tool to U.S. locations.

# Install

## Install Nvidia drivers for your GPU

'pip install -r requirements.txt'

'python setup.py install'


# Or run the docker containers

with gpu
install NVIDIA container toolkit
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

verify GPUs are accessible from inside the container environment
'docker run --gpus all nvidia/cuda:12.0-base nvidia-smi'

'docker run --gpus all tensorflow/tensorflow:latest-gpu'

to specify multiple containers use 'nvidia-smi' to identify your GPU device numbers and pass them as a comma
separated list

'docker run -it --rm --gpus '"device=0,2"' tensorflow/tensorflow:latest-gpu nvidia-smi'

# TODO list

1. Make audio playback quicker with partial generation - DONE
2. Complete weather tools - Basic funcs DONE
3. Add image generation - 
4. Add Timer tools
5. Add interrupt capability button
6. Add interrupt capability voice
7. Add home assistant integration
8. Create Satellite for full assistant integration