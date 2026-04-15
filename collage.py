import argparse
import sys
import random
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--uitvoer", required=True)
parser.add_argument("--kolommen", type=int, required=True)
parser.add_argument("--rijen", type=int, required=True)
parser.add_argument("--breedte", type=int, required=True)
parser.add_argument("--hoogte", type=int, required=True)
parser.add_argument("--gap", type=int, default=6)
parser.add_argument("--fotos", nargs="+", required=True)
args = parser.parse_args()

GAP = args.gap
ACHTERGROND = (20, 20, 20)

totaal_cellen = args.rijen * args.kolommen
fotos = args.fotos

# Vul aan met random herhalingen als er te weinig foto's zijn
if len(fotos) < totaal_cellen:
    extra = random.choices(fotos, k=totaal_cellen - len(fotos))
    fotos = fotos + extra
    random.shuffle(fotos)
else:
    fotos = fotos[:totaal_cellen]

print(f"{len(fotos)} foto's verwerken in {args.rijen} rijen x {args.kolommen} kolommen ({args.breedte}x{args.hoogte}px)")

# Verdeel foto's in rijen van 'kolommen' foto's
rijen = [fotos[i:i + args.kolommen] for i in range(0, len(fotos), args.kolommen)]

collage = Image.new("RGB", (args.breedte, args.hoogte), ACHTERGROND)

# Bereken beschikbare hoogte per rij
beschikbare_hoogte = args.hoogte - (args.rijen + 1) * GAP
rij_hoogte = beschikbare_hoogte // args.rijen

y = GAP

for rij_fotos in rijen:
    # Haal aspect ratios op
    ratios = []
    for pad in rij_fotos:
        try:
            with Image.open(pad) as img:
                ratios.append(img.width / img.height)
        except:
            ratios.append(1.5)  # standaard ratio als foto niet leesbaar is

    # Schaal alle foto's in de rij op dezelfde hoogte zodat de breedte precies klopt
    totaal_ratio = sum(ratios)
    beschikbare_breedte = args.breedte - (len(rij_fotos) + 1) * GAP
    rij_hoogte_aangepast = int(beschikbare_breedte / totaal_ratio)

    x = GAP
    for i, pad in enumerate(rij_fotos):
        foto_breedte = int(rij_hoogte_aangepast * ratios[i])
        try:
            img = Image.open(pad).convert("RGB")
            img = img.resize((foto_breedte, rij_hoogte_aangepast), Image.LANCZOS)
            collage.paste(img, (x, y))
            print(f"  Klaar: {pad.split('/')[-1]}")
        except Exception as e:
            print(f"  Overgeslagen: {pad.split('/')[-1]} ({e})", file=sys.stderr)
        x += foto_breedte + GAP

    y += rij_hoogte_aangepast + GAP

collage.save(args.uitvoer, "JPEG", quality=92)
print(f"\nOpgeslagen: {args.uitvoer}")
