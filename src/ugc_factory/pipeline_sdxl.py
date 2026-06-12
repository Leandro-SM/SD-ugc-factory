"""SDXL Lightning pipeline (CPU). Higher quality, much slower (~15–25 min)."""
import time
from pathlib import Path
import torch
from rich.console import Console

from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler
from ugc_factory.models import MODELS_SDXL
from ugc_factory.postprocess.grain import add_film_grain

console = Console()


class SDXLPipeline:
    def __init__(self, model_key: str, cache_dir: str = "./models"):
        if model_key not in MODELS_SDXL:
            raise ValueError(
                f"Modelo SDXL desconhecido: {model_key}. "
                f"Modelos disponiveis: {list(MODELS_SDXL.keys())}"
            )
        repo = MODELS_SDXL[model_key]["repo"]
        self.model_key = model_key
        console.print(f"[cyan]📥 Carregando SDXL: {model_key} ({repo})[/cyan]")
        console.print("[yellow]⚠️  Primeiro Download ~7GB. Geracao de imagens com CPU pode levar ~15–25 min.[/yellow]")

        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            repo, torch_dtype=torch.float32, cache_dir=cache_dir,
            use_safetensors=True,
        )
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(
            self.pipe.scheduler.config, timestep_spacing="trailing"
        )
        self.pipe.to("cpu")
        self.pipe.enable_attention_slicing()
        try:
            self.pipe.enable_vae_slicing()
        except Exception:
            pass
        try:
            self.pipe.enable_vae_tiling()
        except Exception:
            pass
        console.print("[green]✓ SDXL pronto[/green]\n")

    def run(
        self, prompt: str, negative: str,
        width: int, height: int, steps: int, guidance: float,
        seed: int | None = None,
        out_path: str = "outputs/output.png",
        polish: str = "none",
        grain: str = "medium",
    ) -> Path:
        width  = (width  // 8) * 8
        height = (height // 8) * 8
        if seed is None:
            seed = int(time.time()) % 2**31
        gen = torch.Generator(device="cpu").manual_seed(seed)

        console.print(f"[cyan]🎨 SDXL Lightning | seed={seed}[/cyan]")
        console.print("[yellow]⏳ ETA: ~15–25 minutos com CPU..[/yellow]")
        t0 = time.time()
        img = self.pipe(
            prompt=prompt, negative_prompt=negative,
            width=width, height=height,
            num_inference_steps=steps, guidance_scale=guidance,
            generator=gen,
        ).images[0]
        console.print(f"[green]  ✓ {time.time()-t0:.1f}s[/green]")

        if grain != "off":
            console.print(f"[cyan]🎞️  Grunalação (film grain): {grain}[/cyan]")
            img = add_film_grain(img, grain)

        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out = out.with_name(f"{out.stem}_{seed}{out.suffix}")
        img.save(out, quality=95)

        elapsed = time.time() - t0
        out.with_suffix(".txt").write_text(
            f"engine: sdxl\nmodel: {self.model_key}\n"
            f"prompt: {prompt}\nnegative: {negative}\n"
            f"size: {img.size[0]}x{img.size[1]}\nsteps: {steps}\n"
            f"grain: {grain}\nseed: {seed}\n"
            f"elapsed_s: {elapsed:.1f}\n",
            encoding="utf-8",
        )
        console.print(f"\n[bold green]💾 {out.absolute()}[/bold green]")
        console.print(f"[bold]⏱ Tempo Total: {elapsed:.1f}s[/bold]\n")
        return out
