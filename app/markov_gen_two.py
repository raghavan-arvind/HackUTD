import markovify
import pickle
import pronouncing as p
import argparse
import random

random.seed(1)

input_file = "raps_all.txt"

LINE_LENGTH = [6, 9]

class RapIndex:
    def __init__(self):
        self.rhymeIndex = dict()
        self.markovIndex = dict()


    def addMarkov(self, key1, key2, value):
        key = key1 + "," + key2
        if key in self.markovIndex:
            if value in self.markovIndex[key]:
                self.markovIndex[key][value] += 1
            else:
                self.markovIndex[key][value] = 1
        else:
            entry = dict()
            entry[value] = 1
            self.markovIndex[key] = entry
    
    def addRhyme(self, word1, word2):
        word = word1 + "," + word2
        if len(word1) == 1 and word1 not in 'ia':
            return

        phones = p.phones_for_word(word1)
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

    def markovNext(self, word1, word2, no_stop=False, always_stop=False):
        word = word1+","+word2
        
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
                if returnList[0].split(',')[0] == returnList[1].split(',')[0]:
                    return self.getRhymingWords(num=num)
                return returnList
        return None
    
    def getBars(self, numBars=2, exp_length=6):
        endWords = self.getRhymingWords(num=numBars)

        bars = []
        for word in endWords:
            current_word1,current_word2 = word.split(",")
            current_line = current_word2+" "+current_word1
            num_words = 2
            while current_word1 != '--':
                temp = ""
                if num_words < LINE_LENGTH[0]:
                    temp = self.markovNext(current_word1,current_word2, no_stop=True)
                elif num_words > LINE_LENGTH[1]:
                    temp = self.markovNext(current_word1,current_word2, always_stop=True)
                else:
                    temp = self.markovNext(current_word1,current_word2)
                if temp != '--':
                    current_line = temp + " " + current_line
                    current_word1 = current_word2
                    current_word2 = temp
                else:
                    break
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
    index = RapIndex()

    #print("Building rap index!")
    with open(input_file, "r") as f:
        for line in f:
            line = line.replace("\s+", " ")
            if line.strip() != "":
                words = line.split(" ")
                i = len(words) - 1
                if i > 0:
                    index.addRhyme(words[i].strip(), words[i-1].strip())
                while i > 1:
                    index.addMarkov(words[i].strip(), words[i-1].strip(), words[i-2].strip())
                    i -= 1
                index.addMarkov(words[i].strip(), words[i-1].strip(), "--")

    #index.save("index.ind")
    lyrics = []
    lyrics.extend(index.getBars(numBars=2))
    lyrics.extend(index.getBars(numBars=2))
    lyrics.extend(index.getBars(numBars=2))
    lyrics.extend(index.getBars(numBars=2))
    return lyrics

if __name__ == "__main__":
    index = RapIndex()

    print("Building rap index!")
    with open(input_file, "r") as f:
        for line in f:
            line = line.replace("\s+", " ")
            if line.strip() != "":
                words = line.split(" ")
                i = len(words) - 1
                # BUG
    #print("saving index...")
    #index.save('index.ind')


    print(index.markovIndex)
    for i in range(2):
        bars = index.getBars(numBars=2)
        print(bars[0]+'\n'+bars[1])
