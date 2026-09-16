# Enhanced Audiobook System - Documentação

## Resumo

Sistema aprimorado de audiobook com navegação avançada, detecção de efeitos sonoros e suporte futuro para TTS emocional, baseado em pesquisa de melhores práticas 2025/2026.

## 🎯 Recursos Implementados

### 1. Navegação Avançada

#### Por Capítulo
```bash
# CLI
python3 jarvis/enhanced_audiobook.py <book_id> --chapter 5

# Voz
"vai para o capítulo 5"
"chapter 3"
```

#### Por Porcentagem
```bash
# CLI
python3 jarvis/enhanced_audiobook.py <book_id> --percentage 50

# Voz
"vai para 50 por cento"
"pula para 75 porcento"
"vai para o meio"  # atalho para 50%
"vai para o final"  # atalho para 90%
```

#### Navegação Relativa
```bash
# Voz
"pula 3 capítulos"  # avança 3 capítulos
"volta 2 capítulos"  # retrocede 2 capítulos
```

### 2. Detecção de Efeitos Sonoros

O sistema detecta keywords no texto e notifica quando deve tocar efeitos:

**Clima:**
- rain, raining, chuva, chuvendo
- thunder, trovão, relâmpago
- wind, vento, windy
- storm, tempestade

**Natureza:**
- birds, pássaros, chirping
- waves, ondas, ocean, mar
- fire, fogo, crackling
- forest, floresta, woods

**Ações:**
- door, porta, knock, batida
- footsteps, passos, walking
- explosion, explosão, blast
- scream, grito

**Emoções (para prosody futuro):**
- whisper, sussurro → voz baixa/devagar
- shout, grito → voz alta/rápida
- laugh, riso
- cry, chorar

**Exemplo de uso:**
```python
text = "The rain was falling hard as thunder echoed in the distance"
# Detecta: ['rain', 'thunder']
# Sistema notifica: 🔊 [RAIN] 🔊 [THUNDER]
```

### 3. Comandos de Voz Completos

#### Controle Básico
```
"leia o livro <nome>"      # Iniciar leitura
"para" / "pausa"           # Pausar
"continua" / "resume"      # Retomar
"proximo" / "next"         # Próximo chunk
"anterior" / "previous"    # Chunk anterior
"volta pro inicio"         # Recomeçar do início
```

#### Navegação
```
"vai para o capitulo 5"
"chapter 10"
"vai para 50 por cento"
"pula para 75 porcento"
"vai para o meio"
"vai para o final"
"pula 3 capitulos"
"volta 2 capitulos"
```

#### Velocidade
```
"mais rapido"          # 1.3x
"mais devagar"         # 0.8x
"velocidade normal"    # 1.0x
```

#### Informações
```
"onde estou"           # Mostra posição atual
"status"               # Informações do livro
"quais livros tenho"   # Lista livros indexados
```

## 🔬 Pesquisa e Referências

### Voice Control Patterns (2025)

Baseado em análise de plataformas comerciais:

- **Kobo**: Timeline scrubber, chapter navigation, playback speed
- **Audible**: Chapter list, 15/30s rewind buttons
- **Voice Assistants**: "Skip to next chapter", "Replay last 30 seconds"

