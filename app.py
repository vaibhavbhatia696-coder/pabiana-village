
from flask import (
    Flask, render_template_string, request, redirect,
    url_for, session, flash, abort, send_from_directory, Response
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps
from xml.sax.saxutils import escape
import sqlite3
import secrets
import uuid
import io
import os
import re

# ============================================================
# PABIANA VILLAGE | GREEN + BLUE PREMIUM EDITION
# Created by Vaibhav Bhatia
# All HTML, CSS and JavaScript inside this app.py
# ============================================================

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DATA = BASE / "pabiana_data"
UPLOADS = DATA / "uploads"
DB = DATA / "website.db"

STATIC.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC))
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    MAX_CONTENT_LENGTH=12 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1"
)

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# ============================================================
# VILLAGE INFORMATION AND PHOTOS
# ============================================================

SECTIONS = [
    {
        "id": "view",
        "file": "view.png",
        "tag": "NATURAL BEAUTY",
        "title": "Beautiful Views of Pabiana",
        "hi": "पबियाना के खूबसूरत नज़ारे",
        "subtitle": "Where nature feels like home.",
        "subtitle_hi": "जहाँ प्रकृति में अपनापन महसूस होता है।",
        "description": (
            "Surrounded by the beautiful hills of Himachal "
            "Pradesh, Pabiana offers peaceful mountain views "
            "towards Krol Tibba, Solan and Chail. Green "
            "landscapes, fresh mountain air and changing "
            "clouds make this village truly special."
        ),
        "description_hi": (
            "हिमाचल प्रदेश की सुंदर पहाड़ियों से घिरा "
            "पबियाना, क्रोल टिब्बा, सोलन और चायल की ओर "
            "खूबसूरत नज़ारे प्रस्तुत करता है। हरियाली, "
            "ताज़ी हवा और शांत वातावरण इसकी खास पहचान हैं।"
        ),
        "caption": "A little closer to the clouds, a little closer to home.",
        "caption_hi": "बादलों के करीब, अपने घर के और भी करीब।",
        "keywords": ["view", "mountain", "krol", "chail", "valley"]
    },
    {
        "id": "temple",
        "file": "temple.png",
        "tag": "FAITH & HERITAGE",
        "title": "Temples and Traditions",
        "hi": "मंदिर और परंपराएँ",
        "subtitle": "Our faith. Our culture.",
        "subtitle_hi": "हमारी आस्था, हमारी संस्कृति।",
        "description": (
            "The temples of Pabiana and the surrounding "
            "region reflect the faith, culture and heritage "
            "of our community. They are a meaningful part "
            "of traditions passed down through generations."
        ),
        "description_hi": (
            "पबियाना और आसपास के मंदिर हमारी आस्था, "
            "संस्कृति और विरासत को दर्शाते हैं। "
            "ये पीढ़ियों से चली आ रही परंपराओं का "
            "महत्वपूर्ण हिस्सा हैं।"
        ),
        "caption": "Peace in the mountains, faith in our hearts.",
        "caption_hi": "पहाड़ों में शांति, दिलों में आस्था।",
        "keywords": ["temple", "mandir", "devta", "devi"]
    },
    {
        "id": "senior",
        "file": "school.png",
        "tag": "EDUCATION & FUTURE",
        "title": "Senior Secondary School Pabiana",
        "hi": "वरिष्ठ माध्यमिक विद्यालय पबियाना",
        "subtitle": "Learning today. Leading tomorrow.",
        "subtitle_hi": "आज की शिक्षा, कल का उज्ज्वल भविष्य।",
        "description": (
            "Senior Secondary School Pabiana is an important "
            "part of the village's educational identity. "
            "It represents knowledge, opportunity, confidence "
            "and the dreams of the next generation."
        ),
        "description_hi": (
            "वरिष्ठ माध्यमिक विद्यालय पबियाना गाँव की "
            "शैक्षणिक पहचान का महत्वपूर्ण हिस्सा है। "
            "यह ज्ञान, अवसर और आने वाली पीढ़ी के "
            "सपनों का प्रतीक है।"
        ),
        "caption": "A place where knowledge opens new doors.",
        "caption_hi": "जहाँ शिक्षा नए अवसरों के द्वार खोलती है।",
        "keywords": ["school", "secondary", "senior", "sen sec"]
    },
    {
        "id": "primary",
        "file": "primary.png",
        "tag": "LITTLE STEPS, BIG DREAMS",
        "title": "Primary School Pabiana",
        "hi": "प्राथमिक विद्यालय पबियाना",
        "subtitle": "Little beginnings. Beautiful futures.",
        "subtitle_hi": "छोटी शुरुआत, खूबसूरत भविष्य।",
        "description": (
            "Every great journey begins with a small step. "
            "Primary School Pabiana is where young children "
            "take their first steps into learning, friendship "
            "and a brighter future."
        ),
        "description_hi": (
            "हर बड़ी मंज़िल की शुरुआत एक छोटे कदम से "
            "होती है। प्राथमिक विद्यालय पबियाना वह "
            "स्थान है जहाँ छोटे बच्चे शिक्षा, दोस्ती "
            "और उज्ज्वल भविष्य की ओर अपना पहला कदम "
            "बढ़ाते हैं।"
        ),
        "caption": "Small steps today, endless possibilities tomorrow.",
        "caption_hi": "आज के छोटे कदम, कल की अनगिनत संभावनाएँ।",
        "keywords": ["primary", "prathmik"]
    },
    {
        "id": "panchayat",
        "file": "panchayal.png",
        "tag": "OUR COMMUNITY",
        "title": "Gram Panchayat Ser Jagas",
        "hi": "ग्राम पंचायत सेर जगास",
        "subtitle": "Together, we are stronger.",
        "subtitle_hi": "एक साथ, हम और मजबूत।",
        "description": (
            "Gram Panchayat Ser Jagas, Vikas Khand Rajgarh, "
            "is an important part of local administration "
            "and community life in the surrounding area."
        ),
        "description_hi": (
            "ग्राम पंचायत सेर जगास, विकास खंड राजगढ़, "
            "स्थानीय प्रशासन और आसपास के क्षेत्र के "
            "सामुदायिक जीवन का महत्वपूर्ण हिस्सा है।"
        ),
        "caption": "Our people. Our roots. Our community.",
        "caption_hi": "हमारे लोग, हमारी जड़ें, हमारा समुदाय।",
        "keywords": ["panchayat", "panchayal", "ser jagas"]
    },
    {
        "id": "resort",
        "file": "resort.png",
        "tag": "MOUNTAIN HOSPITALITY",
        "title": "Resort and Mountain Retreat",
        "hi": "रिज़ॉर्ट और पहाड़ी ठहराव",
        "subtitle": "Stay close to nature.",
        "subtitle_hi": "प्रकृति के और करीब।",
        "description": (
            "The resort pictured in the Pabiana area is "
            "surrounded by scenic hills and a peaceful "
            "mountain atmosphere. The beautiful landscape "
            "offers memorable surroundings for visitors."
        ),
        "description_hi": (
            "पबियाना क्षेत्र का यह रिज़ॉर्ट खूबसूरत "
            "पहाड़ियों और शांत वातावरण से घिरा हुआ है। "
            "यहाँ की प्राकृतिक सुंदरता और पहाड़ी "
            "नज़ारे इसे यादगार बनाते हैं।"
        ),
        "caption": "Beautiful mountains, peaceful moments.",
        "caption_hi": "खूबसूरत पहाड़, सुकून भरे पल।",
        "keywords": ["resort", "hotel", "homestay"]
    },
    {
        "id": "road",
        "file": "road.png",
        "tag": "THE ROAD THAT CONNECTS US",
        "title": "Main Road to Solan",
        "hi": "सोलन जाने वाली मुख्य सड़क",
        "subtitle": "Connecting Sirmaur with Solan.",
        "subtitle_hi": "सिरमौर को सोलन से जोड़ता मार्ग।",
        "description": (
            "The main road passing through the Pabiana area "
            "connects the Sirmaur region with Solan. "
            "Solan is approximately 32 kilometres away "
            "by this route. Surrounded by beautiful mountain "
            "scenery, this road is an important connection "
            "for local residents and travellers."
        ),
        "description_hi": (
            "पबियाना क्षेत्र से गुजरने वाली मुख्य सड़क "
            "सिरमौर को सोलन से जोड़ती है। इस मार्ग "
            "से सोलन लगभग 32 किलोमीटर दूर है। "
            "सुंदर पहाड़ों के बीच से गुजरने वाली यह "
            "सड़क स्थानीय लोगों और यात्रियों के लिए "
            "महत्वपूर्ण है।"
        ),
        "caption": "32 km to Solan — a beautiful journey through the hills.",
        "caption_hi": "सोलन 32 किलोमीटर — पहाड़ों के बीच खूबसूरत सफर।",
        "keywords": ["road", "highway", "solan road"]
    }
]

# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_photos (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        count = db.execute(
            "SELECT COUNT(*) FROM admins"
        ).fetchone()[0]

        password = os.environ.get("ADMIN_PASSWORD", "")

        if count == 0 and len(password) >= 12:
            db.execute(
                "INSERT INTO admins VALUES (?, ?)",
                (
                    os.environ.get("ADMIN_USERNAME", "admin"),
                    generate_password_hash(password)
                )
            )


init_db()

# ============================================================
# AUTOMATIC PHOTO DETECTION
# ============================================================

def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def find_photo(filename):
    # Exact match first
    direct = STATIC / filename

    if direct.is_file():
        return direct.relative_to(STATIC).as_posix()

    wanted_stem = normalize(Path(filename).stem)

    # Match filename with any supported image extension
    for path in STATIC.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in EXTENSIONS:
            continue

        if normalize(path.stem) == wanted_stem:
            return path.relative_to(STATIC).as_posix()

    return None


def photo_url(filename):
    relative = find_photo(filename)

    if relative:
        return url_for("static", filename=relative)

    return None


def category_for(filename):
    name = normalize(Path(filename).stem)

    # Primary must be checked before generic school.
    if "primary" in name:
        return "primary"

    if name == "school" or "secondary" in name or "sen sec" in name:
        return "senior"

    for section in SECTIONS:
        for keyword in section["keywords"]:
            if normalize(keyword) in name:
                return section["id"]

    return "other"


