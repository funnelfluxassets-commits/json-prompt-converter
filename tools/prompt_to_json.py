import json
import argparse
import re

# Mapping dictionaries for sorting basic prompts into JSON blocks
STYLE_MAPPING = {
    "cinematic": "ultra_photorealistic",
    "photorealistic": "ultra_photorealistic",
    "realistic": "standard",
    "anime": "anime_v6",
    "3d": "3d_render_octane",
    "raw": "raw",
    "retro": "1970s film grain"
}

LIGHTING_MAPPING = {
    "sunny": "bright direct sunlight",
    "golden hour": "soft warm sunset lighting",
    "neon": "cyberpunk neon glow",
    "studio": "professional studio lighting",
    "dim": "low-key atmospheric lighting",
    "dark": "highly shadowed, dramatic"
}

ASPECT_RATIOS = {
    "portrait": "9:16",
    "landscape": "16:9",
    "square": "1:1",
    "wide": "21:9"
}

HUMAN_KEYWORDS = ["man", "woman", "person", "girl", "boy", "human", "child", "model"]

def convert_prompt(basic_prompt):
    # Initialize JSON structure with defaults
    json_prompt = {
        "task": "Generate a high-quality visual still based on the description.",
        "parameters": {
            "subject": {
                "description": "",
                "made_out_of": "standard materials"
            },
            "background": {
                "setting": "neutral"
            },
            "lighting": "natural lighting",
            "style": "standard"
        },
        "meta": {
            "aspect_ratio": "16:9",
            "resolution": "2K",
            "quality": "standard",
            "negative_prompt": ["blur", "distorted", "watermark", "text", "bad anatomy"]
        }
    }

    words = basic_prompt.lower().split()
    clean_description = basic_prompt

    # 1. Detect Aspect Ratio
    for key, val in ASPECT_RATIOS.items():
        if key in basic_prompt.lower():
            json_prompt["meta"]["aspect_ratio"] = val
            clean_description = re.sub(rf"\b{key}\b", "", clean_description, flags=re.IGNORECASE)

    # 2. Detect Style/Quality
    for key, val in STYLE_MAPPING.items():
        if key in basic_prompt.lower():
            json_prompt["meta"]["quality"] = val
            json_prompt["parameters"]["style"] = key
            clean_description = re.sub(rf"\b{key}\b", "", clean_description, flags=re.IGNORECASE)

    # 3. Detect Lighting
    for key, val in LIGHTING_MAPPING.items():
        if key in basic_prompt.lower():
            json_prompt["parameters"]["lighting"] = val
            clean_description = re.sub(rf"\b{key}\b", "", clean_description, flags=re.IGNORECASE)

    # 4. Human Realism Trick ("made_out_of")
    if any(human in basic_prompt.lower() for human in HUMAN_KEYWORDS):
        json_prompt["parameters"]["subject"]["made_out_of"] = "organic skin, detailed pores, natural texture"

    # 5. Final Description Cleanup
    # Stripping extra spaces and punctuation
    clean_description = re.sub(r'\s+', ' ', clean_description).strip()
    json_prompt["parameters"]["subject"]["description"] = clean_description

    return json_prompt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a basic prompt to Nano Banana JSON.")
    parser.add_argument("prompt", type=str, help="The basic text prompt.")
    args = parser.parse_args()

    result = convert_prompt(args.prompt)
    print(json.dumps(result, indent=4))
