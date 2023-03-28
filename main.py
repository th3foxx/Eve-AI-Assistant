import os
import openai
import speech_recognition as sr
from google.cloud import texttospeech
import pygame
import uuid

# Установите ваш API-ключ для Google Cloud здесь
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "here"

openai.api_key = "here"

assistant_name = "Eve AI"
assistant_name_base = "Eve"

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message['content']


def text_to_speech(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ru-RU", name="ru-RU-Wavenet-C"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    file_name = f"{uuid.uuid4()}.mp3"
    with open(file_name, "wb") as fp:
        fp.write(response.audio_content)

    pygame.mixer.init()
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    os.remove(file_name)


def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print("Скажите что-нибудь...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ru-RU")
            print("Вы сказали: {}".format(text))
            return text
        except Exception as e:
            print("Извините, я не понял. Повторите, пожалуйста.")
            return None


def main():
    print(f"Привет! Я {assistant_name}. Чем могу помочь?")
    text_to_speech(f"Привет! Я {assistant_name}. Чем могу помочь?")
    while True:
        input_text = speech_to_text()
        if input_text:
            if assistant_name_base.lower() in input_text.lower():
                if "благодарю за помощь" in input_text.lower() or "пока" in input_text.lower():
                    print(f"Пока! Если понадобится помощь, обращайтесь к {assistant_name}!")
                    text_to_speech(f"Пока! Если понадобится помощь, обращайтесь к {assistant_name}!")
                    break

                prompt = f"User: {input_text}\nAssistant: "
                response = generate_response(prompt)
                print(f"{assistant_name}: {response}")
                text_to_speech(response)
        else:
            continue


if __name__ == "__main__":
    main()