result.mp4: sample.mp4 script.txt recognized_words.json make_the_result.py
	poetry run python make_the_result.py

recognized_words.json: sample.mp3 picovoice_token.txt extract_the_words.py
	poetry run python extract_the_words.py

sample.mp3: sample.mp4 extract_the_audio.py
	poetry run python extract_the_audio.py
