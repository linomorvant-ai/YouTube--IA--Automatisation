REQUIRED_TOP = [
    "title", "target_age", "duration_seconds", "style",
    "characters", "scenes", "thumbnail_prompt", "youtube"
]

REQUIRED_SCENE = [
    "id", "duration_seconds", "characters", "location",
    "action", "narration", "dialogue", "visual_prompt",
    "camera", "lighting", "style", "sound_effects",
    "music", "transition"
]

def validate_production(data):
    if not isinstance(data, dict):
        raise ValueError("Production must be a JSON object.")

    for key in REQUIRED_TOP:
        if key not in data:
            raise ValueError(f"Missing top-level key: {key}")

    scenes = data["scenes"]
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("scenes must be a non-empty list.")

    ids = []
    total = 0
    for scene in scenes:
        for key in REQUIRED_SCENE:
            if key not in scene:
                raise ValueError(f"Scene {scene.get('id')} missing {key}")
        ids.append(scene["id"])
        total += int(scene["duration_seconds"])

    if ids != list(range(1, len(ids) + 1)):
        raise ValueError("Scene IDs must be consecutive starting at 1.")

    if total < 30:
        raise ValueError("Total scene duration is too short.")

    yt = data["youtube"]
    for key in ["title", "description", "tags"]:
        if key not in yt:
            raise ValueError(f"Missing YouTube metadata: {key}")
