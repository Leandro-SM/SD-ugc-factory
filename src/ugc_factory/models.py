#=== MODELOS ===

MODELS_SD15 = {
    "epicrealism": {
        "repo": "emilianJR/epiCRealism",
        "note": "⭐ Best for UGC realism, natural skin/lighting",
    },
    "realistic_vision": {
        "repo": "SG161222/Realistic_Vision_V5.1_noVAE",
        "note": "Balanced, safe default",
    },
    "dreamshaper": {
        "repo": "Lykon/dreamshaper-8",
        "note": "Editorial / fashion style",
    },
    "cyberrealistic": {
        "repo": "Yntec/CyberRealistic",
        "note": "Influencer / selfie aesthetic",
    },
}

MODELS_SDXL = {
    "juggernaut_xl_lightning": {
        "repo": "RunDiffusion/Juggernaut-XL-Lightning",
        "note": "⭐ SDXL accelerated (6–8 steps), best CPU choice",
    },
    "realvis_xl": {
        "repo": "SG161222/RealVisXL_V4.0",
        "note": "Pure photorealism (needs 25+ steps, slow on CPU)",
    },
}

DEFAULT_SD15 = "epicrealism"
DEFAULT_SDXL = "juggernaut_xl_lightning"

LCM_LORA_SD15 = "latent-consistency/lcm-lora-sdv1-5"
LCM_LORA_SDXL = "latent-consistency/lcm-lora-sdxl"
