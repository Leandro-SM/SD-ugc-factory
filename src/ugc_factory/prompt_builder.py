from ugc_factory.presets.styles import STYLES
from ugc_factory.presets.poses import POSES
from ugc_factory.presets.lighting import LIGHTS
from ugc_factory.presets.outfits import OUTFITS

#ESTILO PADRAO DAS IMAGENS
STYLE_BASE = (
    "amateur iPhone photo, real instagram story aesthetic, "
    "candid moment, natural authentic look, "
    "visible skin texture, slightly imperfect framing"
)
#GUARDRAILS
NEGATIVE_UGC = (
    # (Evita pele artificial estilo plástico)
    "plastic skin, smooth skin, airbrushed, doll-like, fake, render, cgi, 3d, "
    "illustration, painting, anime, cartoon, drawing, "
    # (Evita estilo editorial de estudio, ou imagem não realista)
    "professional photography, studio lighting, softbox, fashion editorial, "
    "beauty shot, magazine cover, posed model pose, glamour shot, retouched, "
    # (Evita erros de geometria e anatomia ʘ‿ʘ)
    "deformed face, asymmetric face, deformed hands, extra fingers, missing fingers, "
    "fused fingers, mutated, disfigured, bad anatomy, long neck, "
    # (Evita problemas de qualidade do modelo, como baixa resolução, marca d'água, textos bugados, etc.)
    "blurry, out of focus, low quality, low resolution, jpeg artifacts, "
    "watermark, text, logo on shirt, brand on shirt, username, signature, "
    # GUARDRAIL Idade
    "child, teen, young, underage"
)


def build_prompt(
    character: str,
    style: str = "selfie",
    pose: str | None = None,
    light: str = "mall",
    outfit: str = "tshirt-shorts",
    scene: str | None = None,
) -> str:
    """Combina o character + composicao + pose + iluminacao + outfit em um unico prompt"""
    parts = [character]

    outfit_txt = OUTFITS.get(outfit, outfit)
    parts.append(outfit_txt)

    if pose and pose in POSES:
        parts.append(POSES[pose])

    if style in STYLES:
        parts.append(STYLES[style]["composition"])

    if light in LIGHTS:
        parts.append(LIGHTS[light])

    if scene:
        parts.append(scene)

    parts.append(STYLE_BASE)
    return ", ".join(parts)
