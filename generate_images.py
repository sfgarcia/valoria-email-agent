"""Script one-shot: genera imágenes de productos Valoria con Pollinations.ai."""

import urllib.request
import urllib.parse
import pathlib
import time

PRODUCTS = {
    "eco-trek.jpg": (
        "premium sustainable outdoor jacket dark minimal aesthetic, "
        "ocean recycled fabric, professional product photography, "
        "black background, luxury fashion editorial"
    ),
    "urban-flow.jpg": (
        "smart urban backpack tech streetwear minimal black, "
        "professional product photography, studio lighting, "
        "modern lifestyle accessory, dark background"
    ),
    "lumina-restore.jpg": (
        "wellness spa recovery kit botanical serenity, "
        "essential oils mist silk eye mask herbal teas, "
        "minimal packaging white background, luxury self-care product photography"
    ),
}

BASE_URL = "https://image.pollinations.ai/prompt/{prompt}?width=600&height=400&nologo=true&model=flux"
OUTPUT_DIR = pathlib.Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)


def download_image(filename: str, prompt: str) -> None:
    encoded = urllib.parse.quote(prompt)
    url = BASE_URL.format(prompt=encoded)
    dest = OUTPUT_DIR / filename
    print(f"Generando {filename}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    size_kb = dest.stat().st_size // 1024
    print(f"  Guardado: {dest} ({size_kb} KB)")


if __name__ == "__main__":
    for filename, prompt in PRODUCTS.items():
        download_image(filename, prompt)
        time.sleep(2)
    print("\nBanco de imágenes listo en images/")
