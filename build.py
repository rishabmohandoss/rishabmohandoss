"""Generate README.md in a neofetch style: ASCII portrait on the left, info on the right.

Usage: python3 build.py [photo.jpg]
Without a photo, a placeholder "RM" banner is used.
"""
import sys
from PIL import Image, ImageOps, ImageFilter

W, H = 72, 38
CW, LH = 7.22, 17
RAMP = " .:-=+*#%@"  # dark -> bright, drawn on a dark terminal


def portrait(path):
    import numpy as np
    # fit the whole head (pad, don't crop) at the real character aspect ratio
    size = (W * 4, H * 8)
    src = ImageOps.pad(Image.open(path).convert("RGB"), (round(W * CW * 8), round(H * LH * 8)), color=(200, 200, 200), centering=(0.5, 0.35)).resize(size, Image.LANCZOS)
    a = np.asarray(src).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spread = a.max(-1) - a.min(-1)
    # backdrop = saturated blue, or bright and near-gray
    bg = (b > r + 22) | ((spread < 28) & (a.max(-1) > 110))
    gray = Image.fromarray(a.mean(-1).astype("uint8"))
    from PIL import ImageFilter as F
    gl = np.asarray(gray).astype(float)
    mean = np.asarray(gray.filter(F.GaussianBlur(10))).astype(float)
    var = np.asarray(Image.fromarray(np.clip((gl - mean) ** 2, 0, 255).astype("uint8")).filter(F.GaussianBlur(10))).astype(float)
    local = 1 / (1 + np.exp(-(gl - mean) / (np.sqrt(var) + 6) * 1.6))      # local contrast: features pop
    eq = np.asarray(ImageOps.equalize(gray)).astype(float) / 255
    tone = np.clip(0.7 * local + 0.3 * eq, 0, 1) ** 0.85
    tone[bg] = 0
    t = Image.fromarray((tone * 255).astype("uint8")).resize((W, H), Image.LANCZOS)
    px = t.load()
    return ["".join(RAMP[px[x, y] * (len(RAMP) - 1) // 255] for x in range(W)).rstrip() for y in range(H)]


from xml.sax.saxutils import escape

import os
USE_TXT = os.path.exists("portrait.txt")
if USE_TXT:
    art = [l.rstrip("\n") for l in open("portrait.txt").read().rstrip("\n").split("\n")]
    A_FS, A_LH = 7.4, 7.9
    A_CW = A_FS * 0.602
    ART_W = max(len(l) for l in art) * A_CW
else:
    art = portrait(sys.argv[1] if len(sys.argv) > 1 else "face_crop.png")
    A_FS, A_LH, A_CW = 12, LH, CW
    ART_W = W * CW

FS = 12
PAD = 28
TOP = 64
X_ART = PAD
X_INFO = PAD + ART_W + 34
KEYW = 16

INFO = [
    ("head", "rishab@mohandoss"),
    ("kv", "Role", "AI Engineer / Cofounder, AdaptIQ"),
    ("kv", "Now", "SWE Co-op @ NJEDA, building Chakra"),
    ("kv", "School", "NJIT: B.S. FinTech + Tech MBA (AI)"),
    ("kv", "GPA", "3.80, Dean's List"),
    ("kv", "Wins", "Anthropic, MLH Solana, GirlHacks, Fiserv"),
    ("gap",),
    ("head", "Stack"),
    ("kv", "Languages", "Python, JavaScript, Java, SQL, Bash"),
    ("kv", "AI / ML", "PyTorch, scikit-learn, Claude API"),
    ("kv", "Vision", "MediaPipe, OpenCV"),
    ("kv", "Web", "React, Next.js, FastAPI, Node.js"),
    ("kv", "Data", "PostgreSQL, Redis, MongoDB, Firebase"),
    ("kv", "Cloud", "AWS, Azure, Docker, Terraform"),
    ("kv", "Security", "Sentinel, MITRE ATT&CK, OWASP"),
    ("gap",),
    ("head", "Leadership"),
    ("kv", "GDG @ NJIT", "Vice President, 700+ members"),
    ("kv", "Also", "TA, Resident Assistant, TAMID alum"),
    ("gap",),
    ("head", "Contact"),
    ("kv", "Website", "rishabmohandoss.com"),
    ("kv", "GitHub", "github.com/rishabmohandoss"),
    ("kv", "LinkedIn", "in/rishab-mohandoss"),
    ("kv", "Email", "rishabmohandoss@gmail.com"),
]

art_h = len(art) * A_LH
info_h = len(INFO) * LH
body_h = max(art_h, info_h)
rows = body_h / LH
height = int(TOP + body_h + 30)
width = int(X_INFO + 58 * CW + PAD)
y0 = lambda i: TOP + (i + 1) * LH + (body_h - info_h) / 2
y_art = lambda i: TOP + (i + 1) * A_LH + (body_h - art_h) / 2

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" font-size="{FS}" xml:space="preserve">']
o.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0a0a"/><stop offset="1" stop-color="#101010"/></linearGradient>
<linearGradient id="art" gradientUnits="userSpaceOnUse" x1="0" y1="{TOP}" x2="{ART_W}" y2="{TOP+body_h}"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#bdbdbd"/></linearGradient>
</defs>
<rect width="{width}" height="{height}" rx="12" fill="url(#bg)" stroke="#262626"/>
<circle cx="24" cy="24" r="6" fill="#ff5f57"/><circle cx="44" cy="24" r="6" fill="#febc2e"/><circle cx="64" cy="24" r="6" fill="#28c840"/>
<text x="{width/2}" y="28" fill="#777" text-anchor="middle">rishabmohandoss / README.md</text>''')

for i, line in enumerate(art):
    if line.strip():
        o.append(f'<text x="{X_ART}" y="{y_art(i)}" font-size="{A_FS}" fill="url(#art)">{escape(line)}</text>')

for i, r in enumerate(INFO):
    y = y0(i)
    if r[0] == "head":
        title = r[1]
        rule = "─" * max(2, 50 - len(title) - 1)
        o.append(f'<text x="{X_INFO}" y="{y}"><tspan fill="#f2f2f2" font-weight="bold">{escape(title)}</tspan> <tspan fill="#4a4a4a">{rule}</tspan></text>')
    elif r[0] == "kv":
        k, v = r[1], r[2]
        dots = "." * (KEYW - len(k) - 1)
        o.append(f'<text x="{X_INFO}" y="{y}"><tspan fill="#e8946a">{escape(k)}</tspan><tspan fill="#4a4a4a">:{dots} </tspan><tspan fill="#9fb4d1">{escape(v)}</tspan></text>')

o.append("</svg>")
open("terminal.svg", "w").write("\n".join(o))

intro = """
<img src="terminal.svg" alt="rishab@mohandoss terminal card" width="100%">

## Hi, I'm Rishab

I build AI that solves real problems. I'm a senior at NJIT (B.S. Financial Technology, concurrent Tech MBA in AI) and a cofounder of **AdaptIQ**, an interview-coaching platform for neurodivergent students that won the Anthropic Claude Builder Club Hackathon. Right now I'm a software engineering co-op at the **NJEDA**, building **Chakra**, an AI data-validation platform piloted with Fortune 500 companies. I sit between business and engineering on purpose, and I care most about access: tools that work for people standard software leaves out.

## Hackathon wins

| Win | Project |
|---|---|
| 1st place, Anthropic Claude Builder Club Hackathon | AdaptIQ |
| 1st place overall + MLH Solana track, NJIT GirlHacks | Alexandria |
| Winner, Fiserv / Rutgers Hack Day (3rd overall, Best Use of AI) | Empathy Engine |

## Featured work

| Project | What it does | Built with |
|---|---|---|
| **AdaptIQ** ([repo](https://github.com/rishabmohandoss/AdaptIQ---Rishab-)) | Mock interviews that read eye contact and voice in real time, then coach with Claude. 85% eye-contact detection, 96% transcription accuracy | React, Node.js, Claude API, MediaPipe, OpenCV, AWS (EC2, RDS, S3, VPC, IAM) |
| **Alexandria** ([repo](https://github.com/mayukha-arn/alexandria.work)) | Private AI search for company knowledge: clearance-scored access, local LLMs, and SHA-256 document hashes anchored on Solana so tampered sources are dropped before the model sees them | Next.js, TypeScript, FastAPI, Postgres, ChromaDB, Ollama, Rust (Anchor), Azure |
| **Chakra** | AI data validation for Fortune 500 pilots. Flags fabricated records in 200 ms at 95% accuracy on 250K test records | FastAPI, React, PostgreSQL, Docker, AWS, ML + LLM review |
| **Empathy Engine** | Chrome extension that detects hesitation in a call from vocal patterns and suggests how to reframe | Chrome MV3, WebSockets, Fastify, Gemini, Supabase pgvector |
| **Ometa\\*N** ([repo](https://github.com/rishabmohandoss/code-efficiency-checker)) | Static scanner for insecure, inefficient AI-generated code. Covers the OWASP Top 10 with no AI backend. Presented at NJIT AI Exploration Day | JavaScript, React |
| **Virtual Home Lab** | Azure security lab: 3 VMs, segmented VNet, 5+ simulated attacks triaged and mapped to MITRE ATT&CK | Azure, Sentinel, Defender, Active Directory |
| **Order Matching & Risk Engine** | In-memory limit order book with risk checks and circuit breakers, tested on 10,000+ transactions | Python, WebSockets, Redis, Docker, Locust |
| **Ether** ([repo](https://github.com/rishabmohandoss/Moody)) | Two-person private space that talks through mood, music and shifting clouds | React, Firebase, Framer Motion |
| **Breathe** | Chrome extension that detects lost focus and walks you through a breathing exercise | MediaPipe, JavaScript |

<details>
<summary>More projects and games</summary>

- **[Hunger Games Newsvendor](https://github.com/rishabmohandoss/Hunger-Games)**: multiplayer classroom simulation with a live leaderboard, used in business analytics teaching
- **[SpyFall](https://github.com/rishabmohandoss/SpyFall)**: online social deduction game ([play](https://rishabmohandoss.github.io/SpyFall/))
- **[Tetris Pomodoro](https://github.com/rishabmohandoss/Tetris-Pomodoro-Timer)**: breaks earn you Tetris ([demo](https://rishabmohandoss.github.io/Tetris-Pomodoro-Timer/))
- **[WhatsApp ordering agent](https://github.com/rishabmohandoss/whatsapp-bot)**: messaging agents that cut manual intervention by 60%
- **AI Investment Analysis Engine**: NLP over 2M+ financial documents on an HPC cluster
- **Stock Trading Bot**, **Resume Customization Tool**, **Conversational Anki**

</details>

## Research

- **Enrollment yield prediction** with Dean Oya Tukel: ML on 12,000+ records over 15 years (Python, scikit-learn, pandas)
- **AI accessibility for neurodivergent users** with Prof. Andrew Klobucar: design research and prototyping that feeds AdaptIQ
- **Finternet**: white paper and video on decentralized financial infrastructure

## Find me

[Website](https://rishabmohandoss.com) · [LinkedIn](https://www.linkedin.com/in/rishab-mohandoss) · [Email](mailto:rishabmohandoss@gmail.com)
"""
open("README.md", "w").write(intro)
