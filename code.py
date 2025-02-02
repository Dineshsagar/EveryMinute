import soundcard as sc
import soundfile as sf
from easygui import msgbox, buttonbox, fileopenbox, filesavebox
import speech_recognition as sr
import threading
import numpy as np
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from datetime import datetime  # Importing datetime to get the current timestamp

def format_transcription(text):
    """Format the transcription with punctuation and new lines."""
    sentences = text.split('. ')
    formatted_text = ""

    for i, sentence in enumerate(sentences):
        formatted_text += sentence.strip() + '. '
        if (i + 1) % 3 == 0:  # Add a newline every three sentences
            formatted_text += "\n\n"

    return formatted_text.strip()

def welcome_screen():
    """Display the welcome screen."""
    msgbox('\n', title='DScribe! V1.0', ok_button="Let's Start!",
           image='C:\\Users\\dinesh.sagar\\OneDrive - Advance Auto Parts\\Desktop\\Screenshot 2025-02-02 125329.png')

def record_audio():
    """Record audio from the microphone."""
    OUTPUT_FILE_NAME = "out.wav"
    SAMPLE_RATE = 48000  # Sampling rate
    RECORD_SEC = 100000  # Duration of recording in seconds

    audio_data = []
    stop_recording = False

    def record_thread(data, is_running):
        """Thread function to record audio data."""
        i = 0
        while i < RECORD_SEC and is_running():
            data.append(mic.record(numframes=SAMPLE_RATE))
            i += 1

    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
        recording_thread = threading.Thread(target=record_thread, args=(audio_data, lambda: not stop_recording))
        recording_thread.start()

        while recording_thread.is_alive():
            if buttonbox("I'm Listening.....", title='DScribe! V1.0', choices=["Stop Recording"],
                         image='C:\\Users\\dinesh.sagar\\OneDrive - Advance Auto Parts\\Desktop\\images.png') == "Stop Recording":
                stop_recording = True
                recording_thread.join()
                audio_data = np.concatenate(audio_data, axis=0)
                sf.write(file=OUTPUT_FILE_NAME, data=audio_data, samplerate=SAMPLE_RATE)
                return OUTPUT_FILE_NAME

def convert_audio_to_text(output_file_name):
    """Convert audio to text and return the transcribed text."""
    r = sr.Recognizer()
    with sr.AudioFile(output_file_name) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        msgbox("Google Speech Recognition could not understand audio", title='Error')
        return None
    except sr.RequestError as e:
        msgbox(f"Could not request results from Google Speech Recognition service; {e}", title='Error')
        return None

def save_text_to_file(text):
    """Save the transcribed text to a file with timestamp and label."""
    text_file_name = filesavebox("Save recognized text as", default="recognized_text.txt")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
    content = f"{current_time} - DScribe! - Pre-Release-Version\n{text}"
    content1 = "Here is the summarized version of session:\n"  # Create the content to write

    with open(text_file_name, "w") as text_file:
        text_file.write(content)
    msgbox(f"Text saved as {text_file_name}", title='Text Conversion Successful')

def summarize_text(text):
    """Summarize the text using Sumy."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()  # You can choose other summarizers like LexRankSummarizer
    summary = summarizer(parser.document, sentences_count=3)  # Adjust number of sentences in summary
    return ' '.join(str(sentence) for sentence in summary)

def main():
    """Main function to run the application."""
    welcome_screen()
    
    while True:
        if buttonbox(title='DScribe! V1.0',
                     choices=["Start Recording", "Exit"],
                     image='C:\\Users\\dinesh.sagar\\OneDrive - Advance Auto Parts\\Desktop\\Speech to text (1).jpg') == "Start Recording":
            output_file_name = record_audio()
            msgbox(f"Audio is saved as {output_file_name} and converting audio to text... \n\n Please expect the transcription to be ready in 2-5 Minutes. \n You will get a prompt once it is ready.", 
                   title='Recording Successful - Processing', ok_button='Okay!', 
                   image='C:\\Users\\dinesh.sagar\\OneDrive - Advance Auto Parts\\Desktop\\Lastpage.jpg')

            text = convert_audio_to_text(output_file_name)
            if text:
                formatted_text = format_transcription(text)
                save_text_to_file(formatted_text)
                summarized_text = summarize_text(formatted_text)
                msgbox(f"Summarized Text:\n{summarized_text}", title='Summarized Text')

        else:
            break

if __name__ == "__main__":
    main()
