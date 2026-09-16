"""
Audio playback utilities.
"""
import os
import json
import asyncio
import tempfile
from pathlib import Path

from audiobook_modules.config import SOUNDS_DIR, DATA_DIR


# Load sound mapping
with open(DATA_DIR / "sound_effects.json", 'r', encoding='utf-8') as f:
    EFFECTS_DATA = json.load(f)

SOUND_MAP = {
    effect: data["file"]
    for effect, data in EFFECTS_DATA["sound_effects"].items()
}


async def play_sound_effect(effect_name: str, volume: float = 0.6) -> bool:
    """
    Play a sound effect using paplay.
    
    Args:
        effect_name: Name of the effect to play
        volume: Volume level (0.0 to 1.0)
        
    Returns:
        True if played successfully, False otherwise
    """
    sound_file = SOUND_MAP.get(effect_name)
    if not sound_file:
        print(f"⚠️ Sound effect not found in map: {effect_name}")
        return False
    
    full_path = SOUNDS_DIR / sound_file
    if not full_path.exists():
        print(f"⚠️ Sound file not found: {full_path}")
        return False
    
    paplay_volume = int(volume * 65536)
    
    try:
        proc = await asyncio.create_subprocess_exec(
            "paplay", f"--volume={paplay_volume}", str(full_path),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        return True
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")
        return False


async def play_audio_bytes(wav_bytes: bytes, volume: float = 1.5):
    """
    Play audio from WAV bytes using paplay with increased volume.
    
    Args:
        wav_bytes: WAV file data as bytes
        volume: Volume level (0.0 to 2.0, default 1.5 for louder output)
    """
    if not wav_bytes or len(wav_bytes) < 100:
        print("⚠️ No audio data to play")
        return
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        temp_path = f.name
    
    # Volume can exceed 1.0 for boost
    paplay_volume = int(min(volume, 2.0) * 65536)
    
    try:
        proc = await asyncio.create_subprocess_exec(
            "paplay", f"--volume={paplay_volume}", temp_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
    except Exception as e:
        print(f"⚠️ Error playing audio: {e}")
    finally:
        try:
            os.remove(temp_path)
        except:
            pass
