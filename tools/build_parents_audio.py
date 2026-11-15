"""Audio for parents/ decks: full sentence, each chunk (split on ' | '), and suggested reply. Polly Olivia en-AU."""
import json, hashlib, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent / "parents"
VOICE, ENGINE, REGION = "Olivia", "generative", "us-east-1"
(ROOT / "audio").mkdir(exist_ok=True)
made = 0
def tts(text):
    global made
    name = hashlib.sha1(f"{VOICE}:{text}".encode()).hexdigest()[:12] + ".mp3"
    out = ROOT / "audio" / name
    if not out.exists():
        subprocess.run(["aws", "polly", "synthesize-speech", "--engine", ENGINE, "--voice-id", VOICE, "--region", REGION,
                        "--output-format", "mp3", "--text", text, str(out)], check=True, stdout=subprocess.DEVNULL)
        made += 1
    return f"audio/{name}"
for d in json.load(open(ROOT / "decks/index.json")):
    p = ROOT / f"decks/{d['id']}.json"; deck = json.load(open(p))
    for c in deck["cards"]:
        parts = [x.strip() for x in c["en"].split("|")]
        c["audio"] = tts(" ".join(parts))
        c["chunks"] = [{"t": x, "a": tts(x)} for x in parts] if len(parts) > 1 else []
        if c.get("reply"): c["reply"]["audio"] = tts(c["reply"]["en"].replace(" | ", " "))
    json.dump(deck, open(p, "w"), ensure_ascii=False, indent=1)
print("generated", made)
