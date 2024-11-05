import os
import whisper
from moviepy.editor import VideoFileClip

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
    for segment in result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip()
        formatted_transcript.append(f"[{start_time:.2f} - {end_time:.2f}] {text}")

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(formatted_transcript))

    print(f"Transcription saved to {output_txt}")

def main():
    os.makedirs("videos", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("wav_files", exist_ok=True)
    
    videos = [f for f in os.listdir("videos") if f.endswith((".mp4", ".mov"))]
    transcribed = [f for f in os.listdir("transcripts") if f.endswith(".txt")]
    
    transcription_count = 0
    for video in videos:
        transcript_filename = video.replace(".mp4", ".txt").replace(".mov", ".txt")
        if transcript_filename not in transcribed:
            print(f"Transcribing {video}")
            create_wav = input("Do you want to create a WAV file for this video? (y/n): ").strip().lower() == 'y'
            transcribe_video(f"videos/{video}", f"transcripts/{transcript_filename}", create_wav)
            transcription_count += 1

    if transcription_count == 0:
        print("No videos to transcribe")
    else:
        print(f"\nTranscribed {transcription_count} videos")

if __name__ == "__main__":
    main()
