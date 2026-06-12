from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ugc_factory import __version__
from ugc_factory.models import (
    MODELS_SD15, MODELS_SDXL, DEFAULT_SD15, DEFAULT_SDXL,
)
from ugc_factory.presets.characters import PERSONAS, DEFAULT_PERSONA, build_character
from ugc_factory.presets.styles import STYLES
from ugc_factory.presets.poses import POSES
from ugc_factory.presets.lighting import LIGHTS
from ugc_factory.presets.outfits import OUTFITS
from ugc_factory.prompt_builder import build_prompt, NEGATIVE_UGC

console = Console()


# ─────────────────────────────────────────────────────────────────
# argparse setup
# ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ugc",
        description="UGC Factory — photorealistic character generation on CPU",
        epilog="Examples:\n"
               "  ugc generate --style selfie --persona nova\n"
               "  ugc batch --count 4 --style ootd --persona ana\n"
               "  ugc presets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True, metavar="<command>")

    # ---- generate ----
    g = sub.add_parser("generate", help="Generate one image")
    _add_generation_args(g)
    g.set_defaults(func=cmd_generate)

    # ---- batch ----
    b = sub.add_parser("batch", help="Generate N variations (cherry-pick)")
    _add_generation_args(b)
    b.add_argument("--count", type=int, default=4)
    b.add_argument("--prefix", default="variation")
    b.set_defaults(func=cmd_batch)

    # ---- presets ----
    pr = sub.add_parser("presets", help="List all preset categories")
    pr.set_defaults(func=cmd_presets)

    # ---- personas ----
    per = sub.add_parser("personas", help="List pre-defined characters")
    per.set_defaults(func=cmd_personas)

    # ---- models ----
    m = sub.add_parser("models", help="List available checkpoints")
    m.set_defaults(func=cmd_models)

    return p


def _add_generation_args(p):
    p.add_argument("--engine", choices=["sd15", "sdxl"], default="sd15",
                   help="sd15 (fast, ~2min) or sdxl (quality, ~25min)")
    p.add_argument("--model", default=None,
                   help="Override checkpoint key (see `ugc models`)")
    p.add_argument("--persona", default=DEFAULT_PERSONA,
                   help=f"Pre-defined character ({', '.join(PERSONAS.keys())})")
    p.add_argument("--style", default="selfie", choices=list(STYLES.keys()),
                   help="Composition preset (hides model weaknesses)")
    p.add_argument("--pose", default=None, choices=list(POSES.keys()),
                   help="Pose preset (hides hands)")
    p.add_argument("--light", default="mall", choices=list(LIGHTS.keys()),
                   help="Lighting preset")
    p.add_argument("--outfit", default="tshirt-shorts",
                   help="Outfit (preset key or free text)")
    p.add_argument("--scene", default=None, help="Extra scene description")
    p.add_argument("--prompt", default=None,
                   help="Full custom prompt (overrides presets)")
    p.add_argument("--negative", default=NEGATIVE_UGC)
    p.add_argument("--seed", type=int, default=None,
                   help="Use same seed for consistency across generations")
    p.add_argument("--width",  type=int, default=None)
    p.add_argument("--height", type=int, default=None)
    p.add_argument("--steps",  type=int, default=None)
    p.add_argument("--guidance", type=float, default=None)
    p.add_argument("--out", default="outputs/output.png")
    p.add_argument("--polish", choices=["none", "face", "full"], default="none",
                   help="Post-process intensity (none = RAW, more realistic)")
    p.add_argument("--grain", choices=["off", "low", "medium", "high"], default="medium",
                   help="Film grain intensity (kills the AI look)")
    p.add_argument("--threads", type=int, default=0,
                   help="CPU threads (0 = auto)")


# ─────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────

def _resolve_defaults(args):
    """Set engine-specific defaults."""
    if args.engine == "sd15":
        args.model = args.model or DEFAULT_SD15
        args.width  = args.width  or 640
        args.height = args.height or 960
        args.steps  = args.steps  or 8
        args.guidance = args.guidance or 1.8
    else:
        args.model = args.model or DEFAULT_SDXL
        args.width  = args.width  or 768
        args.height = args.height or 1152
        args.steps  = args.steps  or 6
        args.guidance = args.guidance or 2.0


def _setup_threads(n: int):
    if n > 0:
        import torch
        torch.set_num_threads(n)


def _build_prompt_from_args(args) -> str:
    if args.prompt:
        return args.prompt
    character_str = build_character(args.persona)
    return build_prompt(
        character=character_str,
        style=args.style, pose=args.pose, light=args.light,
        outfit=args.outfit, scene=args.scene,
    )


