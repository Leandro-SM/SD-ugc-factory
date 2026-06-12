# SD 1.5 diffusion pipeline
import time
from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFilter
from rich.console import Console

from diffusers import (
    StableDiffusionPipeline, StableDiffusionImg2ImgPipeline,
    LCMScheduler, DPMSolverMultistepScheduler,
)
from ugc_factory.models import MODELS_SD15, LCM_LORA_SD15
from ugc_factory.postprocess.face import detect_face_box
from ugc_factory.postprocess.grain import add_film_grain

console = Console()


class SD15Pipeline:
    def __init__(self, model_key: str, cache_dir: str = "./models"):
        if model_key not in MODELS_SD15:
            raise ValueError(
                f"Unknown SD 1.5 model: {model_key}. "
                f"Available: {list(MODELS_SD15.keys())}"
            )
        repo = MODELS_SD15[model_key]["repo"]
        self.cache_dir = cache_dir
        self.model_key = model_key

        console.print(f"[cyan]📥 Carregando SD 1.5: {model_key} ({repo})[/cyan]")
        self.txt2img = StableDiffusionPipeline.from_pretrained(
            repo, torch_dtype=torch.float32,
            safety_checker=None, requires_safety_checker=False,
            cache_dir=cache_dir,
        )
        self.txt2img.scheduler = LCMScheduler.from_config(self.txt2img.scheduler.config)
        console.print("[cyan]⚡ Aplicando LCM-LoRA (8× speedup)...[/cyan]")
        self.txt2img.load_lora_weights(LCM_LORA_SD15, cache_dir=cache_dir)
        self.txt2img.fuse_lora()
        self.txt2img.to("cpu")
        self.txt2img.enable_attention_slicing()
        try:
            self.txt2img.enable_vae_slicing()
        except Exception:
            pass
        self._refine = None
        console.print("[green]✓ Pipeline ready[/green]\n")

    def _build_refine(self):
        if self._refine is not None:
            return self._refine
        console.print("[cyan]🔧 Aplicando refine (img2img)...[/cyan]")
        repo = MODELS_SD15[self.model_key]["repo"]
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            repo, torch_dtype=torch.float32,
            safety_checker=None, requires_safety_checker=False,
            cache_dir=self.cache_dir,
        )
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.to("cpu")
        pipe.enable_attention_slicing()
        self._refine = pipe
        return pipe

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

        console.print(f"[cyan]🎨 txt2img + LCM | seed={seed}[/cyan]")
        t0 = time.time()
        img = self.txt2img(
            prompt=prompt, negative_prompt=negative,
            width=width, height=height,
            num_inference_steps=steps, guidance_scale=guidance,
            generator=gen,
        ).images[0]
        console.print(f"[green]  ✓ {time.time()-t0:.1f}s[/green]")

        if polish == "full":
            console.print("[cyan]🔧 Refine (strength 0.18)[/cyan]")
            t = time.time()
            refine = self._build_refine()
            img = refine(
                prompt=prompt, negative_prompt=negative,
                image=img, strength=0.18,
                num_inference_steps=12, guidance_scale=5.5,
                generator=torch.Generator(device="cpu").manual_seed(seed + 1),
            ).images[0]
            console.print(f"[green]  ✓ {time.time()-t:.1f}s[/green]")

        if polish in ("face", "full"):
            console.print("[cyan]🙂 Face detailer (strength 0.22)[/cyan]")
            t = time.time()
            img = self._face_detail(img, prompt, negative, seed)
            console.print(f"[green]  ✓ {time.time()-t:.1f}s[/green]")

        if grain != "off":
            console.print(f"[cyan]🎞️  Granulação (Film grain): {grain}[/cyan]")
            img = add_film_grain(img, grain)

        return self._save(img, out_path, prompt, negative, seed, t0,
                          width, height, steps, polish, grain)

    def _face_detail(self, image, prompt, negative, seed):
        box = detect_face_box(image)
        if box is None:
            console.print("[yellow]  ⚠ Nenhum rosto detectado, pulando etapa[/yellow]")
            return image
        x, y, w, h = box
        pad = int(0.35 * max(w, h))
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1 = min(image.width,  x + w + pad)
        y1 = min(image.height, y + h + pad)
        crop = image.crop((x0, y0, x1, y1))
        cw, ch = crop.size
        scale = 512 / max(cw, ch)
        nw, nh = (int(cw * scale) // 8) * 8, (int(ch * scale) // 8) * 8
        crop_up = crop.resize((nw, nh), Image.LANCZOS)
        refine = self._build_refine()
        face_prompt = "detailed natural face, realistic eyes, " + prompt
        fixed = refine(
            prompt=face_prompt, negative_prompt=negative,
            image=crop_up, strength=0.22,
            num_inference_steps=14, guidance_scale=6.0,
            generator=torch.Generator(device="cpu").manual_seed(seed + 2),
        ).images[0]
        fixed = fixed.resize((cw, ch), Image.LANCZOS)
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).ellipse((cw*0.05, ch*0.05, cw*0.95, ch*0.95), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=20))
        out = image.copy()
        out.paste(fixed, (x0, y0), mask)
        return out

    def _save(self, img, out_path, prompt, negative, seed, t_start,
              w, h, steps, polish, grain):
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out = out.with_name(f"{out.stem}_{seed}{out.suffix}")
        img.save(out, quality=95)

        elapsed = time.time() - t_start
        out.with_suffix(".txt").write_text(
            f"engine: sd15\nmodel: {self.model_key}\n"
            f"prompt: {prompt}\nnegative: {negative}\n"
            f"size: {img.size[0]}x{img.size[1]}\nsteps: {steps}\n"
            f"polish: {polish}\ngrain: {grain}\nseed: {seed}\n"
            f"elapsed_s: {elapsed:.1f}\n",
            encoding="utf-8",
        )
        console.print(f"\n[bold green]💾 {out.absolute()}[/bold green]")
        console.print(f"[bold]⏱ Tempo Total: {elapsed:.1f}s[/bold]\n")
        return out
