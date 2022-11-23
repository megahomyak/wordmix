from typing import Dict, List, Optional
import moviepy.editor
import json
from dataclasses import dataclass
import sounddevice

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
words: List[Word] = []
for word in raw_words:
    word = Word(**word, previous=last_word, next=None)
    if last_word is not None:
        last_word.next = word
    last_word = word
    words.append(word)

words_dict: Dict[str, List[Word]] = {}

for word in words:
    if abs(word.start_sec - word.end_sec) > 0.05:
        words_dict.setdefault(word.word.casefold(), []).append(word)

for word_list in words_dict.values():
    word_list.sort(key=lambda word: word.confidence, reverse=True)

script = open("script.txt").read()

result_parts = []

script_words = script.split()

for word in script_words:
    if word.casefold() not in words_dict:
        raise Exception(f'Word {word} is not found in the video!')

i = 0
while i < len(script_words):
    word = script_words[i]
    words_list = words_dict[word.casefold()]
    word_index = 0
    word = words_list[word_index]
    start = word.start_sec
    while True:
        words = []
        words.append(word.word)
        while word.next is not None and i + 1 < len(script_words) and word.next.word.casefold() == script_words[i + 1].casefold():
            i += 1
            word = word.next
            words.append(word.word)
        end = word.end_sec
        print(" ".join(words))
        print(f"{word_index + 1}/{len(words_list)}")
        inp = input('Select the word (numbers), tune the beginning mark (numbers with a sign), continue ("c") or play the clip (newline): ')
        if inp == "c":
            break
        elif inp == "":
            clip = video.audio.subclip(start, end)
            sound = clip.to_soundarray()
            sounddevice.play(sound)
        elif inp.startswith("+"):
            amount = float(inp[1:])
            if (start + amount) + 0.05 < end:
                start += amount
            else:
                print("The clip is too short already!")
        elif inp.startswith("-"):
            start -= float(inp[1:])
        else:
            word_index = int(inp) - 1
            word = words_list[word_index]
            start = word.start_sec
    while True:
        inp = input('Tune the end now, "c" to continue and newline to play: ')
        if inp == "c":
            break
        elif inp == "":
            clip = video.audio.subclip(start, end)
            sound = clip.to_soundarray()
            sounddevice.play(sound)
        elif inp.startswith("+"):
            end += float(inp[1:])
        elif inp.startswith("-"):
            amount = float(inp[1:])
            if start + 0.05 < (end - amount):
                end -= amount
            else:
                print("The clip is too short already!")
    result_parts.append(video.subclip(start, end))
    i += 1

moviepy.editor.concatenate_videoclips(result_parts).write_videofile("result.mp4")
