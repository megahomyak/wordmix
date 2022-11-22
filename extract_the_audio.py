import moviepy.editor

video = moviepy.editor.VideoFileClip("sample.mp4")
video.audio.write_audiofile("sample.mp3")  # type: ignore
