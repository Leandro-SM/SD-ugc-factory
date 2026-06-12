#!/usr/bin/env bash
set -e

# ─── UGC Factory Setup ─────────────────────────────────────
# Auto-detects best Python version (3.10-3.13)
# Creates venv, installs CPU PyTorch + dependencies
# ───────────────────────────────────────────────────────────

echo ""
echo "  ╔════════════════════════════════════════════════╗"
echo "            UGC Factory - Criando Setup             "
echo "  ║   Photorealistic AI character on CPU (+RAM)    ║"
echo "                        WSL2                        "
echo "  ╚════════════════════════════════════════════════╝"
echo ""

# 1) Detect compatible Python (3.10-3.13)
PYTHON=""
for v in 3.12 3.11 3.10 3.13; do
    if command -v python$v &> /dev/null; then
        PYTHON="python$v"
        echo "✓ Found Python $v"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.10-3.13 nao encontrado."
    echo "   Instalar Python 3.12: sudo apt install python3.12 python3.12-venv python3.12-dev"
    exit 1
fi

# 2) venv
if [ ! -d ".venv" ]; then
    echo "📦 Criando virtual environment..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip wheel setuptools --quiet

# 3) PyTorch CPU 
echo "📥 Instalando PyTorch CPU build..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet

# 4) Project e dependencias
echo "📥 Instalando UGC Factory..."
pip install -e . --quiet

# 5) Output dirs
mkdir -p outputs models

# 6) Permissions
chmod +x run.sh 2>/dev/null || true

echo ""
echo "✅ Setup completo!"
echo ""
echo "▶️  Primeiros Passos:"
echo "    source .venv/bin/activate"
echo "    ugc generate                          # Configuração padrao"
echo "    ugc generate --style selfie --light mall # Gerar imagem padrao"
echo "    ugc presets                           # Listar presets personalizados (parametros)"
echo "    ugc personas                          # Listar  personas padrao "
echo ""
echo "** Customização do Personagem:"
echo "    - listar personas: ugc personas"
echo "    - usar uma persona: ugc generate --persona ana"
echo "    - criar uma persona: src/ugc_factory/presets/characters.py"
echo "      -> adicione description, face/body, details" 
echo ""
echo "⏱️  A primeira exeucao instala os modelos ~3GB (uma unica vez)."
echo "    proximas execucoes: ~2 min com CPU (16~32GB RAM)."
echo ""
