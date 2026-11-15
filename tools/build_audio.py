"""Generate en-AU audio for every card with Amazon Polly (generative voice).
Writes audio/<sha1>.mp3 and sets card["audio"]. Skips files that already exist."""
import json, hashlib, subprocess, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICE, ENGINE, REGION = "Olivia", "generative", "us-east-1"
(ROOT / "audio").mkdir(exist_ok=True)
made = 0
for d in json.load(open(ROOT / "decks/index.json")):
    p = ROOT / f"decks/{d['id']}.json"
    deck = json.load(open(p))
    for c in deck["cards"]:
        text = re.sub(r"\[\[|\]\]", "", c["en"])
        name = hashlib.sha1(f"{VOICE}:{text}".encode()).hexdigest()[:12] + ".mp3"
        out = ROOT / "audio" / name
        if not out.exists():
            subprocess.run(["aws", "polly", "synthesize-speech", "--engine", ENGINE, "--voice-id", VOICE,
                            "--region", REGION, "--output-format", "mp3", "--text", text, str(out)],
                           check=True, stdout=subprocess.DEVNULL)
            made += 1
        c["audio"] = f"audio/{name}"
    json.dump(deck, open(p, "w"), ensure_ascii=False, indent=1)
print("generated", made)
