import os
import sys
import yaml
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .agent/.env
# Assuming the script runs from the project root or tools/ folder
env_path = Path(__file__).parent.parent / '.agent' / '.env'
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .agent/.env")
    print("Please add your API key to the .env file.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_video(video_path, output_path=None):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    print(f"🎬 Processing video: {video_path}")
    
    # Upload the video file
    print("📤 Uploading video to Gemini...")
    video_file = client.files.upload(file=video_path)
    print(f"✅ Uploaded: {video_file.name}")

    # Wait for the file to be processed
    print("⏳ Waiting for processing...")
    while video_file.state == "PROCESSING":
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)
    
    if video_file.state == "FAILED":
        print("❌ Video processing failed.")
        return

    print("🧠 Analyzing video content with SEALCaM framework...")
    
    prompt = """
    Analyze the provided video using the SEALCaM framework. Break down the video into scenes and for each scene, provide:
    - scene: identifier (e.g., Scene 1)
    - description: brief scene summary
    - subject: the main focus of the scene
    - environment: the setting/background
    - action: what motion or physical events occur
    - lighting: the lighting style and mood
    - camera: the camera angle and movement
    - duration: approximate duration in seconds

    Also, provide an overall 'audio' section describing any music, sound effects, or voiceovers heard throughout the video.

    Output the entire analysis EXCLUSIVELY in YAML format.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    types.Part.from_text(text=prompt),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
        ),
    )

    # Clean the response to ensure only YAML is present
    yaml_content = response.text.strip()
    if yaml_content.startswith("```yaml"):
        yaml_content = yaml_content[7:-3].strip()
    elif yaml_content.startswith("```"):
        yaml_content = yaml_content[3:-3].strip()

    print("\n✨ Analysis Complete!")
    print("-" * 30)
    print(yaml_content)
    print("-" * 30)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(yaml_content)
        print(f"💾 Analysis saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_video.py <video_path> [output_path]")
        sys.exit(1)

    video_input = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    analyze_video(video_input, output_file)
