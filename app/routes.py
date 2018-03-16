import sys, os
from flask import render_template, send_file
from pydub import AudioSegment
from gtts import gTTS
from app import app
import config
if config.markov_len == 1:
    from .markov_gen_one import getLyrics
elif config.markov_len == 2:
    from .markov_gen_two import getLyrics

import time

curtime = -1

# prints verbose error messages
def debug(line):
    if config.verbose: 
        sys.stdout.write(line)
        sys.stdout.flush()

# used to time functions
def timeit():
    global curtime
    if config.verbose:
        if curtime == -1:
            curtime = time.time()
            return -1
        else:
            time_elapsed = time.time() - curtime
            curtime = -1
            return time_elapsed

@app.route('/')
def index():
    # generating lyrics
    debug("Generating lyrics...")
    timeit()
    lyr = getLyrics("raps_all.txt")
    debug(" done in {:f} seconds!\n".format(timeit()))
    generated = {'lyrics' : lyr}
    
    # text to speech
    debug("Converting text to speech...")
    timeit()
    tts = gTTS(text="    ".join(lyr), lang='en')
    tts.save("app/templates/rap.mp3")
    debug(" done in {:f} seconds!\n".format(timeit()))

    # overlay rap onto speech
    debug("Overlaying rap onto instrumental...")
    timeit()
    sound1 = AudioSegment.from_mp3("app/templates/rap.mp3") + 6
    sound2 = AudioSegment.from_mp3("app/templates/ultimate.mp3") - 1

    output = sound2.overlay(sound1,position=18500)
    output.export("app/templates/mixed_sounds.mp3", format="mp3")
    debug(" done in {:f} seconds!\n".format(timeit()))

    return render_template('index.html', title="Home",generated=generated)

