"""
Text processing utilities for audiobook reader.
"""
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# Load sound effects data
DATA_DIR = Path(__file__).parent / "data"

print(f"📂 Loading sound effects from: {DATA_DIR / 'sound_effects.json'}")

with open(DATA_DIR / "sound_effects.json", 'r', encoding='utf-8') as f:
    EFFECTS_DATA = json.load(f)

SOUND_EFFECTS = {
    effect: data["keywords"]
    for effect, data in EFFECTS_DATA["sound_effects"].items()
}

VOCAL_EFFECTS = {
    effect: data["keywords"]
    for effect, data in EFFECTS_DATA["vocal_effects"].items()
}

ONOMATOPOEIA = EFFECTS_DATA["onomatopoeia"]

print(f"✅ Loaded {len(SOUND_EFFECTS)} sound effects:")
for effect, keywords in SOUND_EFFECTS.items():
    print(f"   - {effect}: {keywords[:3]}{'...' if len(keywords) > 3 else ''}")


def detect_sfx_with_position(text: str) -> List[Tuple[str, int, int, str]]:
    """
    Detects sound effects in text and returns their positions.
    Returns: List of (effect_name, start_pos, end_pos, keyword)
    """
    detected = []
    
    print(f"    🔍 Scanning text for SFX...")
    
    for effect, keywords in SOUND_EFFECTS.items():
        for keyword in keywords:
            # Always use case-insensitive for flexibility
            pattern = re.escape(keyword)
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detected.append((effect, match.start(), match.end(), keyword))
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end]
                print(f"       ✓ '{keyword}' → {effect} at {match.start()}")
                print(f"         Context: ...{context}...")
    
    # Sort by position
    detected.sort(key=lambda x: x[1])
    
    # Remove overlapping detections
    filtered = []
    last_end = -1
    for item in detected:
        if item[1] >= last_end:
            filtered.append(item)
            last_end = item[2]
        else:
            print(f"       ⚠️ Skipped overlapping: {item[3]}")
    
    print(f"    📊 Total SFX detected: {len(filtered)}")
    return filtered


def detect_vocal_effect(text: str) -> Optional[str]:
    """Detects vocal effects like laugh, whisper, etc."""
    text_lower = text.lower()
    for effect, keywords in VOCAL_EFFECTS.items():
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', text_lower):
                return effect
    return None


def detect_emotion(text: str) -> Tuple[str, float]:
    """
    Detects emotion and returns (emotion_name, volume_multiplier).
    """
    text_lower = text.lower()
    vocal = detect_vocal_effect(text)
    
    # Vocal effects override
    if vocal:
        vocal_data = EFFECTS_DATA["vocal_effects"][vocal]
        return (vocal_data["emotion"], vocal_data["volume"])
    
    # Context-based emotion detection
    if any(w in text_lower for w in ["desesperado", "desespero", "pânico"]):
        return ("desperate", 1.5)
    if any(w in text_lower for w in ["!", "exclamou", "gritou"]):
        return ("excited", 1.3)
    if any(w in text_lower for w in ["cansado", "sonolento"]):
        return ("sleepy", 0.5)
    if any(w in text_lower for w in ["tristemente", "melancólico"]):
        return ("sad", 0.7)
    if any(w in text_lower for w in ["calmamente", "tranquilo"]):
        return ("calm", 0.7)
    
    return ("neutral", 0.9)


def split_text_by_sfx(text: str, sfx_positions: List[Tuple[str, int, int, str]]) -> List[Dict]:
    """
    Splits text into segments alternating between text and SFX.
    Removes the SFX keywords from narrated text to avoid duplication.
    """
    if not sfx_positions:
        return [{"type": "text", "content": text}]
    
    segments = []
    last_pos = 0
    
    for idx, (effect, start, end, keyword) in enumerate(sfx_positions):
        # Text before SFX (excluding the keyword itself)
        before_text = text[last_pos:start].strip()
        
        if before_text and is_speakable(before_text):
            # Clean up punctuation at start and end
            before_text = re.sub(r'^[!.?\s]+', '', before_text)
            before_text = re.sub(r'[!.?\s]+$', '', before_text)
            
            if before_text and len(before_text) > 2:
                segments.append({"type": "text", "content": before_text})
        
        # Add SFX
        segments.append({"type": "sfx", "effect": effect})
        
        # Skip keyword and trailing punctuation
        skip_end = end
        
        # Skip punctuation and whitespace on same line
        while skip_end < len(text) and text[skip_end] in '!?. \t':
            skip_end += 1
        
        # Skip single newline if present
        if skip_end < len(text) and text[skip_end] == '\n':
            skip_end += 1
            # Skip whitespace after newline
            while skip_end < len(text) and text[skip_end] in ' \t':
                skip_end += 1
        
        last_pos = skip_end
    
    # Text after last SFX
    after_text = text[last_pos:].strip()
    if after_text and is_speakable(after_text):
        after_text = re.sub(r'^[!.?\s]+', '', after_text)
        if after_text and len(after_text) > 2:
            segments.append({"type": "text", "content": after_text})
    
    return segments


def strip_pure_onomatopoeia(text: str) -> str:
    """Removes standalone onomatopoeia from text."""
    for ono in ONOMATOPOEIA:
        # Remove if standalone on a line
        pattern1 = r'^' + re.escape(ono) + r'[!.?]*\s*$'
        text = re.sub(pattern1, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove if followed by space
        pattern2 = r'\b' + re.escape(ono) + r'[!.?]*\s+'
        text = re.sub(pattern2, '', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'^\s+', '', text)
    text = re.sub(r'\s+$', '', text)
    return text.strip()


def clean_text_for_tts(text: str) -> str:
    """Cleans text for TTS processing while preserving pronunciation."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace periods with pauses (commas) to avoid "ponto"
    text = text.replace('.', ',')
    
    # Normalize ellipsis
    text = re.sub(r',,,+', ',', text)
    
    # Remove quotes
    text = re.sub(r'[""„‟«»\"\']', '', text)
    
    # Normalize multiple punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[,]{2,}', ',', text)
    
    # Convert semicolons and colons to commas
    text = re.sub(r'[;:]', ',', text)
    
    # Replace dashes with spaces
    text = re.sub(r'[-–—]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up comma spacing
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r',+', ',', text)
    
    return text.strip()


def is_speakable(text: str) -> bool:
    """Checks if text contains speakable content."""
    return bool(re.search(r"[A-Za-zÀ-ÿ0-9]", text))
