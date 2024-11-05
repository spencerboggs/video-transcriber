import os
import whisper
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

def transcribe_video(video_path, output_txt="transcript.txt", create_wav=True):
    model = whisper.load_model("base")
    wav_folder = "wav_files"
    os.makedirs(wav_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(wav_folder, f"{base_name}.wav") if create_wav else None

    with VideoFileClip(video_path) as clip:
        if create_wav:
            clip.audio.write_audiofile(audio_path, codec="pcm_s16le")

    result = model.transcribe(audio_path) if create_wav else model.transcribe(clip.audio)
    formatted_transcript = []
    subtitles = []
    for segment in result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip()
        formatted_transcript.append(f"[{start_time:.2f} - {end_time:.2f}] {text}")
        subtitles.append((start_time, end_time, text))

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(formatted_transcript))

    print(f"Transcription saved to {output_txt}")

    return subtitles

def create_srt(subtitles, output_srt="subtitles.srt"):
    with open(output_srt, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(subtitles, 1):
            start_time = format_time(start)
            end_time = format_time(end)
            f.write(f"{idx}\n{start_time} --> {end_time}\n{text}\n\n")
    print(f"Subtitles saved to {output_srt}")

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_text_clip(text, clip_size, fontsize=24, color='white'):
    img = Image.new('RGBA', clip_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except IOError:
        font = ImageFont.load_default()

    max_width = clip_size[0] - 40
    lines = wrap_text(text, font, max_width)

    text_height = sum([draw.textbbox((0, 0), line, font)[3] - draw.textbbox((0, 0), line, font)[1] for line in lines])
    
    y_position = clip_size[1] - text_height - 30
    for line in lines:
        text_width = draw.textbbox((0, 0), line, font)[2] - draw.textbbox((0, 0), line, font)[0]
        x_position = (clip_size[0] - text_width) // 2
        draw.text((x_position, y_position), line, fill=color, font=font)
        y_position += draw.textbbox((0, 0), line, font)[3] - draw.textbbox((0, 0), line, font)[1] + 5

    return np.array(img)

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        width, _ = font.getbbox(test_line)[2], font.getbbox(test_line)[3]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def add_subtitles_to_video(video_path, subtitles, output_video="output_video.mp4"):
    with VideoFileClip(video_path) as clip:
        subtitle_clips = []
        for start, end, text in subtitles:
            subtitle_clips.append(((start, end), text))

        text_clips = []
        for (start, end), text in subtitle_clips:
            text_clip = generate_text_clip(text, clip.size, fontsize=50, color='white')
            text_clip = ImageClip(text_clip).set_pos('center').set_start(start).set_end(end)
            text_clips.append(text_clip)

        video = CompositeVideoClip([clip] + text_clips)
        video.write_videofile(output_video, codec="libx264", fps=clip.fps)
    print(f"Video with subtitles saved to {output_video}")


def main():
    os.makedirs("videos", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("wav_files", exist_ok=True)
    os.makedirs("subtitles", exist_ok=True)

    videos = [f for f in os.listdir("videos") if f.endswith((".mp4", ".mov"))]
    transcribed = [f for f in os.listdir("transcripts") if f.endswith(".txt")]
    
    transcription_count = 0
    for video in videos:
        transcript_filename = video.replace(".mp4", ".txt").replace(".mov", ".txt")
        if transcript_filename not in transcribed:
            print(f"Transcribing {video}")
            subtitles = transcribe_video(f"videos/{video}", f"transcripts/{transcript_filename}", True)
            create_srt(subtitles, f"transcripts/{video.replace('.mp4', '.srt').replace('.mov', '.srt')}")
            create_subtitles = input("Do you want to add subtitles to this video? (y/n): ").strip().lower() == 'y'
            if create_subtitles:
                subtitles_video_path = os.path.join("subtitles", f"{os.path.splitext(video)[0]}_with_subtitles.mp4")
                add_subtitles_to_video(f"videos/{video}", subtitles, subtitles_video_path)
            transcription_count += 1
        print("")

    if transcription_count == 0:
        print("No videos to transcribe")
    else:
        print(f"Transcribed {transcription_count} videos")

if __name__ == "__main__":
    main()
