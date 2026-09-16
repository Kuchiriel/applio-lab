# TTS Comparison: Kokoro vs Emotional TTS (2026)

## Current State: Kokoro ONNX

**Prós:**
- ✅ Funciona perfeitamente (integrado com JARVIS daemon)
- ✅ Rápido: ONNX runtime, real-time synthesis
- ✅ Qualidade boa: Natural, clara
- ✅ Baixo recurso: CPU-only, <200MB RAM
- ✅ Multi-língua: PT-BR, EN funcionais
- ✅ Confiável: Usado em produção (voice commands, alerts)

**Contras:**
- ❌ **Sem emoções**: Voz neutra/monotônica
- ❌ Sem prosódia controlável: Pitch, rate, volume fixos
- ❌ Sem tags expressivas: [laugh], [sigh], [whisper] não funcionam
- ❌ Não ideal para audiobooks: Narrativa emotiva é crítica

**Uso atual:**
- Voice assistant responses (JARVIS daemon)
- System alerts and notifications
- Voice commands feedback
- **Não usado para audiobooks ainda** (enhanced_audiobook.py preparado mas não testado)

---

## Emotional TTS Options (Research 2025-2026)

### 🥇 **Chatterbox (Resemble AI)** - RECOMENDADO

**Especificações:**
- MIT License (open-source comercial)
- 350M parameters (lightweight comparado a alternativas)
- Faster than real-time inference
- Alignment-informed generation
- Python 3.11 required (⚠️ incompatível com Python 3.14)

**Recursos:**
- ✅ Emotion exaggeration control
- ✅ Paralinguistic tags: [cough], [laugh], [chuckle], [sigh]
- ✅ Zero-shot voice cloning (3-10s sample)
- ✅ Fine-grained emotion control
- ✅ Real-time capable

**Instalação:**
```bash
# Requer Python 3.11 (pyenv ou venv)
git clone https://github.com/resemble-ai/chatterbox.git
pip install -e .
```

**Integração:**
```python
from chatterbox import ChatterboxTTS

tts = ChatterboxTTS()
# Emotion via text markers
audio = tts.synthesize("He laughed nervously [laugh] as the door creaked open.")
```

**Avaliação:**
- 🟢 Melhor trade-off: performance vs expressividade
- 🟢 Tags inline (integra fácil com detect_emotion())
- 🟢 MIT license (comercial OK)
- 🔴 Python 3.11 required (precisa ambiente isolado)

**Score: 9/10** (perde 1 ponto por incompatibilidade Python 3.14)

---

### 🥈 **Fish Speech V1.5** - ALTERNATIVA

**Especificações:**
- Apache 2.0 License
- 1M+ hours training data
- Multi-lingual (EN, PT, ZH, etc)
- Python 3.8+

**Recursos:**
- ✅ Fine-grained emotion control
- ✅ Tone and delivery control
- ✅ Zero-shot voice cloning
- ⚠️ Emoções via parâmetros API (não inline tags)

**Instalação:**
```bash
git clone https://github.com/fishaudio/fish-speech.git
pip install -e .  # 47 dependencies
```

**Integração:**
```python
# Emotion via parameters
audio = fish_speech.synthesize(
    text="He laughed nervously as the door creaked open.",
    emotion="nervous",
    intensity=0.7
)
```

**Avaliação:**
- 🟢 Training data massivo (1M+ hours)
- 🟢 Python 3.8+ (compatível com 3.14?)
- 🔴 47 dependencies pesadas (torch, transformers, etc)
- 🔴 Emoções via params (precisa detect_emotion() separado)

**Score: 7/10** (bom mas dependencies pesadas)

---

### 🥉 **Bark (Suno AI)** - MAIS EXPRESSIVO

**Especificações:**
- MIT License (recente em 2025)
- Generative audio model
- GPU recommended (4GB+ VRAM)
- Python 3.8+

**Recursos:**
- ✅ **Mais expressivo de todos**: breathing, laughter, sighs naturais
- ✅ Inline tags: [laughs], [sighs], [gasps]
- ✅ Non-verbal sounds nativos
- ✅ Music generation (bonus)
- ⚠️ Slower than real-time (precisa GPU)
- ⚠️ 10GB+ model size

**Instalação:**
```bash
pip install bark
# Download models (~10GB)
```

**Integração:**
```python
from bark import generate_audio

# Tags inline (como Chatterbox)
audio = generate_audio("He [laughs] nervously as the door creaked open.")
```

**Avaliação:**
- 🟢 **Máxima expressividade** (melhor para audiobooks imersivos)
- 🟢 Inline tags (fácil integração)
- 🔴 Lento sem GPU (não real-time)
- 🔴 10GB model (storage)
- 🔴 Alto consumo VRAM (4-10GB)

**Score: 8/10** (excelente mas requer GPU)

---

### ❌ **EmotiVoice (Netease Youdao)** - NÃO RECOMENDADO

**Por que não:**
- Python 3.8 required (docs desatualizados)
- Conda-only installation (complexo)
- Modelo HuggingFace grande (~2GB)
- API menos intuitiva que alternativas
- Menos mantido que Chatterbox/Fish Speech

**Score: 5/10** (funciona mas alternativas superiores)

---

## Recommendation Matrix

| Use Case | Recomendação | Alternativa |
|----------|--------------|-------------|
| **Audiobooks imersivos** | 🥇 Chatterbox + 🥉 Bark | Fish Speech V1.5 |
| **Voice assistant** | Kokoro (atual) | Chatterbox Turbo |
| **System alerts** | Kokoro (atual) | - |
| **Baixo recurso (CPU)** | Kokoro | Chatterbox |
| **Máxima expressividade** | 🥉 Bark | Chatterbox |

