import os
import pandas as pd
import numpy as np
import pykakasi
import re
import fugashi
import xml.etree.ElementTree as ET

class KanjiHelper():
    def __init__(self):
        # Load vocab
        # self.load_vocab()
        print("Loading vocab...")
        self.load_jmdict()
        self.load_jltp()
        
        self.kks = pykakasi.kakasi()
        self.fugashi = fugashi.Tagger()
        self.kanji_re = re.compile("([一-龯]+)")
        self.katakana_re = re.compile("([ァ-ン]+)")
        
        return None

    def load_jmdict(self, path="./resources/JMdict_e"):
        root = ET.parse(path).getroot()
        self.vocab = {}
        
        for entry in root.findall("entry"):
            kebs = entry.findall(".//keb")
            rebs = entry.findall(".//reb")
            trans = [x.text for x in entry.findall(".//gloss")]
            if kebs == None or len(kebs) == 0:
                for reb in rebs:
                    self.vocab[reb.text] = trans
                
            else:
                for keb in kebs:
                    self.vocab[keb.text] = trans

    def load_vocab(self, path="./resources/jp-6000.csv"):
        data = pd.read_csv(path).to_numpy()
        
        jp = data[:, 7]
        eng = data[:, 9]
        
        self.vocab = dict(zip(jp, eng))
        
    def load_jltp(self, path="./resources/jp-6000.csv"):
        data = pd.read_csv(path).to_numpy()
        
        jlpt = data[:, 6]
        jp = data[:, 7]
        
        self.jlpt = dict(zip(jp, jlpt))

    def parse(self, text):
        content_html = ""
        text_vocab = []
        seen = ["い", "し"]
        
        for para in text.split("\n"):
            if para != "":
                para_vocab, para_html = self.parse_linear(para, seen, text_vocab)
                content_html += f"<p class='jp-text content-text'>{para_html}</p>"
        
        return {"content":content_html, "vocab":text_vocab}
    
    # parsing by groups is really clunky, often splits kanji and doesnt cover all words
    def parse_linear(self, text):
        html = ""
        text_vocab = []
        seen = set([])
        
        # Add ている because it is flagged as a verb and it will be VERY common
        if "ている" in text or "ていない" in text or "ています" in text or "ていません" in text:
            seen.add("い")
            seen.add("し")
            text_vocab.append({"word":"居る", "eng":"~ing", "jlpt":5, "pron":"~ている"})

        for para in text.split("\n"):
            html += f"<p class='jp-text content-text'>"

            # Now, go through each word, if it is a
            for word in self.fugashi(para):
                # Filter some things we dont want to highlight, but still want in the text
                # These are usually numbers, punctuation marks, decimals, etc.
                if word.feature.pos2 in set(["数詞", "句点", "読点", "補助記号"]) or word.surface in set(["％"]):
                    html += word.surface
                    continue
                    
                # while this is ugly af and could easily be made more clear 
                # with an "if x in y", this allows more flexibility
                if word.feature.pos1 == "接頭辞":   # prefix
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":f"{word.surface}~", "eng":eng, "jlpt":jlpt, "pron":pron})
                        
                    html += f"<a class='vocab-word word-prefix vocab-{word.surface}'>{word.surface}</a>"
                elif word.feature.pos1 == "接尾辞": # suffix
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":f"~{word.surface}", "eng":eng, "jlpt":jlpt, "pron":pron})
                        
                    html += f"<a class='vocab-word word-suffix vocab-{word.surface}'>{word.surface}</a>"
                elif word.feature.pos1 == "名詞":   # noun
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":word.surface, "eng":eng, "jlpt":jlpt, "pron":pron})
                        
                    html += f"<a class='vocab-word word-noun vocab-{word.surface}'>{word.surface}</a>"
                elif word.feature.pos1 == "動詞":   # verb
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":word.surface, "eng":eng, "jlpt":jlpt, "pron":pron, "lemma":word.feature.lemma})
                    
                    html += f"<a data-lemma='{word.feature.lemma}' class='vocab-word word-verb vocab-{word.feature.lemma}'>{word.surface}</a>"
                elif word.feature.pos1 == "形容詞": # adjective
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":word.surface, "eng":eng, "jlpt":jlpt, "pron":pron, "lemma":word.feature.lemma})
                    
                    html += f"<a class='vocab-word word-adjective vocab-{word.surface}'>{word.surface}</a>"
                elif word.feature.pos1 == "副詞": # adjective
                    jlpt = self.get_jlpt(word)
                    pron = self.get_pron(word)
                    eng = self.get_translation(word)
                    
                    if word.surface not in seen:
                        seen.add(word.surface)
                        text_vocab.append({"word":word.surface, "eng":eng, "jlpt":jlpt, "pron":pron, "lemma":word.feature.lemma})
                    
                    html += f"<a class='vocab-word word-adverb vocab-{word.surface}'>{word.surface}</a>"
                else:
                    html += word.surface
            
            html += "</p>"
            
        return {"content":html, "vocab":text_vocab}
        
    def get_jlpt(self, word):
        if isinstance(word, fugashi.fugashi.UnidicNode):
            if word.surface in self.jlpt:
                return int(self.jlpt[word.surface][-1]) + 1
            elif word.feature.lemma in self.jlpt:
                return int(self.jlpt[word.feature.lemma][-1]) + 1
        else:
            if word.surface in self.jlpt:
                return int(self.jlpt[word.surface][-1]) + 1
        
        return 0
            
    def get_pron(self, word):
        return "".join([x["hira"] for x in self.kks.convert(word.surface)])
    
    def get_translation(self, word):
        if isinstance(word, fugashi.fugashi.UnidicNode):
            if word.surface in self.vocab:
                return self.vocab[word.surface]
            elif word.feature.lemma in self.vocab:
                return self.vocab[word.feature.lemma]
        else:
            if word in self.vocab:
                return self.vocab[word]
        return ""
    
    def parse_basic(self, text):
        remaining_text = text
    
        seen = set(["い", "し"])
        text_vocab = []
        
        # Parse katakana groups (easiest, simplest)
        katakana_groups = [x for x in self.katakana_re.findall(text) if len(x) > 0]
        for word in katakana_groups:
            if word not in seen and word in self.vocab:
                seen.add(word)
                remaining_text = remaining_text.replace(word, "")
                
                jlpt_n = 0
                
                if word in self.jlpt:
                    jlpt_n = int(self.jlpt[word][-1]) + 1
                elif not isinstance(word, str) and word.feature.lemma in self.jlpt:
                    jlpt_n = int(self.jlpt[word.feature.lemma][-1]) + 1
                
                pron = self.kks.convert(word)[0]["hira"]
                
                text_vocab.append({"word":word, "eng":self.vocab[word], "jlpt":jlpt_n, "pron":pron})
        
        kanji_groups = [x for x in self.kanji_re.findall(remaining_text) if len(x) > 0]
        for word in kanji_groups:
            if word not in seen and word in self.vocab:
                seen.add(word)
                remaining_text = remaining_text.replace(word, "")
                
                jlpt_n = 0
                
                if word in self.jlpt:
                    jlpt_n = int(self.jlpt[word][-1]) + 1
                elif not isinstance(word, str) and word.feature.lemma in self.jlpt:
                    jlpt_n = int(self.jlpt[word.feature.lemma][-1]) + 1
                
                pron = self.kks.convert(word)[0]["hira"]
                
                text_vocab.append({"word":word, "eng":self.vocab[word], "jlpt":jlpt_n, "pron":pron})
        
        
        # Nouns are hard because they can be kanji, kanji + hira, or just hira (katakana dealt with above)
        # So lets process all the nouns next, except numerical, and % tokens
        # for noun in [x for x in self.fugashi(text) if x.feature.pos1 == "名詞" and x.feature.pos2 != "数詞" and x.surface != "％"]:
        #     if noun.surface not in seen and noun.surface in self.vocab:
        #         seen.add(noun.surface)
        #         remaining_text = remaining_text.replace(noun.surface, "")
                
        #         jlpt_n = 0
                
        #         if noun.surface in self.jlpt:
        #             jlpt_n = int(self.jlpt[noun.surface][-1]) + 1
        #         elif not isinstance(noun.surface, str) and noun.feature.lemma in self.jlpt:
        #             jlpt_n = int(self.jlpt[noun.feature.lemma][-1]) + 1
                
        #         pron = self.kks.convert(noun.surface)[0]["hira"]
                
        #         text_vocab.append({"word":noun.surface, "eng":self.vocab[noun.surface], "jlpt":jlpt_n, "pron":pron})

        # Since verbs are conjugated with kanji + hiragana, we want to parse them together
        # for verb in [w for w in self.fugashi(text) if w.feature.pos1 == "動詞"]:
        #     if (verb.surface in self.vocab and verb.surface not in seen) or \
        #         (verb.feature.lemma in self.vocab and verb.feature.lemma not in seen):
                
        #         # add to list of words
        #         if verb.surface in self.jlpt:
        #             jlpt_n = int(self.jlpt[verb.surface][-1]) + 1
        #         elif verb.feature.lemma in self.jlpt:
        #             jlpt_n = int(self.jlpt[verb.feature.lemma][-1]) + 1
                    
        #         if verb.surface in self.vocab:
        #             eng = self.vocab[verb.surface]
        #         else:
        #             eng = self.vocab[verb.feature.lemma]
                    
        #         pron = self.kks.convert(verb.surface)[0]["hira"]

        #         text_vocab.append({"word":verb.surface, "eng":eng, "jlpt":jlpt_n, "pron":pron})
                
        #         # mark verb, verb lemma, and its root kanji as seen
        #         seen.add(verb.surface)
        #         seen.add(verb.feature.lemma)
                
        #         for kanji in self.kanji_re.findall(verb.surface):
        #             seen.add(kanji) # add kanji (root) to seen
        
        # Some kanji are made up of other kanji in the sentence, i.e., 文部科学省 has 文部 and 科学
        # This will end up splitting long words
        
        return text_vocab
            
    def parse_old(self, text):
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
            jp = ""
            
            if word in self.jlpt:
                jlpt_n = int(self.jlpt[word][-1]) + 1
            elif word.feature.lemma in self.jlpt:
                jlpt_n = int(self.jlpt[word.feature.lemma][-1]) + 1
            
            if word in self.vocab:
                eng = self.vocab[word]
                jp = word
            elif word.feature.lemma in self.vocab:
                eng = self.vocab[word.feature.lemma]
                jp = word.feature.lemma

            
            pron = self.kks.convert(jp)[0]["hira"]
            
            text_vocab.append({"word":jp, "lemma":word.feature.lemma, "eng":eng, "jlpt":jlpt_n, "pron":pron})
            
        return text_vocab
    