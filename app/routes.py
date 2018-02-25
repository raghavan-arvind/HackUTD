import sys, os
from flask import render_template
from app import app
from .markov_gen_one import getLyrics


@app.route('/')
def index():
    generated = {'lyrics' : getLyrics()}
    return render_template('index.html', title="Home",generated=generated)
