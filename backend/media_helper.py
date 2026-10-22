"""Optional per-beat stock clips from Pexels (requires PEXELS_API_KEY in backend/.env)."""
import hashlib, json, os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from storyboard_helper import _load_env

MAX_CLIP_BYTES = 40 * 1024 * 1024


def _search_clip(query: str, api_key: str):
    url = "https://api.pexels.com/videos/search?" + urlencode({"query": query, "orientation": "landscape", "per_page": 3})
    req = Request(url, headers={"Authorization": api_key, "User-Agent": "AdventTech/2.0"})
    with urlopen(req, timeout=12) as response:
        videos = json.loads(response.read().decode("utf-8")).get("videos") or []
    for video in videos:
        files = [f for f in (video.get("video_files") or []) if f.get("link") and f.get("file_type") == "video/mp4"]
        files.sort(key=lambda f: (f.get("width", 0) >= 1280, f.get("width", 0)), reverse=True)
        chosen = next((f for f in files if f.get("width", 0) >= 640), files[0] if files else None)
        if chosen:
            return chosen["link"]
    return None


def attach_clips(beats, folder):
    """Add `video_path` and `video_source` to each beat that finds a clip. Other beats keep the cause artwork."""
    _load_env()
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if not api_key:
        return beats
    target_dir = Path(folder)
    target_dir.mkdir(parents=True, exist_ok=True)
    for index, beat in enumerate(beats):
        query = " ".join(str(beat.get("image_query", "")).split()[:9])
        try:
            link = _search_clip(query, api_key)
            if not link:
                continue
            with urlopen(Request(link, headers={"User-Agent": "AdventTech/2.0"}), timeout=25) as response:
                content = response.read(MAX_CLIP_BYTES + 1)
            if len(content) > MAX_CLIP_BYTES or len(content) < 10000:
                continue
            path = target_dir / f"{beat['id']}-{hashlib.md5(query.encode()).hexdigest()[:6]}.mp4"
            path.write_bytes(content)
            beat["video_path"] = str(path.resolve())
            beat["video_source"] = "Pexels"
        except Exception as exc:
            print(f"Stock clip skipped for beat {beat.get('id', index)}: {exc}")
    return beats


ART_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
ASSET_DIR = Path(__file__).resolve().parent / "assets" / "cause-art"


def find_cause_art(cause: str, beat_id: str):
    """Predefined template artwork. Drop files in backend/assets/cause-art/ as food-intro.jpg, food.jpg, etc."""
    for name in (f"{cause}-{beat_id}", cause):
        for ext in ART_EXTENSIONS:
            candidate = ASSET_DIR / f"{name}{ext}"
            if candidate.exists():
                return str(candidate.resolve())
    return None


CLOSING_DIR = Path(__file__).resolve().parent / "assets" / "closing"


def find_closing_art(cause: str, style: str):
    """Predefined closing card (logo, spotlight title, AI disclosure). QR is added on top at render time.
    Drop files in backend/assets/closing/ as food-premium.png, premium.png or closing.png."""
    for name in (f"{cause}-{style}", style, "closing"):
        for ext in ART_EXTENSIONS:
            candidate = CLOSING_DIR / f"{name}{ext}"
            if candidate.exists():
                return str(candidate.resolve())
    return None
