import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

class MusicGenEngine:
	def __init__(self, model_name="facebook/musicgen-small", device="cpu"):
		self.device = device
		self.model_name = model_name
		self.processor = AutoProcessor.from_pretrained(self.model_name)
		self.model = MusicgenForConditionalGeneration.from_pretrained(self.model_name).to(self.device)

	def generate_music(self, prompt, duration=30, parameters=None):
		inputs = self.processor(text=prompt, padding=True, return_tensors="pt")
		inputs = {k: v.to(self.device) for k, v in inputs.items()}
		with torch.no_grad():
			audio_tensor = self.model.generate(**inputs, max_new_tokens=duration * 50)  # Approx 50 tokens/sec
		return audio_tensor

	def tensor_to_wav(self, audio_tensor, filename="output.wav"):
		import soundfile as sf
		arr = audio_tensor.cpu().numpy()
		arr = arr.squeeze()
		sf.write(filename, arr, 32000)
		return filename

	def wav_to_mp3(self, wav_path, mp3_path="output.mp3"):
		from pydub import AudioSegment
		AudioSegment.converter = r"C:\\Users\\ABHINAY\\Downloads\\ffmpeg-8.0-essentials_build\\ffmpeg-8.0-essentials_build\\bin\\ffmpeg.exe"
		audio = AudioSegment.from_wav(wav_path)
		audio.export(mp3_path, format="mp3")
		return mp3_path
