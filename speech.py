import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
import numpy as np
import queue

# Audio Processor for handling microphone input
class SpeechToTextProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
    
    def recv(self, frame):
        audio_data = np.frombuffer(frame.to_ndarray(), dtype=np.int16)
        self.audio_queue.put(audio_data)
        return frame

    def convert_speech_to_text(self):
        # Process audio from the queue
        if not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            audio_bytes = audio_data.tobytes()

            # Convert numpy array to AudioData
            audio = sr.AudioData(audio_bytes, 16000, 2)

            try:
                # Using Google's Web Speech API to recognize the speech
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Google Speech Recognition could not understand the audio"
            except sr.RequestError as e:
                return f"Could not request results from Google Speech Recognition service; {e}"

# Streamlit App
st.title("Real-time Speech to Text")

st.write("Click start and speak into your microphone. The app will convert your speech to text in real time.")

# Initialize the audio processor and start the WebRTC streamer
audio_processor = SpeechToTextProcessor()
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=lambda: audio_processor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
)

# Display recognized speech in real-time
if webrtc_ctx.state.playing:
    result = audio_processor.convert_speech_to_text()
    if result:
        st.write("Recognized Text:")
        st.text_area("Text Output", result)
