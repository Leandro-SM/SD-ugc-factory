<div align="center">

# 🎨 UGC Factory

### Geração de personagens fotorrealistas em CPU

*Como presets cuidadosamente elaborados permitem que **Stable Diffusion 1.5/SDXL** compitam com modelos muito maiores para geração de imagens/conteúdo UGC, sem utilização de GPU.*

![Python](https://img.shields.io/badge/Python-3.10%E2%80%933.13-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange?logo=pytorch&logoColor=white)
![Diffusers](https://img.shields.io/badge/🤗_Diffusers-0.32+-yellow)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-v1.0.0--rc1-orange)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey)


</div>

---

## ✨ Funcionalidades

- 🖥️ **100% local** - sem APIs, sem cloud, sem telemetria
- 🚀 **CPU-first** - otimizado para notebooks sem GPU dedicada
- 🎭 **10 presets de composição** (styles) que escondem falhas do modelo, como deformidades nas mãos
- ✋ **12 presets de pose** que escondem mãos/dedos
- 💡 **12 presets de iluminação** realistas
- 👤 **5 personas pré-definidas**
- 🎞️ **Film grain embutido** - remove instantaneamente a aparência de foto artificial, com uma camada de granulação
- ⚡ **Duas engines:** SD 1.5 + LCM-LoRA (~2 min) ou SDXL Lightning (~15–25 min)

---

## 📸 Exemplos

| Style | Descrição | Exemplo |
|---|---|---|
| `selfie` | Mall fitting room mirror selfie | `docs/examples/selfie.png` |
| `back-turned` | Hides face completely | `docs/examples/back_turned.png` |
| `crop-torso` | Focus on outfit | `docs/examples/crop_torso.png` |
| `pov` | First-person product showcase | `docs/examples/pov.png` |

```bash
ugc generate --style selfie --light mall --persona hanna
ugc generate --style back-turned --light golden --persona ana
ugc generate --style crop-legs --pose holding-bag --persona sofia
```

---

## 🚀 Como usar

### Pré-Requisitos

- **OS**: Linux, macOS, ou WSL2 (Windows)
- **Python**: 3.10, 3.11, 3.12, or 3.13 (3.14 não é suportado pelo PyTorch)
- **RAM**: 12GB min, **16GB recomendado**
- **Disk**: ~15GB livres (cached models)
- **GPU**: ❌

### Instação

```bash
# 1. Clone
git clone https://github.com/leandro-sm/SD-ugc-factory.git
cd SD-ugc-factory

# 2. One-command setup (detects Python, creates venv, installs deps)
chmod +x setup.sh run.sh
./setup.sh

# 3. Activate and generate
source .venv/bin/activate
ugc generate
```

> ⏱️ **Primeira Execução**: Faz Download dos modelos ~3GB (Apenas na primeira execução).
> **Pŕoximas execuções**: ~2 min (SD 1.5) e ~15–25 min (SDXL).

---

## 🎯 Utilização

### Listar Presets

```bash
ugc presets       # listar styles + poses + lighting + outfits
ugc personas      # listar personas pré-definidas
ugc models        # listar modelos/engines
```

### Gerar Imagem

```bash
# Padrão: persona básica, style selfie, lighting mall
ugc generate

# Customizado
ugc generate --persona mike --style ootd --pose phone-face --light bedroom --outfit trendy

# Esconder rosto completamente
ugc generate --style back-turned --light golden --outfit dress

# Foco no produto
ugc generate --style crop-legs --pose holding-bag --light mall
```

### Gerar variações

```bash
# 4 imagens com diferentes seeds
ugc batch --count 4 --style selfie --light mall --persona ana
```

### Máxima qualidade com CPU (SDXL, slower)

```bash
ugc generate --engine sdxl --style selfie
# ⏱️ ~15–25 min - ~30-45 min
```

### Usar Prompt customizado

```bash
ugc generate --prompt "prompt customizado" --seed 42
```

---

## 🧠 Como funciona

```
                   ┌─────────────────────────────────────┐
                   │     Parametros executados no CLI    │
                   │  --persona / --style / --pose       │
                   │  --light / --outfit                 │
                   └──────────────┬──────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────────────┐
                   │     Prompt Builder (/presets/)       │
                   │   Combina personagem + composição    │
                   │     + pose + iluminação               │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────────────────────┐
                   │   Stable Diffusion Pipeline (SD 1.5 / SDXL) │
                   │          + LCM-LoRA acceleration            │
                   └──────────────┬──────────────────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────────────────┐
                   │  Pós-Processamento (film grain, vignette)  │
                   │  Elimina aparencia plastificada com Grain  │
                   └──────────────┬─────────────────────────────┘
                                  │
                                  ▼
                       📸 Imagem Gerada (Output - 640×960)
```

### POSE presets que escondem as mãos do personagem

`phone-face` · `hands-pocket` · `hands-back` · `hands-hair` · `hands-hip` · `arms-crossed` · `holding-coffee` · `holding-bag` · `walking` · `sitting` · `leaning-wall` · `back-camera`

---

## ⚙️ Configuração

| Flag | Default | Descrição |
|---|---|---|
| `--engine` | `sd15` | `sd15` | Engine
| `--persona` | `hanna` | Personagens pré-definidos |
| `--style` | `selfie` | Presets de composição da imagen que escondem falhas dos modelos |
| `--pose` | _none_ | Presets de pose) |
| `--light` | `mall` | Iluminação da imagem |
| `--outfit` | `tshirt-shorts` | Outfit (preset or free text) |
| `--scene` | _none_ | Descrição adicional para a imagem |
| `--polish` | `none` | `none` (RAW) \| `face` \| `full` |
| `--grain` | `medium` | `off`/`low`/`medium`/`high` (granulação fotográfica) |
| `--seed` | random | Consistência
| `--prompt` | _none_ | Full custom prompt (overrides presets) |

---

## ⏱️ Performance (16GB - 32GB RAM)

| Engine | Tempo de execução |
|---|---|
| `sd15` + RAW (default) ⭐ | **~2 min** |
| `sd15` + `--polish face` | ~3 min |
| `sd15` + `--polish full` | ~5 min |
| `sdxl` Lightning | **~15–25 min** |

---

## 🗺️ Roadmap

- [x] SD 1.5 + SDXL (Engine)
- [x] 10 variações de Estilo, Poses, Iluminação (Styles.py/Poses.py/Lighting.py/)
- [x] 5 Personas (Characters.py)
- [x] Film Grain para granulação da imagem (pós-processamento)

---


## 📚 Recursos

- [🤗 Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [LCM-LoRA Paper](https://arxiv.org/abs/2311.05556)
- [SDXL Lightning](https://huggingface.co/ByteDance/SDXL-Lightning)
- [epiCRealism on Civitai](https://civitai.com/models/25694)

---