def cmd_generate(args):
    _setup_threads(args.threads)
    _resolve_defaults(args)
    prompt = _build_prompt_from_args(args)

    console.rule(f"[bold magenta]ENGINE {args.engine.upper()} | "
                 f"MODEL {args.model} | PERSONA {args.persona}[/bold magenta]")
    console.print(f"[cyan]Prompt:[/cyan] {prompt[:200]}{'...' if len(prompt)>200 else ''}")
    console.print(f"[cyan]Size:[/cyan] {args.width}x{args.height}  "
                  f"[cyan]Steps:[/cyan] {args.steps}  "
                  f"[cyan]Guidance:[/cyan] {args.guidance}")
    console.print(f"[cyan]Polish:[/cyan] {args.polish}  [cyan]Grain:[/cyan] {args.grain}\n")

    if args.engine == "sd15":
        from ugc_factory.pipeline import SD15Pipeline as Pipe
    else:
        from ugc_factory.pipeline_sdxl import SDXLPipeline as Pipe

    pipe = Pipe(model_key=args.model)
    pipe.run(
        prompt=prompt, negative=args.negative,
        width=args.width, height=args.height,
        steps=args.steps, guidance=args.guidance,
        seed=args.seed, out_path=args.out,
        polish=args.polish, grain=args.grain,
    )


def cmd_batch(args):
    _setup_threads(args.threads)
    _resolve_defaults(args)
    prompt = _build_prompt_from_args(args)

    if args.engine == "sd15":
        from ugc_factory.pipeline import SD15Pipeline as Pipe
    else:
        from ugc_factory.pipeline_sdxl import SDXLPipeline as Pipe

    pipe = Pipe(model_key=args.model)
    base = args.seed or 1
    for i in range(args.count):
        seed = base + i
        out = Path("outputs") / f"{args.prefix}_{args.persona}_seed{seed}.png"
        console.rule(f"[bold magenta]Variation {i+1}/{args.count} (seed={seed})[/bold magenta]")
        pipe.run(
            prompt=prompt, negative=args.negative,
            width=args.width, height=args.height,
            steps=args.steps, guidance=args.guidance,
            seed=seed, out_path=str(out),
            polish=args.polish, grain=args.grain,
        )


def cmd_presets(args):
    # Styles
    t = Table(title="🎭 STYLES (composicao da imagem)", show_lines=True)
    t.add_column("Style", style="cyan", no_wrap=True)
    t.add_column("Hides")
    for k, v in STYLES.items():
        t.add_row(k, ", ".join(v["hide"]))
    console.print(t)

    # Poses
    t = Table(title="✋ POSES (Esconde maos)")
    t.add_column("Pose", style="cyan", no_wrap=True)
    t.add_column("Description")
    for k, v in POSES.items():
        t.add_row(k, v[:75])
    console.print(t)

    # Lights
    t = Table(title="💡 LIGHTS")
    t.add_column("Light", style="cyan", no_wrap=True)
    t.add_column("Description")
    for k, v in LIGHTS.items():
        t.add_row(k, v[:75])
    console.print(t)

    # Outfits
    t = Table(title="👕 OUTFITS")
    t.add_column("Outfit", style="cyan", no_wrap=True)
    t.add_column("Description")
    for k, v in OUTFITS.items():
        t.add_row(k, v)
    console.print(t)

    console.print("\n[bold green]Exemplos:[/bold green]")
    console.print("  ugc generate --persona hanna --style selfie --light mall")
    console.print("  ugc generate --persona ana --style back-turned --light golden")
    console.print("  ugc generate --persona sofia --style crop-legs --pose holding-bag")


def cmd_personas(args):
    t = Table(title="👤 PERSONAS", show_lines=True)
    t.add_column("Persona", style="cyan", no_wrap=True)
    t.add_column("Description")
    for k, v in PERSONAS.items():
        mark = " ⭐" if k == DEFAULT_PERSONA else ""
        t.add_row(k + mark, v[:120])
    console.print(t)
    console.print("\n[dim]💡 Cria sua persona em: src/ugc_factory/presets/characters.py[/dim]")


def cmd_models(args):
    t = Table(title="🤖 CHECKPOINTS", show_lines=True)
    t.add_column("Engine", style="green")
    t.add_column("Key", style="cyan")
    t.add_column("HuggingFace Repo")
    t.add_column("Note")
    for k, v in MODELS_SD15.items():
        mark = " ⭐" if k == DEFAULT_SD15 else ""
        t.add_row("sd15", k + mark, v["repo"], v["note"])
    for k, v in MODELS_SDXL.items():
        mark = " ⭐" if k == DEFAULT_SDXL else ""
        t.add_row("sdxl", k + mark, v["repo"], v["note"])
    console.print(t)


# ─────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹  Cancelled by user.[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        if "--debug" in (argv or sys.argv):
            raise
        console.print("[dim]Run with --debug for full traceback.[/dim]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
