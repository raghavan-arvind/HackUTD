import markovify
import pickle
import pronouncing as p
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, help="The name of the input text")

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
            while i >= 0:
                if any(char.isdigit() for char in phones[i]):
                    if phones[i] in self.rhymeIndex:
                        self.rhymeIndex[phones[i]].add(word)
                    else:
                        self.rhymeIndex[phones[i]] = set([word])
                    break
                i -= 1

    def markovNext(self, word):
        if word not in self.markovIndex:
            raise RuntimeError
        choices = []
        for key in self.markovIndex[word]:
            for i in range(self.markovIndex[word][key]):
                choices.append(key)
        return random.choice(choices)

    #def getRhymes(self):
        
    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, "rb") as f:
            dump = pickle.load(f)
            self.markovIndex = dump.markovIndex
            self.rhymeIndex = dump.rhymeIndex


if __name__ == "__main__":
    args = parser.parse_args()
    
    index = RapIndex()

    print("Building rap index!")
    with open(args.input_file, "r") as f:
        for line in f:
            if line.strip() != "":
                words = line.split(" ")
                i = len(words) - 1
                while i > 0:
                    index.addMarkov(words[i].strip(), words[i-1].strip())
                    i -= 1
                index.addMarkov(words[i].strip(), "--")
            for word in line.strip().split():
                index.addRhyme(word)
    print(index.markovIndex)
