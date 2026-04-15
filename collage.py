import argparse
import sys
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--uitvoer", required=True)
parser.add_argument("--kolommen", type=int, required=True)
parser.add_argument("--rijen", type=int, required=True)
parser.add_argument("--breedte", type=int, required=True)
parser.add_argument("--hoogte", type=int, required=True)
parser.add_argument("--fotos", nargs="+", required=True)
args = parser.parse_args()

GAP = 6
ACHTERGROND = (20, 20, 20)

collage = Image.new("RGB", (args.breedte, args.hoogte), ACHTERGROND)

cel_breed = (args.breedte - (args.kolommen + 1) * GAP) // args.kolommen
cel_hoog  = (args.hoogte  - (args.rijen    + 1) * GAP) // args.rijen

cel_ratio = cel_breed / cel_hoog
totaal_cellen = args.rijen * args.kolommen
fotos = args.fotos[:totaal_cellen]

print(f"{len(fotos)} foto's verwerken in {args.rijen}x{args.kolommen} raster ({args.breedte}x{args.hoogte}px)")

for i, pad in enumerate(fotos):
    rij     = i // args.kolommen
    kolom   = i  % args.kolommen
    cel_x   = GAP + kolom * (cel_breed + GAP)
    cel_y   = GAP + rij   * (cel_hoog  + GAP)

    try:
        img = Image.open(pad).convert("RGB")
        img_ratio = img.width / img.height

        if img_ratio > cel_ratio:
            # Breed beeld: schaal op breedte
            nieuw_breed = cel_breed
            nieuw_hoog  = int(cel_breed / img_ratio)
        else:
            # Hoog beeld: schaal op hoogte
            nieuw_hoog  = cel_hoog
            nieuw_breed = int(cel_hoog * img_ratio)

        img = img.resize((nieuw_breed, nieuw_hoog), Image.LANCZOS)

        # Centreer in cel
        x = cel_x + (cel_breed - nieuw_breed) // 2
        y = cel_y + (cel_hoog  - nieuw_hoog)  // 2

        collage.paste(img, (x, y))
        print(f"  [{i+1}/{len(fotos)}] klaar")
    except Exception as e:
        print(f"  Overgeslagen ({e})", file=sys.stderr)

collage.save(args.uitvoer, "JPEG", quality=92)
print(f"Opgeslagen: {args.uitvoer}")