**Sources:**
- [Kobo Audiobook Controls](https://help.kobo.com/hc/en-us/articles/360018108553-Audiobook-controls-on-Android)
- [Audible Chapter Navigation](https://help.audible.com/s/article/browse-chapters-and-episodes?language=en_US)
- [Voice Commands for Audiobooks](https://www.meegle.com/en_us/topics/voice-commands/voice-command-for-audiobooks)

### Emotional TTS Models (2025-2026)

**Open-source models pesquisados:**

1. **Chatterbox** - Emotion exaggeration control, paralinguistic tags ([laugh], [cough])
2. **FishAudio-S1-mini** - Fine-grained emotion, tone, delivery control
3. **EmotiVoice** - Multi-emotional synthesis (happy, excited, sad, angry)
4. **Bark** - Expressive speech with breathing, laughter, natural nuances
5. **Marvis TTS (2025)** - Tuned for emotional and varied speech
6. **Mozilla TTS** - Multi-speaker, emotional synthesis, SSML support

**SSML/Prosody Support:**
- **OpenTTS** - SSML subset with multiple voices
- **OpenMary (MaryTTS)** - Full SSML/APML support, high prosody control
- **IndexTTS** - Controllable duration, pitch, prosody

**Sources:**
- [Best Open-Source TTS Models 2026](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
- [EmotiVoice GitHub](https://github.com/netease-youdao/EmotiVoice)
- [Google Cloud SSML](https://cloud.google.com/text-to-speech/docs/ssml)

### Immersive Audiobooks (2025)

**Tendências de mercado:**

- **Multi-track editing**: Voice + sound design + ambient + music
- **Spatial audio mixing**: 3D soundscape
- **Background ambiance**: Environmental sounds matching book setting
- **Sound effects library**: Weather, nature, actions synchronized with narrative

**Dados de engajamento:**
- Audiobooks imersivos têm **maior taxa de conclusão** que tradicionais
- Produtores independentes agora têm acesso a ferramentas profissionais
- Mercado em crescimento para diferenciação via áudio imersivo

**Sources:**
- [The Rise of Immersive Audio](https://publishdrive.com/the-rise-of-immersive-audio-is-your-audiobook-an-audio-movie.html)
- [Immersive Audiobooks Guide](https://soundsandsuch.com/howtoaudiobook/creating-immersive-audiobooks-a-beginners-guide-to-spatial-audio-and-sound-effects)
- [Best Immersive Audiobooks 2025](https://ahomeisannounced.com/2025/05/30/best-immersive-audiobooks/)

## 🚀 Próximos Passos (Roadmap)

### 1. Biblioteca de Sons (Prioridade: Alta)

**Implementação:**
```bash
mkdir -p ~/.jarvis/sounds/{weather,nature,actions,ambient}

# Download free sound effects:
# Freesound.org (CC licenses)
# OpenGameArt.org
# BBC Sound Effects Library
```

**Estrutura sugerida:**
```
~/.jarvis/sounds/
├── weather/
│   ├── rain_light.ogg
│   ├── rain_heavy.ogg
│   ├── thunder.ogg
│   └── wind.ogg
├── nature/
│   ├── birds_morning.ogg
│   ├── ocean_waves.ogg
│   └── forest_ambiance.ogg
├── actions/
│   ├── door_knock.ogg
│   ├── footsteps.ogg
│   └── explosion.ogg
└── ambient/
    ├── fireplace.ogg
    └── rain_background.ogg
```

**TODO no código:**
```python
# Em enhanced_audiobook.py, linha ~200
async def play_sound_effect(effect_name: str):
    sound_dir = Path.home() / ".jarvis" / "sounds"

    # Tentar diferentes variações
    for category in ["weather", "nature", "actions"]:
        sound_file = sound_dir / category / f"{effect_name}.ogg"
        if sound_file.exists():
            await asyncio.create_subprocess_exec(
                "paplay", str(sound_file)
            )
            return

    print(f"⚠️ Sound effect not found: {effect_name}")
```

### 2. TTS Emocional (Prioridade: Média)

**Opção 1: EmotiVoice (Recomendado)**
```bash
pip install onnxruntime
git clone https://github.com/netease-youdao/EmotiVoice
# Integrar com enhanced_audiobook.py
```

**Opção 2: Bark (Mais expressivo)**
```bash
pip install transformers bark
# Requer GPU, ~10GB VRAM
```

**Implementação futura:**
```python
def add_prosody_markers(text: str) -> str:
    emotion, rate = detect_emotion(text)

    if emotion == "excited":
        # EmotiVoice: {"emotion": "excited", "speed": rate}
        pass
    elif emotion == "whisper":
        # Bark: Use [whispered] tag
        return f"[whispered]{text}[/whispered]"

    return text
```

### 3. Áudio Ambiente Contínuo (Prioridade: Baixa)

**Conceito:**
```python
# Detectar cenário do livro via contexto
scene_type = detect_scene(text)  # "forest", "storm", "ocean"

# Tocar áudio ambiente em loop baixo volume
if scene_type == "forest":
    play_ambient("forest_ambiance.ogg", volume=0.3, loop=True)

# Parar quando cena muda
if new_scene != scene_type:
    stop_ambient()
```

## 📁 Arquivos do Sistema

```
AI_SYSTEM/
├── jarvis/
│   ├── enhanced_audiobook.py          # ✅ Leitor aprimorado
│   └── jarvis-read.py                 # Leitor básico (mantido para compatibilidade)
├── orchestrator/
│   ├── brain/core/audiobook.rive      # ✅ Comandos de voz atualizados
│   └── rivescript_router.py           # ✅ Macros chapter/percentage/skip
├── core/
│   ├── book_indexer.py                # Indexação ChromaDB
│   └── book_extractor.py              # Extração PDF/EPUB/TXT
└── docs/
    └── ENHANCED_AUDIOBOOK.md          # Este arquivo
```

## 🎮 Testes Rápidos

### Teste 1: Navegação por Capítulo
```bash
# Indexar livro de teste
python3 core/book_indexer.py index ~/Documents/test_book.pdf

# Iniciar no capítulo 3
python3 jarvis/enhanced_audiobook.py <book_id> --chapter 3

# Verificar que começou no capítulo correto
```

### Teste 2: Navegação por Porcentagem
```bash
# Pular para 50%
python3 jarvis/enhanced_audiobook.py <book_id> --percentage 50

# Verificar posição no estado
cat ~/.jarvis/reading_state.json
```

### Teste 3: Detecção de Efeitos Sonoros
```python
# Criar arquivo de teste com keywords
echo "The rain was falling as thunder echoed" > test.txt

# Verificar que detecta "rain" e "thunder"
python3 -c "
from jarvis.enhanced_audiobook import detect_sound_effects
text = 'The rain was falling as thunder echoed'
print(detect_sound_effects(text))
"
# Esperado: ['rain', 'thunder']
```

### Teste 4: Comandos de Voz
```bash
# Via JARVIS daemon (requer wakeword ativo)
# "Hey JARVIS"
# "leia o livro test"
# "vai para o meio"
# "para"
```

## 🔧 Troubleshooting

### Sons não tocam
```bash
# Verificar se paplay funciona
paplay /usr/share/sounds/freedesktop/stereo/bell.oga

# Verificar diretório de sons
ls ~/.jarvis/sounds/
```

### Capítulos não detectados
```bash
# Verificar metadados no ChromaDB
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='~/.jarvis/chroma_books')
# Inspecionar metadata['chapter']
"
```

### TTS não emocional (esperado)
```
Atualmente usando Kokoro TTS (neutro).
Para emoções, implementar EmotiVoice conforme roadmap.
```

## 📊 Comparação: Antes vs Depois

| Recurso | Antes | Depois |
|---------|-------|--------|
| Navegação | Apenas next/prev chunk | Capítulos, %, relativa |
| Comandos de voz | 8 comandos | 20+ comandos |
| Efeitos sonoros | Não | Detecção automática |
| TTS emocional | Não | Preparado (detect_emotion) |
| Áudio ambiente | Não | Framework pronto |
| Atalhos | Não | "meio", "final" |

## 📝 Comandos de Exemplo (Copy-Paste)

```bash
# Indexar livro
python3 core/book_indexer.py index ~/Documents/meu_livro.pdf

# Listar livros
python3 jarvis/enhanced_audiobook.py list

# Ler do início
python3 jarvis/enhanced_audiobook.py <book_id>

# Ler do capítulo 5
python3 jarvis/enhanced_audiobook.py <book_id> --chapter 5

# Ir para 75%
python3 jarvis/enhanced_audiobook.py <book_id> --percentage 75

# Sem efeitos sonoros
python3 jarvis/enhanced_audiobook.py <book_id> --no-sfx
```

## 🎯 Conclusão

Sistema pronto para uso em produção com:
- ✅ Navegação avançada (3 métodos)
- ✅ 20+ comandos de voz
- ✅ Detecção de SFX (framework)
- ✅ Preparado para TTS emocional
- ⏳ Aguarda biblioteca de sons (manual)
- ⏳ Aguarda integração EmotiVoice (opcional)

**Benefícios imediatos:**
- Melhor controle de leitura (pular capítulos, porcentagem)
- Acessibilidade aprimorada (comandos naturais PT/EN)
- Base sólida para audiobooks imersivos

**Baseado em research 2025/2026 de:**
- Plataformas comerciais (Audible, Kobo)
- Modelos TTS open-source
- Tendências de audiobook immersive
