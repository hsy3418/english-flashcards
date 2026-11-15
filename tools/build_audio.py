"""Generate en-AU audio for every card with Amazon Polly (generative voice).
Writes audio/<sha1>.mp3 and sets card["audio"]. Skips files that already exist."""
import json, hashlib, subprocess, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE, REGION = "generative", "us-east-1"
VOICES = {"audio": "Olivia", "audio_us": "Danielle"}  # en-AU, en-US
(ROOT / "audio").mkdir(exist_ok=True)
made = 0
for d in json.load(open(ROOT / "decks/index.json")):
    p = ROOT / f"decks/{d['id']}.json"
    deck = json.load(open(p))
    for c in deck["cards"]:
      culture = deck.get("type") == "culture"   # Aussie references: always en-AU audio
      for field, voice in VOICES.items():
        if culture and field == "audio_us":
            c[field] = c["audio"]; continue
        en = c.get("us", {}).get("en", c["en"]) if field == "audio_us" else c["en"]
        text = re.sub(r"\[\[|\]\]", "", en)
        name = hashlib.sha1(f"{voice}:{text}".encode()).hexdigest()[:12] + ".mp3"
        out = ROOT / "audio" / name
        if not out.exists():
            subprocess.run(["aws", "polly", "synthesize-speech", "--engine", ENGINE, "--voice-id", voice,
                            "--region", REGION, "--output-format", "mp3", "--text", text, str(out)],
                           check=True, stdout=subprocess.DEVNULL)
            made += 1
        c[field] = f"audio/{name}"
    json.dump(deck, open(p, "w"), ensure_ascii=False, indent=1)
print("generated", made)
