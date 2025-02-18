import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

text = "fra poco arrivo, hai dormito questa notte? hai fatto colazione?"

# List available 🐸TTS models
# print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1.1").to(device)
# tts = TTS("tts_models/multilingual/multi-dataset/bark").to(device)

# tts = TTS("tts_models/it/mai_female/glow-tts").to(device)
# tts = TTS("tts_models/it/mai_female/vits").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
# wav = tts.tts(text=text, speaker_wav="ita.wav", language="it")
# Text to speech to a file
tts.tts_to_file(text=text, speaker_wav="ita.wav", language="it", file_path="output.wav")


# Generate speech
# tts.tts_to_file(text=text, speaker_wav="ita.wav", file_path="output.wav")