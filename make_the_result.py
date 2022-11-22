from typing import Dict, List, Optional
import moviepy.editor
import json
from dataclasses import dataclass

video = moviepy.editor.VideoFileClip("sample.mp4")

@dataclass
class Word:
    word: str
    confidence: float
    start_sec: float
    end_sec: float
    previous: Optional["Word"]
    next: Optional["Word"]

    def __repr__(self):
        return f"Word(word={self.word!r}, confidence={self.confidence!r}, start_sec={self.start_sec!r}, end_sec={self.end_sec!r})"

raw_words = json.load(open("recognized_words.json"))

last_word: Optional[Word] = None
words = []
for word in raw_words:
    word = Word(**word, previous=last_word, next=None)
    if last_word is not None:
        last_word.next = word
    last_word = word
    words.append(word)

words_dict: Dict[str, List[Word]] = {}

for word in words:
    words_dict.setdefault(word.word.casefold(), []).append(word)

for word_list in words_dict.values():
    word_list.sort(key=lambda word: word.confidence, reverse=True)

script = open("script.txt").read()

result_parts = []

script_words = script.split()

i = 0
while i < len(script_words):
    word = script_words[i]
    word = words_dict[word.casefold()][0]
    start = 0 if word.previous is None else word.previous.end_sec
    while True:
        end = word.end_sec
        if word.next is not None and i + 1 < len(script_words) and word.next.word.casefold() == script_words[i + 1].casefold():
            i += 1
            word = word.next
        else:
            break
    result_parts.append(video.subclip(start, end))
    i += 1

moviepy.editor.concatenate_videoclips(result_parts).write_videofile("result.mp4")
