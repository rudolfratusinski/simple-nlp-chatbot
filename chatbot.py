#!/usr/bin/env python3

import time
import io
import os
import speech_recognition as sr
from wit import Wit
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play

start_time = time.time()
access_token = os.environ.get('WIT_AI_ACCESS_TOKEN')
wit_client = Wit(access_token)
tts_client = texttospeech.TextToSpeechClient()


def synthesize_text(text):
    print("Synthesizing expression: " + text + "..")

    input_text = texttospeech.types.SynthesisInput(text=text)

    # Names of voices can be retrieved with tts_client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-F',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(input_text, voice, audio_config)

    song = AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")
    play(song)


print("Initializing..." + str(time.time() - start_time))

r = sr.Recognizer()
m = sr.Microphone()

try:
    print("Adjusting ambience noise level..." + str(time.time() - start_time))
    with m as source: r.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Awaiting voice command..." + str(time.time() - start_time))
        with m as source: audio = r.listen(source)
        print("Voice sampling completed, sending to recognizer service..." + str(time.time() - start_time))
        try:
            # recognize speech using wit.ai + parse it with wit.ai NLP
            value = wit_client.speech(audio.get_wav_data(), None, {'Content-Type': 'audio/wav'})

            print("Recognizer service returned a result..." + str(time.time() - start_time))

            # we need some special handling here to correctly print unicode characters to standard output
            if str is bytes:  # this version of Python uses bytes for strings (Python 2)
                print("Recognizer returned {}".format(value).encode("utf-8"))
            else:  # this version of Python uses unicode for strings (Python 3+)
                print("Recognizer returned {}".format(value))

                print("Synthesizing an answer..." + str(time.time() - start_time))

                # Synthesizing back only what was recognized by recognizer. Print whole "value" dictionary to get info about NLP results.
                synthesize_text(value["_text"])

        except sr.UnknownValueError:
            print("Unknown value!")
        except sr.RequestError as e:
            print("Couldn't request results from Speech Recognition service; {0}".format(e))
except KeyboardInterrupt:
    pass
