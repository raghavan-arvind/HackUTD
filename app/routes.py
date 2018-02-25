import sys, os
from flask import render_template, send_file
from pydub import AudioSegment
from gtts import gTTS
from app import app
from .markov_gen_one import getLyrics


@app.route('/')
def index():
    lyr = getLyrics()
    generated = {'lyrics' : lyr}
    tts = gTTS(text="    ".join(lyr), lang='en')
    tts.save("app/templates/rap.mp3")
    sound1 = AudioSegment.from_mp3("app/templates/rap.mp3")
    sound2 = AudioSegment.from_mp3("app/templates/ultimate.mp3")

    output = sound2.overlay(sound1,position=20000)
    output.export("app/templates/mixed_sounds.mp3", format="mp3")

    return render_template('index.html', title="Home",generated=generated)

