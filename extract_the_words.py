import pvleopard
import json

leopard = pvleopard.create(access_key=open("picovoice_token.txt").read())

_transcript, words = leopard.process_file("sample.mp3")

words_as_dicts = []

for word in words:
    words_as_dicts.append({
        "word": word.word,
        "confidence": word.confidence,
        "start_sec": word.start_sec,
        "end_sec": word.end_sec,
    })

json.dump(words_as_dicts, open("recognized_words.json", "w"))