def all_photos():
    photos = []
    excluded = {
        "pabiana.png",
        "pabiana.jpg",
        "pabiana.jpeg",
        "pabiana.webp",
        "vaibhav.jpg",
        "vaibhav.jpeg",
        "vaibhav.png",
        "vaibhav.webp"
    }

    for path in sorted(STATIC.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in EXTENSIONS:
            continue

        if path.name.lower() in excluded:
            continue

        relative = path.relative_to(STATIC).as_posix()

        photos.append({
            "id": relative,
            "url": url_for("static", filename=relative),
            "category": category_for(path.name),
            "title": path.stem,
            "source": "static"
        })

    with get_db() as db:
        records = db.execute(
            "SELECT * FROM uploaded_photos ORDER BY created_at DESC"
        ).fetchall()

    for record in records:
        if (UPLOADS / record["filename"]).is_file():
            photos.append({
                "id": record["id"],
                "url": url_for(
                    "uploaded_photo",
                    filename=record["filename"]
                ),
                "category": record["category"],
                "title": record["title"],
                "source": "upload"
            })

    return photos


# ============================================================
# ADMIN SECURITY
# ============================================================

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)

    return session["csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def verify_csrf():
    expected = session.get("csrf", "")
    supplied = request.form.get("csrf", "")

    if not expected or not secrets.compare_digest(expected, supplied):
        abort(400)


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# PREMIUM GREEN + BLUE DESIGN
# ============================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

:root{
 --green:#00a878;
 --darkgreen:#087a62;
 --blue:#236ce7;
 --sky:#59c6e9;
 --navy:#102c42;
 --text:#203646;
 --muted:#687e8d;
 --mint:#e9fff4;
 --ice:#eaf4ff;
 --white:#fff;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
 margin:0;
 font-family:'Poppins',sans-serif;
 background:white;
 color:var(--text);
 overflow-x:hidden;
}
body.lock{overflow:hidden}
a{text-decoration:none;color:inherit}
button,input,select,textarea{font:inherit}
button{cursor:pointer}
img{display:block;max-width:100%}

.container{
 width:min(1260px,calc(100% - 64px));
 margin:auto;
}

.gradient{
 background:linear-gradient(110deg,#00a878,#246ce9);
 background-clip:text;
 -webkit-background-clip:text;
 color:transparent;
}

.kicker{
 color:var(--darkgreen);
 font-size:11px;
 font-weight:700;
 letter-spacing:2px;
}

.heading{
 font-size:clamp(36px,4.7vw,66px);
 font-weight:800;
 line-height:1.24;
 letter-spacing:-1.7px;
 margin:22px 0;
}

.btn{
 display:inline-flex;
 justify-content:center;
 align-items:center;
 padding:16px 27px;
 border-radius:13px;
 border:0;
 font-size:12px;
 font-weight:700;
 transition:transform .3s,box-shadow .3s;
}

.btn:hover{
 transform:translateY(-5px);
 box-shadow:0 16px 35px #087b9b3b;
}

.btn-primary{
 background:linear-gradient(110deg,#00a878,#246ce9);
 color:white;
}

.btn-white{
 background:white;
 color:#075d64;
}

.btn-glass{
 background:#ffffff20;
 border:1px solid #ffffff8a;
 color:white;
 backdrop-filter:blur(10px);
}

/* NAVBAR */

.navbar{
 position:absolute;
 top:0;
 left:0;
 width:100%;
 z-index:100;
 padding:22px 0;
 color:white;
 transition:.3s;
}

.navbar.sticky{
 position:fixed;
 padding:12px 0;
 background:#092e43f2;
 backdrop-filter:blur(18px);
 box-shadow:0 12px 30px #0003;
}

.nav-inner{
 display:flex;
 align-items:center;
 justify-content:space-between;
 gap:20px;
}

.brand{
 font-size:25px;
 font-weight:800;
 letter-spacing:2px;
}

.brand span{color:#8cf6cf}

.brand small{
 display:block;
 font-size:8px;
 font-weight:500;
 letter-spacing:2.3px;
}

.nav-links{
 display:flex;
 align-items:center;
 gap:24px;
 font-size:11px;
 font-weight:700;
}

.nav-links a:hover{color:#9ff5d7}

.creator{
 display:flex;
 align-items:center;
 gap:9px;
 background:#ffffff21;
 border:1px solid #ffffff60;
 border-radius:50px;
 padding:5px 12px 5px 5px;
}

.creator img,.avatar{
 width:38px;
 height:38px;
 border-radius:50%;
 object-fit:cover;
 border:2px solid #a6f4d9;
}

.avatar{
 display:grid;
 place-items:center;
 background:var(--green);
 color:white;
 font-weight:800;
}

.creator small{
 display:block;
 font-size:8px;
 color:#c8ffeb;
}

.creator strong{font-size:11px}

.menu{
 display:none;
 border:1px solid #ffffff70;
 background:#ffffff20;
 border-radius:10px;
 padding:10px 13px;
 color:white;
}

/* HERO - PABIANA.PNG FIRST */

.hero{
 height:100svh;
 min-height:690px;
 max-height:1100px;
 position:relative;
 display:flex;
 align-items:center;
 overflow:hidden;
 background:#092c40;
 color:white;
}

.hero-photo{
 position:absolute;
 inset:0;
 width:100%;
 height:100%;
 object-fit:contain;
 object-position:center;
 animation:heroEnter 1.7s ease both;
}

.hero-fallback{
 position:absolute;
 inset:0;
 background:linear-gradient(125deg,#067c71,#226ad4);
}

.hero-shade{
 position:absolute;
 inset:0;
 background:
 linear-gradient(90deg,#051d30e0,#082f4c99 55%,#082d471b),
 linear-gradient(0deg,#041c2e99,transparent 55%);
}

.hero-content{
 position:relative;
 z-index:2;
 padding:110px 0 70px;
 animation:fadeUp 1.1s ease both;
}

.hero-tag{
 display:inline-block;
 padding:12px 18px;
 border-radius:40px;
 border:1px solid #c6ffe59c;
 background:#ffffff1b;
 color:#b9ffe4;
 font-size:10px;
 letter-spacing:1.8px;
 font-weight:700;
}

.hero h1{
 font-size:clamp(53px,8vw,112px);
 font-weight:800;
 line-height:1.1;
 letter-spacing:-3px;
 margin:30px 0 22px;
}

.hero h1 span{color:#a4ffdb}

.hero p{
 max-width:570px;
 font-size:15px;
 line-height:2;
 color:#f1fbff;
}

.hero-buttons{
 display:flex;
 flex-wrap:wrap;
 gap:14px;
 margin-top:35px;
}

.scroll-note{
 position:absolute;
 z-index:3;
 bottom:30px;
 left:0;
 right:0;
 text-align:center;
 font-size:10px;
 letter-spacing:2px;
 color:#d6fff0;
}

.scroll-note span{
 display:block;
 font-size:23px;
 animation:bounce 2s infinite;
}

/* INTRO */

.intro{
 padding:125px 0;
 background:
 radial-gradient(circle at 5% 15%,#e2fff0,transparent 40%),
 radial-gradient(circle at 95% 85%,#e6f2ff,transparent 45%),
 white;
}

.intro-grid{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:80px;
 align-items:center;
}

.intro p{
 color:var(--muted);
 font-size:14px;
 line-height:2.2;
}

.intro-photo{
 height:470px;
 border-radius:28px;
 overflow:hidden;
 background:linear-gradient(120deg,#b4eedb,#bed9ff);
 box-shadow:0 24px 65px #087b9026;
}

.intro-photo img{
 width:100%;
 height:100%;
 object-fit:cover;
}

.intro-pill{
 display:inline-block;
 margin-top:22px;
 padding:12px 18px;
 border-radius:30px;
 background:#ddfaec;
 color:#08775d;
 font-size:11px;
 font-weight:700;
}

/* LEFT RIGHT ALTERNATING LAYOUT */

.places{
 padding:95px 0 25px;
}

.places-header{
 text-align:center;
 margin-bottom:100px;
}

.place{
 display:grid;
 grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr);
 gap:clamp(35px,6vw,95px);
 align-items:center;
 margin-bottom:135px;
}

.place.reverse{
 grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr);
}

.place.reverse .photo-side{order:2}
.place.reverse .text-side{order:1}

.photo-frame{
 position:relative;
 height:510px;
 padding:11px;
 border-radius:28px;
 background:linear-gradient(135deg,#dcfff0,#dbeaff);
 box-shadow:0 24px 65px #0c718d24;
}

.photo-inner{
 width:100%;
 height:100%;
 border-radius:19px;
 overflow:hidden;
 background:#e5f5f0;
 display:flex;
 align-items:center;
 justify-content:center;
}

.photo-inner img{
 width:100%;
 height:100%;
 object-fit:cover;
 transition:transform .7s ease;
}

.photo-frame:hover img{
 transform:scale(1.045);
}

/* ROAD PHOTO MUST SHOW COMPLETELY */

.place.road .photo-inner img{
 object-fit:contain;
}

.place.road .photo-frame:hover img{
 transform:none;
}

.photo-placeholder{
 padding:30px;
 color:#167c77;
 text-align:center;
 font-weight:700;
}

.photo-number{
 position:absolute;
 bottom:-20px;
 right:23px;
 padding:14px 19px;
 border-radius:13px;
 background:linear-gradient(110deg,#00a878,#236ce7);
 color:white;
 font-size:11px;
 font-weight:700;
 box-shadow:0 12px 30px #126d9a35;
}

.place.reverse .photo-number{
 right:auto;
 left:23px;
}

.place-tag{
 display:inline-block;
 background:#e5fbf0;
 color:#087d63;
 padding:10px 15px;
 border-radius:9px;
 font-size:10px;
 font-weight:700;
 letter-spacing:1.5px;
}

.text-side h3{
 font-size:clamp(32px,3.8vw,53px);
 font-weight:800;
 line-height:1.3;
 letter-spacing:-1.4px;
 margin:22px 0 13px;
}

.subtitle{
 font-size:15px;
 font-weight:700;
 color:var(--blue);
 margin-bottom:20px;
}

.description{
 font-size:14px;
 line-height:2.2;
 color:var(--muted);
}

.caption{
 margin-top:25px;
 padding:18px 20px;
 background:linear-gradient(110deg,#e4faef,#e8f2ff);
 border-left:4px solid #00aa84;
 border-radius:0 12px 12px 0;
 font-size:13px;
 line-height:1.9;
 font-weight:600;
 color:#176e79;
}

.place-link{
 display:inline-block;
 margin-top:25px;
 color:var(--blue);
 font-size:12px;
 font-weight:700;
}

.distance{
 display:inline-block;
 margin-top:15px;
 background:#e5f5ff;
 color:#145cb5;
 padding:12px 17px;
 border-radius:10px;
 font-size:12px;
 font-weight:700;
}

/* MESSAGE */

.message{
 padding:115px 20px;
 text-align:center;
 background:linear-gradient(120deg,#075e62,#098a75,#205dc2);
 color:white;
}

.message h2{
 max-width:900px;
 margin:20px auto;
 font-size:clamp(30px,4vw,55px);
 line-height:1.5;
 font-weight:700;
}

.message p{
 font-size:11px;
 letter-spacing:2px;
 color:#d0ffec;
}

/* GALLERY */

.gallery-section{
 padding:120px 0;
 background:linear-gradient(130deg,#effff7,#edf5ff);
}

.gallery-head{
 display:flex;
 justify-content:space-between;
 align-items:end;
 gap:35px;
 margin-bottom:48px;
}

.gallery-head p{
 max-width:340px;
 font-size:13px;
 line-height:2;
 color:var(--muted);
}

.gallery-grid{
 display:grid;
 grid-template-columns:repeat(3,minmax(0,1fr));
 grid-auto-rows:265px;
 gap:16px;
}

.gallery-card{
 position:relative;
 padding:0;
 border:0;
 border-radius:17px;
 overflow:hidden;
 background:#c7eade;
}

.gallery-card img{
 width:100%;
 height:100%;
 object-fit:cover;
 transition:transform .5s;
}

.gallery-card:hover img{
 transform:scale(1.07);
}

.gallery-card span{
 position:absolute;
 top:15px;
 right:15px;
 background:white;
 color:#087a66;
 border-radius:50%;
 width:38px;
 height:38px;
 display:grid;
 place-items:center;
 font-size:20px;
 opacity:0;
 transition:.3s;
}

.gallery-card:hover span{opacity:1}

.gallery-action{
 text-align:center;
 margin-top:50px;
}

.empty{
 grid-column:1/-1;
 text-align:center;
 padding:70px;
 color:var(--muted);
}

.page-hero{
 padding:185px 0 100px;
 color:white;
 background:linear-gradient(120deg,#075a62,#0b8d83,#236ce7);
}

.page-hero h1{
 font-size:clamp(48px,7vw,86px);
 font-weight:800;
 letter-spacing:-2px;
}

.gallery-page{padding:90px 0 130px}

.filters{
 display:flex;
 flex-wrap:wrap;
 gap:10px;
 margin-bottom:35px;
}

.filter{
 padding:11px 17px;
 background:white;
 border:1px solid #cce8dd;
 border-radius:30px;
 font-size:11px;
 font-weight:600;
}

.filter.active{
 background:linear-gradient(110deg,#00a878,#236ce7);
 color:white;
 border-color:transparent;
}

/* FOOTER */

.footer{
 background:#102b40;
 color:white;
 padding:85px 0 30px;
}

.footer-grid{
 display:grid;
 grid-template-columns:1.5fr 1fr 1fr;
 gap:60px;
}

.footer h3{
 font-size:27px;
 font-weight:800;
 letter-spacing:2px;
}

.footer h4{
 color:#91efd0;
 font-size:11px;
 letter-spacing:2px;
}

.footer p,.footer a{
 color:#b9d4dd;
 font-size:12px;
 line-height:2.1;
}

.footer a{
 display:block;
 margin:9px 0;
}

.footer-bottom{
 display:flex;
 justify-content:space-between;
 align-items:center;
 gap:25px;
 border-top:1px solid #ffffff25;
 margin-top:60px;
 padding-top:30px;
 font-size:11px;
 color:#b9d4dd;
}

.developer{
 display:flex;
 align-items:center;
 gap:12px;
}

.developer img,.developer .avatar{
 width:55px;
 height:55px;
 border-radius:50%;
 object-fit:cover;
 border:2px solid #9ef2d4;
}

.developer small{
 display:block;
 font-size:9px;
}

.developer strong{
 display:block;
 font-size:14px;
 color:white;
 margin-top:4px;
}

/* FULLSCREEN GALLERY */

.lightbox{
 display:none;
 position:fixed;
 inset:0;
 z-index:999;
 align-items:center;
 justify-content:center;
 padding:55px;
 background:#061725f7;
}

.lightbox.active{display:flex}

.lightbox img{
 max-width:90vw;
 max-height:85vh;
 width:auto;
 height:auto;
 object-fit:contain;
 border-radius:8px;
}

.lightbox button{
 position:absolute;
 width:45px;
 height:45px;
 border-radius:50%;
 border:1px solid #ffffff80;
 background:#ffffff25;
 color:white;
 font-size:27px;
}

.close-photo{top:22px;right:22px}
.prev-photo{top:50%;left:18px}
.next-photo{top:50%;right:18px}

.photo-count{
 position:absolute;
 bottom:20px;
 color:#d5e9ef;
 font-size:12px;
}

/* ANIMATIONS */

@keyframes heroEnter{
 from{opacity:0;transform:scale(1.035)}
 to{opacity:1;transform:scale(1)}
}

@keyframes fadeUp{
 from{opacity:0;transform:translateY(38px)}
 to{opacity:1;transform:translateY(0)}
}

@keyframes bounce{
 0%,100%{transform:translateY(0)}
 50%{transform:translateY(9px)}
}

.reveal{
 opacity:0;
 transform:translateY(42px);
 transition:opacity .85s ease,transform .85s ease;
}

.reveal.visible{
 opacity:1;
 transform:translateY(0);
}

/* ADMIN */

.admin-body{
 min-height:100vh;
 padding:60px 20px;
 background:linear-gradient(120deg,#e2fff0,#e8f3ff);
}

.admin-panel{
 max-width:1000px;
 margin:auto;
 padding:40px;
 background:white;
 border-radius:24px;
 box-shadow:0 24px 65px #086d8a25;
}

.admin-panel.small{max-width:460px}

.admin-panel h1{
 font-size:35px;
 font-weight:800;
}

.admin-panel label{
 display:block;
 margin:18px 0;
 font-size:12px;
 font-weight:700;
}

.admin-panel input,
.admin-panel textarea,
.admin-panel select{
 display:block;
 width:100%;
 margin-top:9px;
 padding:13px;
 border:1px solid #c9e3dc;
 border-radius:9px;
}

.admin-panel textarea{min-height:95px}

.admin-panel button{
 background:linear-gradient(110deg,#00a878,#236ce7);
 border:0;
 border-radius:9px;
 padding:13px 20px;
 color:white;
}

.admin-columns{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:40px;
}

.admin-photo{
 display:flex;
 align-items:center;
 gap:15px;
 padding:15px 0;
 border-bottom:1px solid #e7efeb;
}

.admin-photo img{
 width:85px;
 height:65px;
 object-fit:cover;
 border-radius:8px;
}

.admin-photo div{flex:1}

.flash{
 padding:14px;
 margin:15px 0;
 background:#e1f9ec;
 color:#08705b;
 border-radius:9px;
}

/* RESPONSIVE */

@media(max-width:1050px){
 .container{width:calc(100% - 44px)}

 .nav-links{
  display:none;
  position:absolute;
  top:78px;
  left:20px;
  right:20px;
  background:#103a4c;
  border-radius:14px;
  padding:22px;
  flex-direction:column;
  align-items:stretch;
 }

 .nav-links.open{display:flex}
 .menu{display:block}

 .intro-grid{
  grid-template-columns:1fr;
  gap:45px;
 }

 .place,.place.reverse{
  grid-template-columns:1fr;
  gap:45px;
  margin-bottom:105px;
 }

 .place.reverse .photo-side,
 .place.reverse .text-side{
  order:initial;
 }

 .photo-frame{height:430px}

 .footer-grid{grid-template-columns:1fr 1fr}
 .footer-grid>div:first-child{grid-column:span 2}
}

@media(max-width:600px){
 .container{width:calc(100% - 32px)}
 .brand{font-size:19px}
 .creator small,.creator strong{display:none}
 .hero{min-height:670px}
 .hero h1{font-size:52px;letter-spacing:-2px}
 .hero p{font-size:13px}
 .intro{padding:90px 0}
 .intro-photo{height:330px}
 .heading{font-size:38px}
 .places{padding-top:65px}
 .places-header{margin-bottom:65px}
 .photo-frame{height:330px;padding:8px}
 .photo-inner{border-radius:16px}
 .text-side h3{font-size:34px}
 .gallery-head{display:block}
 .gallery-grid{
  grid-template-columns:repeat(2,minmax(0,1fr));
  grid-auto-rows:180px;
  gap:9px;
 }
 .gallery-section{padding:90px 0}
 .footer-grid{grid-template-columns:1fr}
 .footer-grid>div:first-child{grid-column:auto}
 .footer-bottom{flex-direction:column;align-items:flex-start}
 .lightbox{padding:45px 10px}
 .prev-photo{left:5px}
 .next-photo{right:5px}
 .admin-columns{grid-template-columns:1fr}
 .admin-panel{padding:25px}
}

@media(prefers-reduced-motion:reduce){
 *,*:before,*:after{
  animation:none!important;
  transition:none!important;
  scroll-behavior:auto!important;
 }
 .reveal{opacity:1;transform:none}
}
"""

# ============================================================
# MAIN WEBSITE HTML
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#102b40">
<meta name="author" content="Vaibhav Bhatia">
<meta name="description" content="Discover Pabiana Village, District Sirmaur, Himachal Pradesh. Explore mountains, schools, temples, Gram Panchayat Ser Jagas and the scenic road to Solan.">
<title>{{ 'Photo Gallery' if page=='gallery' else 'Pabiana Village' }} | Himachal Pradesh</title>
<style>{{ css|safe }}</style>
</head>
<body>

<header class="navbar" id="navbar">
 <div class="container nav-inner">

  <a href="/" class="brand">
   PABIANA<span>.</span>
   <small>THE HIMALAYAN EXPERIENCE</small>
  </a>

  <nav class="nav-links" id="navLinks">
   <a href="/">HOME</a>
   <a href="/#about">ABOUT</a>
   <a href="/#places">EXPLORE</a>
   <a href="/gallery">GALLERY</a>
   <a href="{{ url_for('change_language',code='hi' if lang=='en' else 'en',next=request.path) }}">
    {{ 'हिंदी' if lang=='en' else 'ENGLISH' }}
   </a>
  </nav>

  <div class="creator">
   {% if portrait %}
    <img src="{{ portrait }}" alt="Vaibhav Bhatia">
   {% else %}
    <div class="avatar">V</div>
   {% endif %}
   <div>
    <small>CREATED BY</small>
    <strong>Vaibhav Bhatia</strong>
   </div>
  </div>

  <button class="menu" id="menuBtn" aria-label="Open menu">
   ☰
  </button>

 </div>
</header>

{% if page=='home' %}

<!-- FIRST SCREEN: PABIANA.PNG -->

<section class="hero">

 {% if hero %}
  <img class="hero-photo"
       src="{{ hero }}"
       alt="Pabiana Village"
       fetchpriority="high">
 {% else %}
  <div class="hero-fallback"></div>
 {% endif %}

 <div class="hero-shade"></div>

 <div class="container hero-content">

  <div class="hero-tag">
   ✦ SIRMAUR · HIMACHAL PRADESH · INDIA
  </div>

  {% if lang=='en' %}

   <h1>
    Welcome to<br>
    <span>Pabiana Village.</span>
   </h1>

   <p>
    A beautiful Himalayan village surrounded by
    green mountains, peaceful valleys and
    timeless traditions. Discover the place
    we proudly call home.
   </p>

  {% else %}

   <h1>
    स्वागत है<br>
    <span>पबियाना गाँव में।</span>
   </h1>

   <p>
    हरे-भरे पहाड़ों, शांत घाटियों और हिमाचल
    प्रदेश की प्राकृतिक सुंदरता से घिरा
    हमारा प्यारा गाँव।
   </p>

  {% endif %}

  <div class="hero-buttons">
   <a href="#places" class="btn btn-white">
    EXPLORE PABIANA ↗
   </a>

   <a href="/gallery" class="btn btn-glass">
    VIEW ALL PHOTOS ↗
   </a>
  </div>

 </div>

 <div class="scroll-note">
  SCROLL TO EXPLORE
  <span>↓</span>
 </div>

</section>

<!-- INTRODUCTION -->

<section class="intro" id="about">
 <div class="container intro-grid">

  <div class="reveal">

   <div class="kicker">WELCOME TO OUR HOME</div>

   <h2 class="heading">
    {% if lang=='en' %}
     A beautiful village.<br>
     <span class="gradient">A special feeling.</span>
    {% else %}
     हमारा खूबसूरत गाँव।<br>
     <span class="gradient">हमारी खास पहचान।</span>
    {% endif %}
   </h2>

   <p>
    {% if lang=='en' %}
     Pabiana is a beautiful village in District
     Sirmaur, Himachal Pradesh. From peaceful
     mountain views to its schools, temples and
     community life, every corner has a story.
    {% else %}
     पबियाना हिमाचल प्रदेश के जिला सिरमौर में
     स्थित एक खूबसूरत गाँव है। यहाँ के पहाड़,
     विद्यालय, मंदिर और सामुदायिक जीवन
     इसकी विशेष पहचान हैं।
    {% endif %}
   </p>

   <div class="intro-pill">
    ✦ PROUDLY PABIANA · PROUDLY HIMACHALI
   </div>

  </div>

  <div class="intro-photo reveal">
   {% if intro %}
    <img src="{{ intro }}"
         alt="Pabiana mountain view"
         loading="lazy">
   {% endif %}
  </div>

 </div>
</section>

<!-- LEFT RIGHT PHOTO SECTIONS -->

<section class="places" id="places">
 <div class="container">

  <div class="places-header reveal">
   <div class="kicker">
    DISCOVER OUR BEAUTIFUL VILLAGE
   </div>

   <h2 class="heading">
    Places that make<br>
    <span class="gradient">Pabiana special.</span>
   </h2>
  </div>

  {% for section in sections %}

   <article
    id="{{ section.id }}"
    class="place {% if loop.index is even %}reverse{% endif %} {% if section.id=='road' %}road{% endif %}"
   >

    <div class="photo-side reveal">

     <div class="photo-frame">
      <div class="photo-inner">

       {% if section.photo %}
        <img src="{{ section.photo }}"
             alt="{{ section.title }}"
             loading="lazy">
       {% else %}
        <div class="photo-placeholder">
         {{ section.title }}
         <p>Photo will appear here when added.</p>
        </div>
       {% endif %}

      </div>

      <div class="photo-number">
       {{ '%02d'|format(loop.index) }} / PABIANA
      </div>
     </div>

    </div>

    <div class="text-side reveal">

     <div class="place-tag">
      {{ section.tag }}
     </div>

     <h3>
      {{ section.title if lang=='en' else section.hi }}
     </h3>

     <div class="subtitle">
      {{ section.subtitle if lang=='en' else section.subtitle_hi }}
     </div>

     <p class="description">
      {{ section.description if lang=='en' else section.description_hi }}
     </p>

     {% if section.id=='road' %}
      <div class="distance">
       📍 SOLAN — APPROX. 32 KM
      </div>
     {% endif %}

     <div class="caption">
      ✦ {{ section.caption if lang=='en' else section.caption_hi }}
     </div>

     <a href="/gallery?category={{ section.id }}"
        class="place-link">
      VIEW PHOTOGRAPHS ↗
     </a>

    </div>

   </article>

  {% endfor %}

 </div>
</section>

<!-- MESSAGE -->

<section class="message">
 <div class="container reveal">

  <p>THE SPIRIT OF PABIANA</p>

  <h2>
   Some places are more than destinations.
   They are memories, belonging and home.
  </h2>

  <p>✦ PABIANA · HIMACHAL PRADESH ✦</p>

 </div>
</section>

<!-- GALLERY PREVIEW -->

<section class="gallery-section">
 <div class="container">

  <div class="gallery-head reveal">

   <div>
    <div class="kicker">OUR PHOTO COLLECTION</div>

    <h2 class="heading">
     Every photograph<br>
     <span class="gradient">tells a story.</span>
    </h2>
   </div>

   <p>
    Discover the mountains, schools, temples,
    panchayat, resort and scenic road of Pabiana.
   </p>

  </div>

  <div class="gallery-grid">

   {% for photo in photos[:9] %}

    <button class="gallery-card js-photo"
            data-src="{{ photo.url }}"
            aria-label="Open photograph">

     <img src="{{ photo.url }}"
          alt="Pabiana Village photograph"
          loading="lazy">

     <span>↗</span>

    </button>

   {% else %}

    <div class="empty">
     Add photographs to the static folder.
    </div>

   {% endfor %}

  </div>

  <div class="gallery-action">
   <a href="/gallery" class="btn btn-primary">
    VIEW ALL PHOTOS ↗
   </a>
  </div>

 </div>
</section>

{% else %}

<!-- FULL GALLERY PAGE -->

<section class="page-hero">
 <div class="container">

  <div class="hero-tag">
   PABIANA PHOTO COLLECTION
  </div>

  <h1>Our Beautiful Moments.</h1>

  <p>Explore Pabiana through photographs.</p>

 </div>
</section>

<section class="gallery-page">
 <div class="container">

  <div class="filters">

   <a href="/gallery"
      class="filter {% if not selected %}active{% endif %}">
    All Photos
   </a>

   {% for section in sections %}

    <a href="/gallery?category={{ section.id }}"
       class="filter {% if selected==section.id %}active{% endif %}">
     {{ section.title }}
    </a>

   {% endfor %}

   <a href="/gallery?category=other"
      class="filter {% if selected=='other' %}active{% endif %}">
    Other
   </a>

  </div>

  <div class="gallery-grid">

   {% for photo in photos %}

    <button class="gallery-card js-photo"
            data-src="{{ photo.url }}"
            aria-label="Open photograph">

     <img src="{{ photo.url }}"
          alt="Pabiana photograph"
          loading="lazy">

     <span>↗</span>

    </button>

   {% else %}

    <div class="empty">
     No photos found in this category.
    </div>

   {% endfor %}

  </div>

  <div class="gallery-action">
   <a href="/" class="btn btn-primary">
    ← BACK TO HOME
   </a>
  </div>

 </div>
</section>

{% endif %}

<!-- FOOTER -->

<footer class="footer">
 <div class="container">

  <div class="footer-grid">

   <div>
    <h3>PABIANA.</h3>

    <p>
     A digital celebration of our village,
     our culture, our community and
     the beautiful Himalayan landscape.
    </p>
   </div>

   <div>
    <h4>EXPLORE</h4>
    <a href="/">Home</a>
    <a href="/#about">About</a>
    <a href="/#places">Explore</a>
    <a href="/gallery">Gallery</a>
   </div>

   <div>
    <h4>LOCATION</h4>

    <p>
     Pabiana Village<br>
     District Sirmaur<br>
     Himachal Pradesh<br>
     India
    </p>
   </div>

  </div>

  <div class="footer-bottom">

   <div>
    © {{ year }} Pabiana Village.
    All rights reserved.
   </div>

   <div class="developer">

    {% if portrait %}
     <img src="{{ portrait }}"
          alt="Vaibhav Bhatia">
    {% else %}
     <div class="avatar">V</div>
    {% endif %}

    <div>
     <small>CREATED & DEVELOPED BY</small>
     <strong>Vaibhav Bhatia</strong>
    </div>

   </div>

  </div>

 </div>
</footer>

<!-- FULLSCREEN PHOTO VIEWER -->

<div class="lightbox"
     id="lightbox"
     role="dialog"
     aria-modal="true"
     aria-label="Photo viewer">

 <button class="close-photo"
         id="closePhoto"
         aria-label="Close">×</button>

 <button class="prev-photo"
         id="prevPhoto"
         aria-label="Previous">‹</button>

 <img id="largePhoto" alt="Pabiana photograph">

 <div class="photo-count" id="photoCount"></div>

 <button class="next-photo"
         id="nextPhoto"
         aria-label="Next">›</button>

</div>

<script>
(function(){

 const navbar=document.getElementById("navbar");
 const menu=document.getElementById("menuBtn");
 const links=document.getElementById("navLinks");

 function updateNav(){
  navbar.classList.toggle("sticky",window.scrollY>25);
 }

 updateNav();

 window.addEventListener(
  "scroll",updateNav,{passive:true}
 );

 menu.addEventListener("click",()=>{
  links.classList.toggle("open");
 });

 links.querySelectorAll("a").forEach(link=>{
  link.addEventListener("click",()=>{
   links.classList.remove("open");
  });
 });

 // SMOOTH SCROLL ANIMATIONS

 const revealItems=document.querySelectorAll(".reveal");

 if("IntersectionObserver" in window){

  const observer=new IntersectionObserver(
   entries=>{
    entries.forEach(entry=>{
     if(entry.isIntersecting){
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
     }
    });
   },
   {threshold:0.08,rootMargin:"0px 0px 35px 0px"}
  );

  revealItems.forEach(item=>observer.observe(item));

 }else{
  revealItems.forEach(item=>{
   item.classList.add("visible");
  });
 }

 // FULLSCREEN PHOTO GALLERY

 const photos=[...document.querySelectorAll(".js-photo")];
 const lightbox=document.getElementById("lightbox");
 const large=document.getElementById("largePhoto");
 const count=document.getElementById("photoCount");

 let current=0;
 let lastFocus=null;

 function showPhoto(index){
  if(!photos.length)return;

  current=(index+photos.length)%photos.length;

  large.src=photos[current].dataset.src;

  count.textContent=(current+1)+" / "+photos.length;

  lightbox.classList.add("active");
  document.body.classList.add("lock");

  document.getElementById("closePhoto").focus();
 }

 function closePhoto(){
  lightbox.classList.remove("active");
  document.body.classList.remove("lock");
  large.removeAttribute("src");

  if(lastFocus)lastFocus.focus();
 }

 photos.forEach((photo,index)=>{
  photo.addEventListener("click",()=>{
   lastFocus=photo;
   showPhoto(index);
  });
 });

 document.getElementById("closePhoto").onclick=closePhoto;

 document.getElementById("prevPhoto").onclick=()=>{
  showPhoto(current-1);
 };

 document.getElementById("nextPhoto").onclick=()=>{
  showPhoto(current+1);
 };

 lightbox.addEventListener("click",event=>{
  if(event.target===lightbox)closePhoto();
 });

 document.addEventListener("keydown",event=>{
  if(!lightbox.classList.contains("active"))return;

  if(event.key==="Escape")closePhoto();
  if(event.key==="ArrowLeft")showPhoto(current-1);
  if(event.key==="ArrowRight")showPhoto(current+1);
 });

 let touchStart=0;

 lightbox.addEventListener("touchstart",event=>{
  touchStart=event.changedTouches[0].screenX;
 },{passive:true});

 lightbox.addEventListener("touchend",event=>{
  const delta=event.changedTouches[0].screenX-touchStart;

  if(Math.abs(delta)>60){
   showPhoto(current+(delta<0?1:-1));
  }
 },{passive:true});

})();
</script>

</body>
</html>
"""

# ============================================================
# ADMIN HTML
# ============================================================

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pabiana Admin Studio</title>
<style>{{ css|safe }}</style>
</head>
<body>

<div class="admin-body">
 <div class="admin-panel {% if login %}small{% endif %}">

  <a href="/">← Back to Website</a>

  <h1>
   {{ 'Admin Login' if login else 'Pabiana Photo Studio' }}
  </h1>

  {% for message in get_flashed_messages() %}
   <div class="flash">{{ message }}</div>
  {% endfor %}

  {% if login %}

   <form method="POST">

    <input type="hidden"
           name="csrf"
           value="{{ csrf_token() }}">

    <label>
     Username
     <input name="username" required>
    </label>

    <label>
     Password
     <input name="password" type="password" required>
    </label>

    <button type="submit">LOGIN</button>

   </form>

  {% else %}

   <form method="POST" action="/admin/logout">

    <input type="hidden"
           name="csrf"
           value="{{ csrf_token() }}">

    <button type="submit">Logout</button>

   </form>

   <div class="admin-columns">

    <div>
     <h2>Upload New Photo</h2>

     <form method="POST" enctype="multipart/form-data">

      <input type="hidden"
             name="csrf"
             value="{{ csrf_token() }}">

      <label>
       Select Photo
       <input type="file"
              name="photo"
              accept="image/jpeg,image/png,image/webp"
              required>
      </label>

      <label>
       Photo Title
       <input name="title" maxlength="100" required>
      </label>

      <label>
       Description
       <textarea name="description"
                 maxlength="400"></textarea>
      </label>

      <label>
       Category
       <select name="category">

        {% for section in sections %}
         <option value="{{ section.id }}">
          {{ section.title }}
         </option>
        {% endfor %}

        <option value="other">Other Photos</option>

       </select>
      </label>

      <button type="submit">UPLOAD PHOTO</button>

     </form>
    </div>

    <div>
     <h2>Website Photo Names</h2>

     <p>Homepage: pabiana.png</p>
     <p>Views: view.png</p>
     <p>Temple: temple.png</p>
     <p>Senior Secondary School: school.png</p>
     <p>Primary School: primary.png</p>
     <p>Panchayat: panchayal.png</p>
     <p>Resort: resort.png</p>
     <p>Road: road.png</p>
     <p>Developer: vaibhav.jpg</p>

    </div>

   </div>

   <h2 style="margin-top:45px">
    Uploaded Photos
   </h2>

   {% for photo in photos %}

    <div class="admin-photo">

     <img src="{{ photo.url }}"
          alt="{{ photo.title }}">

     <div>
      <strong>{{ photo.title }}</strong>
      <p>{{ photo.category }}</p>
     </div>

     <form method="POST"
           action="/admin/delete/{{ photo.id }}"
           onsubmit="return confirm('Delete this photo?')">

      <input type="hidden"
             name="csrf"
             value="{{ csrf_token() }}">

      <button type="submit">Delete</button>

     </form>

    </div>

   {% else %}
    <p>No uploaded photos yet.</p>
   {% endfor %}

  {% endif %}

 </div>
</div>

</body>
</html>
"""

# ============================================================
# RENDER WEBSITE
# ============================================================

def render_website(page="home", selected=""):
    photos = all_photos()
    sections = []

    for section in SECTIONS:
        item = dict(section)

        # First try the expected static photo.
        item["photo"] = photo_url(section["file"])

        # If not found, use a photo from the same category.
        if not item["photo"]:
            matches = [
                photo for photo in photos
                if photo["category"] == section["id"]
            ]

            if matches:
                item["photo"] = matches[0]["url"]

        sections.append(item)

    # Main gallery begins with one image per category.
    preview = []
    seen = set()

    for section in sections:
        if section["photo"] and section["photo"] not in seen:
            matching = next(
                (
                    photo for photo in photos
                    if photo["url"] == section["photo"]
                ),
                None
            )

            if matching:
                preview.append(matching)
                seen.add(matching["url"])

    for photo in photos:
        if photo["url"] not in seen:
            preview.append(photo)
            seen.add(photo["url"])

    if page == "gallery" and selected:
        visible = [
            photo for photo in photos
            if photo["category"] == selected
        ]
    elif page == "home":
        visible = preview
    else:
        visible = photos

    intro = photo_url("view.png")

    if not intro and preview:
        intro = preview[0]["url"]

    return render_template_string(
        HTML,
        css=CSS,
        page=page,
        lang=session.get("language", "en"),
        sections=sections,
        photos=visible,
        selected=selected,
        hero=photo_url("pabiana.png"),
        intro=intro,
        portrait=photo_url("vaibhav.jpg"),
        year=datetime.now().year
    )


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route("/")
def home():
    return render_website()


@app.route("/gallery")
def gallery():
    selected = request.args.get("category", "")

    valid = {section["id"] for section in SECTIONS}
    valid.add("other")

    if selected not in valid:
        selected = ""

    return render_website("gallery", selected)


@app.route("/language/<code>")
def change_language(code):
    if code not in ("en", "hi"):
        abort(404)

    session["language"] = code

    destination = request.args.get("next", "/")

    if (
        not destination.startswith("/")
        or destination.startswith("//")
        or destination.startswith("/\\")
    ):
        destination = "/"

    return redirect(destination)


@app.route("/uploaded/<filename>")
def uploaded_photo(filename):
    with get_db() as db:
        record = db.execute(
            "SELECT 1 FROM uploaded_photos WHERE filename=?",
            (filename,)
        ).fetchone()

    if not record:
        abort(404)

    return send_from_directory(UPLOADS, filename)


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        verify_csrf()

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        with get_db() as db:
            admin = db.execute(
                "SELECT * FROM admins WHERE username=?",
                (username,)
            ).fetchone()

        if admin and check_password_hash(
            admin["password_hash"], password
        ):
            session.clear()
            session["admin"] = username
            csrf_token()

            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.")

    return render_template_string(
        ADMIN_HTML,
        css=CSS,
        login=True,
        sections=SECTIONS,
        photos=[]
    )


# ============================================================
# ADMIN PHOTO UPLOAD
# ============================================================

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    if request.method == "POST":
        verify_csrf()

        file = request.files.get("photo")
        title = request.form.get("title", "").strip()[:100]
        description = request.form.get(
            "description", ""
        ).strip()[:400]
        category = request.form.get("category", "other")

        valid = {section["id"] for section in SECTIONS}
        valid.add("other")

        if not file or not title or category not in valid:
            flash("Please enter valid photo details.")
            return redirect(url_for("admin_dashboard"))

        filename = uuid.uuid4().hex + ".jpg"
        destination = UPLOADS / filename

        try:
            raw = file.read()

            with Image.open(io.BytesIO(raw)) as check:
                check.verify()

            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in ("JPEG", "PNG", "WEBP"):
                    raise ValueError("Unsupported image format")

                if image.width * image.height > 30_000_000:
                    raise ValueError("Image too large")

                image = ImageOps.exif_transpose(image)
                image = image.convert("RGB")
                image.thumbnail((2200, 2200))

                image.save(
                    destination,
                    "JPEG",
                    quality=91,
                    optimize=True
                )

            with get_db() as db:
                db.execute("""
                    INSERT INTO uploaded_photos
                    (id, filename, title, description,
                     category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    uuid.uuid4().hex,
                    filename,
                    title,
                    description,
                    category,
                    datetime.now().isoformat()
                ))

            flash("Photo uploaded successfully!")

        except (OSError, ValueError, Image.DecompressionBombError):
            destination.unlink(missing_ok=True)
            flash("Unable to upload this photo.")

        return redirect(url_for("admin_dashboard"))

    uploaded = [
        photo for photo in all_photos()
        if photo["source"] == "upload"
    ]

    return render_template_string(
        ADMIN_HTML,
        css=CSS,
        login=False,
        sections=SECTIONS,
        photos=uploaded
    )


# ============================================================
# DELETE UPLOADED PHOTO
# ============================================================

@app.route("/admin/delete/<photo_id>", methods=["POST"])
@admin_required
def delete_photo(photo_id):
    verify_csrf()

    with get_db() as db:
        record = db.execute(
            "SELECT filename FROM uploaded_photos WHERE id=?",
            (photo_id,)
        ).fetchone()

        if record:
            db.execute(
                "DELETE FROM uploaded_photos WHERE id=?",
                (photo_id,)
            )

    if record:
        (UPLOADS / record["filename"]).unlink(missing_ok=True)

    flash("Photo deleted successfully.")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    verify_csrf()
    session.clear()

    return redirect(url_for("home"))


# ============================================================
# SEO
# ============================================================

@app.route("/robots.txt")
def robots():
    sitemap_url = url_for("sitemap", _external=True)

    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Sitemap: " + sitemap_url + "\n"
    )

    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    urls = [
        url_for("home", _external=True),
        url_for("gallery", _external=True)
    ]

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(
            "<url><loc>" + escape(url) + "</loc></url>"
            for url in urls
        )
        + "</urlset>"
    )

    return Response(xml, mimetype="application/xml")


# ============================================================
# START WEBSITE
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PABIANA VILLAGE — PREMIUM GREEN & BLUE")
    print("Created by Vaibhav Bhatia")
    print("=" * 60)

    required = [
        "pabiana.png",
        "view.png",
        "temple.png",
        "school.png",
        "primary.png",
        "panchayal.png",
        "resort.png",
        "road.png",
        "vaibhav.jpg"
    ]

    for filename in required:
        found = find_photo(filename)
        print(f"{filename}: {'FOUND' if found else 'MISSING'}")

    print("=" * 60)
    print("Website: http://127.0.0.1:5000")
    print("Gallery: http://127.0.0.1:5000/gallery")
    print("Admin: http://127.0.0.1:5000/admin/login")
    print("=" * 60 + "\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
