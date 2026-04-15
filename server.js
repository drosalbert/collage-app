const express = require("express");
const multer = require("multer");
const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = 3001;

const DATA_DIR   = process.env.COLLAGE_DATA_DIR || __dirname;
const UPLOAD_DIR = process.env.COLLAGE_DATA_DIR ? path.join(DATA_DIR, "uploads") : path.join(__dirname, "uploads");
const OUTPUT_DIR = process.env.COLLAGE_DATA_DIR ? path.join(DATA_DIR, "output")  : path.join(__dirname, "output");

app.use(express.static(__dirname));
app.use(express.json());
app.use("/output", express.static(OUTPUT_DIR));

const opslag = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const uniek = Date.now() + "-" + Math.round(Math.random() * 1e6);
    cb(null, uniek + path.extname(file.originalname));
  }
});

const upload = multer({ storage: opslag });

app.post("/upload", upload.array("fotos", 500), (req, res) => {
  const paden = req.files.map(f => f.path);
  res.json({ paden });
});

app.post("/genereer", (req, res) => {
  const { paden, kolommen, rijen, breedte, hoogte, gap } = req.body;

  if (!paden || paden.length === 0) {
    return res.status(400).json({ fout: "Geen foto's ontvangen" });
  }

  const uitvoer = path.join(OUTPUT_DIR, `collage-${Date.now()}.jpg`);
  const padenArg = paden.map(p => `"${p}"`).join(" ");
  const pythonScript = path.join(__dirname, "collage.py");

  const cmd = `arch -arm64 python3 "${pythonScript}" \
    --uitvoer "${uitvoer}" \
    --kolommen ${kolommen} \
    --rijen ${rijen} \
    --breedte ${breedte} \
    --hoogte ${hoogte} \
    --gap ${gap ?? 6} \
    --fotos ${padenArg}`;

  exec(cmd, { maxBuffer: 1024 * 1024 * 10 }, (err, stdout, stderr) => {
    if (err) {
      console.error(stderr);
      return res.status(500).json({ fout: "Genereren mislukt", detail: stderr });
    }
    const bestandsnaam = path.basename(uitvoer);
    res.json({ bestand: bestandsnaam });
  });
});

app.listen(PORT, () => {
  console.log(`Collage app draait op http://localhost:${PORT}`);
});
