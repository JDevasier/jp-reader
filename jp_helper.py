import os
import pandas as pd
import numpy as np
import pykakasi
import re
import fugashi

class KanjiHelper():
    def __init__(self):
        # Load vocab
        self.load_vocab()
        self.kks = pykakasi.kakasi()
        self.fugashi = fugashi.Tagger()
        self.kanji_regex = re.compile("([一-龯]*)")
        
        return None

    def load_vocab(self, path="./resources/jp-6000.csv"):
        data = pd.read_csv(path).to_numpy()
        
        jlpt = data[:, 6]
        jp = data[:, 7]
        eng = data[:, 9]
        
        self.vocab = dict(zip(jp, eng))
        self.jlpt = dict(zip(jp, jlpt))

    def parse(self, text):
        filter_pos1 = set(["補助記号", "助詞", "助動詞"])
        fugashi_output = [w for w in self.fugashi(text) if w.feature.pos1 not in filter_pos1]
        seen = set(["い","き"])
        
        text_vocab = []
        
        for word in fugashi_output:
            if word.surface in seen or word.feature.lemma in seen:
                continue
            seen.add(word.surface)
            seen.add(word.feature.lemma)

            jlpt_n = 0
            eng = ""
            if word in self.vocab:
                jlpt_n = int(self.jlpt[word][-1])
                eng = self.vocab[word]
                
            elif word.feature.lemma in self.vocab:
                jlpt_n = int(self.jlpt[word.feature.lemma][-1])
                eng = self.vocab[word.feature.lemma]

            text_vocab.append({"word":word.surface, "eng":eng, "jlpt":jlpt_n, "pron":word.feature.pron})
            
        return text_vocab
    