import markovify
import pickle
import os, sys
import pronouncing as p
import config
import random

input_file = 'raps_all.txt'

LINE_LENGTH = [5, 8]

# prints verbose error messages
def debug(line):
    if config.verbose: 
        sys.stdout.write(line)
        sys.stdout.flush()

class RapIndex:
    def __init__(self):
        self.rhymeIndex = dict()
        self.markovIndex = dict()


    def addMarkov(self, key, value):
        if key in self.markovIndex:
            if value in self.markovIndex[key]:
                self.markovIndex[key][value] += 1
            else:
                self.markovIndex[key][value] = 1
        else:
            entry = dict()
            entry[value] = 1
            self.markovIndex[key] = entry
    
    def addRhyme(self, word):
        if len(word) == 1 and word not in 'ia':
            return

        phones = p.phones_for_word(word)
        if len(phones) != 0:
            phones = phones[0].split(" ")
            i = len(phones) - 1
            stub = ""
            while i >= 0:
                if any(char.isdigit() for char in phones[i]):
                    if (stub+phones[i]) in self.rhymeIndex:
                        self.rhymeIndex[stub+phones[i]].add(word)
                    else:
                        self.rhymeIndex[stub+phones[i]] = set([word])
                    break
                stub += phones[i]
                i -= 1

    def markovNext(self, word, no_stop=False, always_stop=False):
        if word not in self.markovIndex:
            raise RuntimeError

        choices = []
        for key in self.markovIndex[word]:
            for i in range(self.markovIndex[word][key]):
                if no_stop and key == '--':
                    None # don't add
                else:
                    choices.append(key)
        if always_stop and '--' in choices:
            return '--'
        else:
            if len(choices) == 0:
                return '--'
            return random.choice(choices)

    def getRhymingWords(self, num=2):
        vowels = [key for key in self.rhymeIndex]
        while len(vowels) > 0:
            choice = random.choice(vowels)
            if len(self.rhymeIndex[choice]) < num:
                vowels.remove(choice)
            else:
                words = [word for word in self.rhymeIndex[choice]]
                returnList = []
                while len(returnList) < num:
                    wordChoice = random.choice(words)
                    returnList.append(wordChoice)
                    words.remove(wordChoice)
                return returnList
        return None
    
    def getBars(self, numBars=2, exp_length=6):
        endWords = self.getRhymingWords(num=numBars)

        bars = []
        for word in endWords:
            current_line = word
            current_word = word
            num_words = 1
            while current_word != '--':
                if num_words < LINE_LENGTH[0]:
                    current_word = self.markovNext(current_word, no_stop=True)
                elif num_words > LINE_LENGTH[1]:
                    current_word = self.markovNext(current_word, always_stop=True)
                else:
                    current_word = self.markovNext(current_word)
                if current_word != '--':
                    current_line = current_word + " " + current_line
                num_words += 1
            bars.append(current_line) 
        return bars


        
    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, "rb") as f:
            dump = pickle.load(f)
            self.markovIndex = dump.markovIndex
            self.rhymeIndex = dump.rhymeIndex


def getLyrics(input_file):
    # save current directory, switch to this file's directory
    curdir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    index = RapIndex()

    if os.path.isfile("index_one.ind"):
        index.load("index_one.ind")
    else:
        # Building rap index!
        with open(input_file, "r") as f:
            for line in f:
                line = line.replace("\s+", " ")
                if line.strip() != "":
                    words = line.split(" ")
                    i = len(words) - 1
                    if i > 0:
                        index.addRhyme(words[i].strip())
                    while i > 0:
                        index.addMarkov(words[i].strip(), words[i-1].strip())
                        i -= 1
                    index.addMarkov(words[i].strip(), "--")

        # Saving index
        index.save("index_one.ind")
    lyrics = []
    for i in range(4):
        lyrics.extend(index.getBars(numBars=2))

    # reset current directory
    os.chdir(curdir)
    return lyrics

if __name__ == '__main__':
    print(getLyrics(input_file))