---

## Migration Plan: Kokoro → Emotional TTS

### Fase 1: Preparação (1-2h)
1. ✅ Sistema de áudio imersivo implementado (SFX + ambient)
2. ✅ `detect_emotion()` preparado em enhanced_audiobook.py
3. ⏳ Resolver Python 3.14 incompatibilidade:
   - **Opção A**: pyenv install 3.11 (ambiente isolado)
   - **Opção B**: Docker container com Python 3.11
   - **Opção C**: Downgrade ChromaDB (teste rápido)

### Fase 2: Instalação TTS Emocional (30min-1h)
```bash
# Se usar pyenv (recomendado)
pyenv install 3.11.10
~/.pyenv/versions/3.11.10/bin/python3 -m venv ~/.jarvis/audiobook-tts-env
source ~/.jarvis/audiobook-tts-env/bin/activate

# Instalar Chatterbox
git clone https://github.com/resemble-ai/chatterbox.git /tmp/chatterbox
cd /tmp/chatterbox
pip install -e .

# OU instalar Bark (se tiver GPU)
pip install bark transformers torch
```

### Fase 3: Integração em enhanced_audiobook.py (30min)
```python
# Adicionar classe TTS switcher
class TTSEngine:
    def __init__(self, engine="chatterbox"):
        if engine == "chatterbox":
            from chatterbox import ChatterboxTTS
            self.tts = ChatterboxTTS()
            self.supports_inline_tags = True
        elif engine == "bark":
            from bark import generate_audio
            self.tts = generate_audio
            self.supports_inline_tags = True
        elif engine == "kokoro":
            # Fallback para Kokoro (daemon atual)
            self.tts = None  # Usa jarvis-speak
            self.supports_inline_tags = False

    async def synthesize(self, text: str, emotion: str = "neutral"):
        if self.supports_inline_tags:
            # Chatterbox/Bark: usar tags inline
            tagged_text = self._add_emotion_tags(text, emotion)
            audio = self.tts.synthesize(tagged_text)
        else:
            # Kokoro fallback (via daemon)
            await self._speak_daemon(text)

    def _add_emotion_tags(self, text: str, emotion: str) -> str:
        """Adiciona tags emocionais inline"""
        if emotion == "laugh":
            return f"[laugh] {text}"
        elif emotion == "whisper":
            return f"[whisper] {text} [/whisper]"
        elif emotion == "excited":
            return f"{text}!"  # Chatterbox detecta automaticamente
        return text
```

### Fase 4: Teste com LOTM (10min)
```bash
# Teste com enhanced_audiobook.py + Chatterbox
python3 enhanced_audiobook.py 2af2c60c5b25 --percentage 10 --engine chatterbox

# Comparação A/B:
# - Kokoro: Neutro, rápido
# - Chatterbox: Emotivo, inline tags
# - Bark: Máxima expressividade (se GPU)
```

---

## Final Verdict: Keep Kokoro?

### ✅ **SIM, manter Kokoro para:**

1. **Voice assistant (JARVIS daemon)**:
   - Respostas rápidas ("OK", "Pronto", "Comando executado")
   - Latência crítica (<100ms)
   - Kokoro: ~50ms, Chatterbox: ~200ms, Bark: ~2-5s

2. **System alerts**:
   - Notificações ("Bateria baixa", "Alarme ativado")
   - Confiabilidade > expressividade
   - Kokoro: testado, estável

3. **Fallback**:
   - Se Chatterbox/Bark falhar (GPU offline, OOM)
   - Kokoro sempre funciona (CPU-only)

### ❌ **NÃO usar Kokoro para:**

1. **Audiobooks**:
   - Narrativa emotiva é crítica
   - Chatterbox/Bark 10x melhor experiência
   - Usuário prefere qualidade > velocidade

2. **Long-form narration**:
   - Prosódia monotônica cansa após 5-10min
   - Emotional TTS mantém engajamento

---

## Implementation Priority

**HIGH (fazer agora):**
1. ✅ Sistema de áudio imersivo (DONE)
2. ⏳ Fix Python 3.14 incompatibilidade (pyenv 3.11 ou downgrade ChromaDB)
3. ⏳ Instalar Chatterbox em ambiente isolado
4. ⏳ Integrar Chatterbox em enhanced_audiobook.py

**MEDIUM (próximas sessões):**
1. Teste A/B: Kokoro vs Chatterbox (avaliar qualidade)
2. Voice cloning: Criar vozes custom para personagens
3. Bark integration (se GPU disponível)

**LOW (opcional):**
1. Download sons reais (substituir sox synthesis)
2. Fine-tuning Chatterbox para PT-BR (se necessário)
3. Docker container para deployment

---

## Conclusion

**Kokoro:** Excelente para voice assistant, manter para comandos rápidos

**Chatterbox:** RECOMENDADO para audiobooks (MIT, real-time, inline tags)

**Bark:** Melhor expressividade (se GPU disponível)

**Next Step:** Resolver Python 3.14 → pyenv 3.11 isolado → instalar Chatterbox

---

**Sources:**
- [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- [Bark TTS Documentation](https://github.com/suno-ai/bark)
- [Fish Speech V1.5](https://github.com/fishaudio/fish-speech)
- [Best Open-Source TTS 2026](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
