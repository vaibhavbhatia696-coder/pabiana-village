
from flask import (
    Flask, render_template_string, request, redirect,
    url_for, session, flash, abort, send_from_directory,
    Response
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pathlib import Path
from functools import wraps
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from xml.sax.saxutils import escape
import sqlite3
import secrets
import uuid
import os
import io

# ==========================================================
# PABIANA VILLAGE — PREMIUM GREEN BLUE WEBSITE
# Complete single-file Flask application
# ==========================================================

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
IMAGES = STATIC / "images"
DATA = BASE / "pabiana_data"
UPLOADS = DATA / "uploads"
DB = DATA / "website.db"

# IMPORTANT RENDER FIX:
# Never attempt to create static/images here.
# If GitHub accidentally contains a file called "images",
# the app can still start and report missing pictures.
if STATIC.exists() and not STATIC.is_dir():
    raise RuntimeError(
        "The path 'static' must be a folder, not a file."
    )

STATIC.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC))

app.secret_key = (
    os.environ.get("SECRET_KEY")
    or secrets.token_hex(32)
)

app.config.update(
    MAX_CONTENT_LENGTH=12 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1"
)

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
UPLOAD_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ==========================================================
# VILLAGE CONTENT
# ==========================================================

SECTIONS = [
    {
        "id": "mountain",
        "file": "mountain.png",
        "tag": "01 / THE HIMALAYAN HORIZON",
        "name": "Krol Tibba, Solan & Kali Tibba, Chail",
        "name_hi": "क्रोल टिब्बा सोलन और काली टिब्बा चायल",
        "title": "Where the mountains whisper.",
        "title_hi": "जहाँ पहाड़ अपनी कहानी कहते हैं।",
        "text": (
            "Where the sky embraces the mountains, every view "
            "feels like a postcard from home. Krol Tibba is a "
            "prominent mountain landmark associated with Solan, "
            "while Kali Tibba in Chail is known for its hilltop "
            "temple and panoramic Himalayan views. These landmarks "
            "reflect the scenic beauty of the surrounding region."
        ),
        "text_hi": (
            "जहाँ आसमान पहाड़ों से मिलता है, वहाँ हर नज़ारा "
            "अपने घर की खूबसूरती का एहसास कराता है। "
            "क्रोल टिब्बा सोलन क्षेत्र का एक प्रमुख पहाड़ी "
            "स्थल है, जबकि चायल का काली टिब्बा अपने "
            "पहाड़ी मंदिर और मनोरम दृश्यों के लिए प्रसिद्ध है।"
        ),
        "caption": "Closer to the clouds, closer to nature."
    },
    {
        "id": "temple",
        "file": "temple.png",
        "tag": "02 / FAITH & HERITAGE",
        "name": "Temples of Pabiana",
        "name_hi": "पबियाना के मंदिर",
        "title": "Faith rooted in the hills.",
        "title_hi": "पहाड़ों में बसी आस्था।",
        "text": (
            "The temples of Pabiana and the surrounding region "
            "reflect our faith, customs and cultural traditions. "
            "They are an important part of our village heritage."
        ),
        "text_hi": (
            "पबियाना और आसपास के मंदिर हमारी आस्था, "
            "संस्कृति और परंपराओं की पहचान हैं। "
            "ये हमारे गाँव की विरासत का महत्वपूर्ण हिस्सा हैं।"
        ),
        "caption": "A peaceful corner of our heritage."
    },
    {
        "id": "senior",
        "file": "school.png",
        "tag": "03 / EDUCATION & TOMORROW",
        "name": "Senior Secondary School Pabiana",
        "name_hi": "वरिष्ठ माध्यमिक विद्यालय पबियाना",
        "title": "Dreams grow here.",
        "title_hi": "यहाँ सपनों को नई उड़ान मिलती है।",
        "text": (
            "Senior Secondary School Pabiana is an important "
            "part of the village's educational identity, "
            "nurturing learning, confidence and ambitions "
            "for the future."
        ),
        "text_hi": (
            "वरिष्ठ माध्यमिक विद्यालय पबियाना हमारे गाँव की "
            "शैक्षिक पहचान का महत्वपूर्ण हिस्सा है, जहाँ "
            "शिक्षा के साथ आत्मविश्वास और भविष्य के सपने "
            "आकार लेते हैं।"
        ),
        "caption": "A place of learning, hope and possibility."
    },
    {
        "id": "primary",
        "file": "primary.png",
        "tag": "04 / THE FIRST STEP",
        "name": "Primary School Pabiana",
        "name_hi": "प्राथमिक विद्यालय पबियाना",
        "title": "Little steps. Bright futures.",
        "title_hi": "छोटे कदम, उज्ज्वल भविष्य।",
        "text": (
            "Every great journey begins with a small step. "
            "Primary School Pabiana is where young children "
            "take their first steps into learning, friendship "
            "and a brighter future."
        ),
        "text_hi": (
            "हर बड़ी मंज़िल की शुरुआत छोटे कदम से होती है। "
            "प्राथमिक विद्यालय पबियाना वह स्थान है जहाँ "
            "बच्चे शिक्षा और उज्ज्वल भविष्य की ओर "
            "अपना पहला कदम बढ़ाते हैं।"
        ),
        "caption": "Small beginnings, beautiful possibilities."
    },
    {
        "id": "panchayat",
        "file": "panchayal.png",
        "tag": "05 / OUR COMMUNITY",
        "name": "Gram Panchayat Ser Jagas",
        "name_hi": "ग्राम पंचायत सेर जगास",
        "title": "The heart of our village.",
        "title_hi": "हमारे गाँव की पहचान।",
        "text": (
            "Gram Panchayat Ser Jagas, Vikas Khand Rajgarh, "
            "is an important part of local administration "
            "and everyday community life in the region."
        ),
        "text_hi": (
            "ग्राम पंचायत सेर जगास, विकास खंड राजगढ़, "
            "स्थानीय प्रशासन और क्षेत्र के सामुदायिक "
            "जीवन का महत्वपूर्ण हिस्सा है।"
        ),
        "caption": "Together, we make a community."
    },
    {
        "id": "resort",
        "file": "resort.png",
        "tag": "06 / MOUNTAIN HOSPITALITY",
        "name": "Resorts & Mountain Stays",
        "name_hi": "रिज़ॉर्ट और पहाड़ी ठहराव",
        "title": "Stay close to nature.",
        "title_hi": "प्रकृति के और करीब ठहरिए।",
        "text": (
            "Surrounded by peaceful mountain scenery, "
            "the resort and stay options pictured around "
            "Pabiana offer a glimpse of the region's "
            "natural charm and beautiful landscapes."
        ),
        "text_hi": (
            "शांत पहाड़ी नज़ारों से घिरे पबियाना क्षेत्र "
            "के रिज़ॉर्ट और ठहरने के स्थान यहाँ की "
            "प्राकृतिक सुंदरता की झलक दिखाते हैं।"
        ),
        "caption": "Where mountains feel like home."
    },
    {
        "id": "road",
        "file": "road.png",
        "tag": "07 / THE ROAD THAT CONNECTS US",
        "name": "Main Road to Solan · Approx. 32 km",
        "name_hi": "सोलन मुख्य मार्ग · लगभग 32 किलोमीटर",
        "title": "Every road tells a story.",
        "title_hi": "हर रास्ते की अपनी कहानी होती है।",
        "text": (
            "The scenic main road connects the Pabiana "
            "area with Solan and surrounding regions. "
            "Solan is approximately 32 km away by this "
            "route. The road plays an important role "
            "in local travel and connectivity."
        ),
        "text_hi": (
            "यह खूबसूरत मुख्य सड़क पबियाना क्षेत्र को "
            "सोलन और आसपास के इलाकों से जोड़ती है। "
            "इस मार्ग से सोलन लगभग 32 किलोमीटर दूर है।"
        ),
        "caption": "Connecting places, people and memories."
    }
]

# ==========================================================
# DATABASE
# ==========================================================

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_photos (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM admins"
        ).fetchone()[0]

        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "")

        if count == 0 and len(password) >= 12:
            conn.execute(
                "INSERT INTO admins (username, password_hash) "
                "VALUES (?, ?)",
                (
                    username,
                    generate_password_hash(password)
                )
            )


init_db()

# ==========================================================
# PHOTO FINDER — RENDER SAFE
# ==========================================================

def find_photo(filename):
    """
    Supports:
      static/images/photo.png
      static/photo.png
      other subfolders inside static

    Never creates static/images.
    """

    if IMAGES.is_dir():
        candidate = IMAGES / filename

        if candidate.is_file():
            return url_for(
                "static",
                filename=f"images/{filename}"
            )

    candidate = STATIC / filename

    if candidate.is_file():
        return url_for(
            "static",
            filename=filename
        )

    for file in STATIC.rglob("*"):
        if not file.is_file():
            continue

        if file.name.lower() == filename.lower():
            return url_for(
                "static",
                filename=file.relative_to(STATIC).as_posix()
            )

    return None


def prepared_sections():
    result = []

    for section in SECTIONS:
        item = section.copy()
        item["url"] = find_photo(section["file"])
        result.append(item)

    return result


def all_photos():
    photos = []
    seen = set()

    for file in sorted(STATIC.rglob("*")):
        if not file.is_file():
            continue

        if file.suffix.lower() not in EXTENSIONS:
            continue

        if file.name.lower() in {
            "vaibhav.jpg",
            "vaibhav.png"
        }:
            continue

        relative = file.relative_to(STATIC).as_posix()

        if relative in seen:
            continue

        seen.add(relative)

        photos.append({
            "url": url_for("static", filename=relative),
            "title": file.stem.replace("_", " ").title(),
            "category": "Village Photography"
        })

    with get_db() as conn:
        records = conn.execute(
            "SELECT * FROM uploaded_photos "
            "ORDER BY created_at DESC"
        ).fetchall()

    for photo in records:
        if (UPLOADS / photo["filename"]).is_file():
            photos.append({
                "url": url_for(
                    "uploaded_photo",
                    filename=photo["filename"]
                ),
                "title": photo["title"],
                "category": photo["category"]
            })

    return photos


# ==========================================================
# SECURITY
# ==========================================================

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)

    return session["csrf"]


def verify_csrf():
    expected = session.get("csrf", "")
    submitted = request.form.get("csrf", "")

    if not expected or not secrets.compare_digest(
        expected, submitted
    ):
        abort(400)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        return func(*args, **kwargs)

    return wrapper


app.jinja_env.globals["csrf_token"] = csrf_token

# ==========================================================
# PREMIUM GREEN BLUE CSS
# ==========================================================

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Cormorant+Garamond:wght@500;600;700&display=swap');

:root {
    --green: #128b71;
    --green-dark: #075b50;
    --blue: #1681c5;
    --blue-dark: #124d86;
    --purple: #7855bf;
    --dark: #123c4a;
    --text: #173b48;
    --muted: #637b86;
    --gold: #e8c38c;
    --serif: 'Cormorant Garamond', Georgia, serif;
    --sans: 'Poppins', sans-serif;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    font-family: var(--sans);
    color: var(--text);
    background: #fafffd;
    overflow-x: hidden;
}

body.lock {
    overflow: hidden;
}

a {
    color: inherit;
    text-decoration: none;
}

button, input, textarea, select {
    font: inherit;
}

button {
    cursor: pointer;
}

img {
    display: block;
    max-width: 100%;
}

.container {
    width: min(1250px, calc(100% - 44px));
    margin: auto;
}

/* NAVBAR */

.navbar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 50;
    padding: 22px 0;
    color: white;
    transition: .3s;
}

.navbar.sticky {
    position: fixed;
    background: rgba(7, 54, 67, .96);
    backdrop-filter: blur(18px);
    padding: 12px 0;
    box-shadow: 0 10px 30px #0002;
}

.nav-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.brand {
    font-weight: 900;
    font-size: 24px;
    letter-spacing: 3px;
}

.brand small {
    display: block;
    font-size: 8px;
    letter-spacing: 2px;
    color: #b7f4de;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 25px;
    font-size: 11px;
    font-weight: 700;
}

.nav-links a:hover {
    color: #b3f4dc;
}

.lang-btn {
    border: 1px solid #ffffff70;
    border-radius: 30px;
    padding: 9px 15px;
    background: #ffffff22;
    color: white;
}

.menu-btn {
    display: none;
    background: #ffffff22;
    border: 1px solid #ffffff70;
    color: white;
    padding: 9px 13px;
    border-radius: 10px;
}

/* HERO */

.hero {
    position: relative;
    min-height: 720px;
    height: 100svh;
    max-height: 1050px;
    display: flex;
    align-items: center;
    overflow: hidden;
    color: white;
    background: linear-gradient(125deg, #073f49, #137e94);
}

.hero-photo {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain !important;
    object-position: center !important;
}

.hero-shade {
    position: absolute;
    inset: 0;
    background:
        linear-gradient(
            90deg,
            #063d47df,
            #075b7090 60%,
            #064d6930
        ),
        linear-gradient(
            0deg,
            #083b4599,
            transparent 70%
        );
}

.hero-content {
    position: relative;
    z-index: 2;
    padding: 130px 0 80px;
}

.eyebrow {
    color: #b5f4d9;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
}

.hero h1 {
    font-family: var(--serif);
    font-size: clamp(75px, 11vw, 155px);
    font-weight: 700;
    line-height: .9;
    margin: 30px 0;
}

.hero h1 em {
    display: block;
    color: #b5f5e2;
}

.hero p {
    max-width: 570px;
    line-height: 2;
    color: #f0fffb;
    font-size: 15px;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 35px;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 16px 27px;
    border-radius: 40px;
    font-size: 11px;
    font-weight: 800;
    transition: .3s;
    border: none;
}

.btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px #064c5b30;
}

.btn-gold {
    background: linear-gradient(
        110deg,
        #b7f2c8,
        #a9ddff
    );
    color: #124354;
}

.btn-outline {
    border: 1px solid #ffffffaa;
    color: white;
    background: #ffffff18;
}

.btn-dark {
    background: linear-gradient(
        110deg,
        #138b71,
        #177fca
    );
    color: white;
}

/* INTRO */

.intro {
    padding: 125px 0;
}

.intro-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 80px;
}

.intro-image {
    min-height: 460px;
    height: 510px;
    border-radius: 220px 220px 25px 25px;
    background: linear-gradient(
        135deg,
        #b9ecd3,
        #b2dff9
    );
    overflow: hidden;
    box-shadow: 0 30px 65px #145c7030;
}

.intro-image img {
    width: 100%;
    height: 100%;
    object-fit: contain !important;
    object-position: center !important;
}

.label {
    color: var(--green);
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: 800;
}

.title {
    font-family: var(--serif);
    font-size: clamp(52px, 6vw, 88px);
    font-weight: 600;
    line-height: 1.05;
    margin: 25px 0;
}

.title em {
    color: var(--green);
}

.copy {
    font-size: 14px;
    line-height: 2.2;
    color: var(--muted);
}

/* ZIGZAG PHOTO SECTIONS */

.places {
    padding: 60px 0 40px;
}

.places-heading {
    margin-bottom: 90px;
}

.place {
    display: grid;
    grid-template-columns: 1.08fr .92fr;
    align-items: center;
    gap: clamp(35px, 7vw, 105px);
    margin-bottom: 140px;
}

.place.reverse {
    grid-template-columns: .92fr 1.08fr;
}

.place.reverse .place-visual {
    order: 2;
}

.place-visual {
    height: 530px;
    position: relative;
    overflow: hidden;
    border-radius: 20px 130px 20px 20px;
    background: linear-gradient(
        135deg,
        #d2f4e5,
        #b9e3f8
    );
    box-shadow: 0 25px 60px #145a7426;
}

.place.reverse .place-visual {
    border-radius: 130px 20px 20px 20px;
}

/* PHOTO FULL VISIBLE — NO CROP */

.place-visual img {
    width: 100%;
    height: 100%;
    object-fit: contain !important;
    object-position: center !important;
}

.place-badge {
    position: absolute;
    left: 20px;
    bottom: 20px;
    background: #fffffff0;
    color: #087c70;
    padding: 12px 17px;
    border-radius: 9px;
    font-size: 10px;
    font-weight: 800;
}

.number {
    font-family: var(--serif);
    font-size: 100px;
    color: #b9e9d8;
    line-height: 1;
}

.place-content h3 {
    font-family: var(--serif);
    font-size: clamp(45px, 5vw, 75px);
    line-height: 1.05;
    margin: 20px 0;
}

.place-line {
    width: 100px;
    height: 3px;
    background: linear-gradient(
        90deg,
        var(--green),
        var(--blue)
    );
    margin: 27px 0;
}

.place-name {
    font-size: 13px;
    font-weight: 800;
    color: #087f83;
}

.place-content p {
    color: var(--muted);
    font-size: 14px;
    line-height: 2.2;
}

.caption-line {
    margin-top: 25px;
    padding: 16px 20px;
    border-left: 4px solid var(--blue);
    border-radius: 0 12px 12px 0;
    background: linear-gradient(
        90deg,
        #e4f8ed,
        #e5f3ff
    );
    color: #15768a;
    font-family: var(--serif);
    font-size: 24px;
    font-style: italic;
}

.placeholder {
    height: 100%;
    display: grid;
    place-items: center;
    padding: 30px;
    color: #137c79;
    text-align: center;
    font-size: 20px;
}

/* QUOTE */

.quote {
    padding: 110px 20px;
    text-align: center;
    color: white;
    background: radial-gradient(
        circle at 80% 0%,
        #168f9a,
        #093e56 65%
    );
}

.quote h2 {
    font-family: var(--serif);
    font-size: clamp(40px, 5vw, 70px);
    font-style: italic;
    max-width: 950px;
    margin: 25px auto;
}

/* GALLERY */

.gallery-section {
    padding: 120px 0;
    background: linear-gradient(
        135deg,
        #e9faef,
        #e8f5ff
    );
}

.gallery-heading {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 30px;
    margin-bottom: 50px;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.photo-card {
    position: relative;
    display: block;
    width: 100%;
    height: 265px;
    border: none;
    padding: 0;
    border-radius: 15px;
    overflow: hidden;
    background: linear-gradient(
        135deg,
        #b9ecd4,
        #b5dff6
    );
    transition: box-shadow .3s ease;
}

.photo-card img {
    width: 100%;
    height: 100%;
    object-fit: contain !important;
    object-position: center !important;
}

.photo-card:hover {
    box-shadow: 0 18px 40px #126b8730;
}

.expand {
    position: absolute;
    top: 15px;
    right: 15px;
    background: #fffffff0;
    padding: 7px 13px;
    border-radius: 50%;
    font-size: 22px;
    color: var(--green);
}

.gallery-action {
    text-align: center;
    margin-top: 45px;
}

/* FULLSCREEN PHOTO VIEWER */

.lightbox {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: #051a23f5;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 60px;
}

.lightbox.active {
    display: flex;
}

.lightbox img {
    max-width: 95vw;
    max-height: 85vh;
    width: auto;
    height: auto;
    object-fit: contain !important;
    border-radius: 8px;
}

.lightbox button {
    position: absolute;
    width: 45px;
    height: 45px;
    border: 1px solid #ffffff70;
    border-radius: 50%;
    background: #ffffff22;
    color: white;
    font-size: 25px;
}

.lightbox-close {
    top: 20px;
    right: 20px;
}

.lightbox-prev {
    left: 15px;
    top: 50%;
}

.lightbox-next {
    right: 15px;
    top: 50%;
}

.lightbox-count {
    position: absolute;
    bottom: 18px;
    color: white;
    font-size: 12px;
}

/* FOOTER */

.closing {
    padding: 110px 0;
    text-align: center;
}

.footer {
    background: #073b49;
    color: white;
    padding: 75px 0 25px;
}

.footer-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr;
    gap: 50px;
}

.footer h3 {
    letter-spacing: 3px;
    font-size: 26px;
}

.footer h4 {
    color: #a9f1d6;
    letter-spacing: 2px;
    font-size: 12px;
}

.footer p,
.footer a {
    color: #c3e5e8;
    font-size: 13px;
    line-height: 2;
}

.footer a {
    display: block;
    margin: 8px 0;
}

.footer-bottom {
    border-top: 1px solid #ffffff30;
    margin-top: 55px;
    padding-top: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    color: #c3e5e8;
    font-size: 11px;
}

.developer {
    display: flex;
    align-items: center;
    gap: 13px;
}

.developer img {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    object-fit: contain;
    border: 2px solid #a9f1d6;
}

/* ADMIN */

.admin-body {
    min-height: 100vh;
    background: linear-gradient(
        135deg,
        #075f52,
        #178c82,
        #1679bd
    );
    padding: 70px 20px;
}

.admin-box {
    max-width: 1000px;
    margin: auto;
    background: white;
    border-radius: 25px;
    padding: 35px;
}

.admin-box.small {
    max-width: 450px;
}

.admin-box h1 {
    color: #087f78;
}

.admin-box input,
.admin-box select,
.admin-box textarea {
    display: block;
    width: 100%;
    padding: 13px;
    border: 1px solid #bfe2da;
    border-radius: 10px;
    margin: 8px 0 20px;
}

.admin-box label {
    display: block;
    font-size: 13px;
    font-weight: 700;
}

.admin-box button {
    border: none;
    padding: 13px 22px;
    background: linear-gradient(
        110deg,
        #168b70,
        #1679bd
    );
    color: white;
    border-radius: 10px;
    font-weight: 700;
}

.admin-photo {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 15px 0;
    border-bottom: 1px solid #eee;
}

.admin-photo img {
    width: 100px;
    height: 85px;
    object-fit: contain;
    background: #e6f8ef;
}

.admin-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 35px;
}

.flash {
    padding: 12px;
    background: #e5f8ed;
    border-radius: 8px;
    margin: 15px 0;
}

/* LEFT RIGHT ANIMATIONS */

.reveal {
    opacity: 0;
    transform: translateY(35px);
    transition:
        opacity .9s ease,
        transform 1s cubic-bezier(.2,.75,.25,1);
}

.place:not(.reverse) .place-visual.reveal {
    transform: translateX(-85px);
}

.place.reverse .place-visual.reveal {
    transform: translateX(85px);
}

.place:not(.reverse) .place-content.reveal {
    transform: translateX(65px);
}

.place.reverse .place-content.reveal {
    transform: translateX(-65px);
}

.reveal.visible,
.place .reveal.visible {
    opacity: 1;
    transform: translate3d(0, 0, 0);
}

/* RESPONSIVE */

@media(max-width:850px) {
    .nav-links {
        display: none;
        position: absolute;
        top: 75px;
        left: 20px;
        right: 20px;
        background: #074454;
        padding: 22px;
        border-radius: 15px;
        flex-direction: column;
        align-items: flex-start;
    }

    .nav-links.open {
        display: flex;
    }

    .menu-btn {
        display: block;
    }

    .hero {
        min-height: 650px;
    }

    .hero h1 {
        font-size: 82px;
    }

    .intro-grid,
    .place,
    .place.reverse,
    .footer-grid,
    .admin-columns {
        grid-template-columns: 1fr;
    }

    .place.reverse .place-visual {
        order: 0;
    }

    .place {
        gap: 30px;
        margin-bottom: 95px;
    }

    .place-visual {
        height: 420px;
        border-radius: 20px 80px 20px 20px;
    }

    .place.reverse .place-visual {
        border-radius: 80px 20px 20px 20px;
    }

    .intro {
        padding: 90px 0;
    }

    .intro-image {
        height: 390px;
        min-height: 390px;
    }

    .gallery-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .gallery-heading {
        display: block;
    }

    .footer-bottom {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media(max-width:520px) {
    .container {
        width: calc(100% - 30px);
    }

    .hero h1 {
        font-size: 68px;
    }

    .hero p {
        font-size: 13px;
    }

    .place-visual {
        height: 310px;
    }

    .place-content h3 {
        font-size: 47px;
    }

    .gallery-grid {
        grid-template-columns: 1fr;
    }

    .photo-card {
        height: 285px;
    }

    .lightbox {
        padding: 12px;
    }

    .lightbox img {
        max-width: 96vw;
        max-height: 78vh;
    }

    .place:not(.reverse) .place-visual.reveal,
    .place.reverse .place-visual.reveal,
    .place:not(.reverse) .place-content.reveal,
    .place.reverse .place-content.reveal {
        transform: translateY(30px);
    }

    .place .reveal.visible {
        transform: translate3d(0,0,0);
    }
}

@media(prefers-reduced-motion:reduce) {
    .reveal,
    .place .reveal {
        opacity: 1;
        transform: none !important;
        transition: none;
    }
}
"""

# ==========================================================
# HTML — BASE TEMPLATE
# ==========================================================

BASE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{{ page_title }}</title>

<meta name="description"
content="Discover Pabiana Village in Sirmaur, Himachal Pradesh. Explore mountains, schools, temples, village culture and beautiful photography.">

<meta name="robots" content="index, follow">
<meta name="theme-color" content="#075f52">

<style>{{ css|safe }}</style>
</head>

<body>

<nav class="navbar" id="navbar">
<div class="container nav-inner">

<a href="/" class="brand">
PABIANA
<small>THE VILLAGE EXPERIENCE</small>
</a>

<button class="menu-btn" onclick="toggleMenu()">☰</button>

<div class="nav-links" id="navLinks">
<a href="/">HOME</a>
<a href="/#about">OUR STORY</a>
<a href="/#explore">EXPLORE</a>
<a href="/gallery">PHOTO GALLERY</a>
<a href="/#contact">CONTACT</a>

<button class="lang-btn" onclick="toggleLanguage()">
EN / हिंदी
</button>
</div>

</div>
</nav>

{% block content %}{% endblock %}

<footer class="footer" id="contact">
<div class="container">

<div class="footer-grid">

<div>
<h3>PABIANA</h3>
<p>
A digital celebration of our village,
our mountains, our culture and our beautiful home.
</p>
</div>

<div>
<h4>EXPLORE</h4>
<a href="/">Home</a>
<a href="/#explore">Village Places</a>
<a href="/gallery">Photo Gallery</a>
</div>

<div>
<h4>LOCATION</h4>
<p>
Village Pabiana<br>
District Sirmaur<br>
Himachal Pradesh, India
</p>
</div>

</div>

<div class="footer-bottom">
<span>
© {{ year }} Pabiana Village. All rights reserved.
</span>

<div class="developer">

{% if developer_photo %}
<img src="{{ developer_photo }}" alt="Developer">
{% endif %}

<div>
<small>DESIGNED & DEVELOPED BY</small>
<strong>VAIBHAV BHATIA</strong>
</div>

</div>
</div>

</div>
</footer>

<div class="lightbox" id="lightbox">

<button class="lightbox-close" onclick="closeLightbox()">×</button>
<button class="lightbox-prev" onclick="changePhoto(-1)">‹</button>

<img id="lightboxImage" alt="Full photograph">

<button class="lightbox-next" onclick="changePhoto(1)">›</button>

<div class="lightbox-count" id="lightboxCount"></div>

</div>

<script>
let currentPhoto = 0;
let photoSources = [];
let hindi = false;

function setupGallery() {
    const photos = document.querySelectorAll(".js-photo");

    photoSources = Array.from(photos).map(
        photo => photo.dataset.src
    );

    photos.forEach((photo, index) => {
        photo.addEventListener("click", () => {
            openLightbox(index);
        });
    });
}

function openLightbox(index) {
    if (!photoSources.length) return;

    currentPhoto = index;

    document.getElementById("lightbox")
        .classList.add("active");

    document.body.classList.add("lock");

    updateLightbox();
}

function updateLightbox() {
    document.getElementById("lightboxImage").src =
        photoSources[currentPhoto];

    document.getElementById("lightboxCount").textContent =
        (currentPhoto + 1) + " / " + photoSources.length;
}

function changePhoto(direction) {
    if (!photoSources.length) return;

    currentPhoto = (
        currentPhoto + direction + photoSources.length
    ) % photoSources.length;

    updateLightbox();
}

function closeLightbox() {
    document.getElementById("lightbox")
        .classList.remove("active");

    document.body.classList.remove("lock");
}

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeLightbox();
    }

    const open = document.getElementById("lightbox")
        .classList.contains("active");

    if (open && event.key === "ArrowRight") {
        changePhoto(1);
    }

    if (open && event.key === "ArrowLeft") {
        changePhoto(-1);
    }
});

function toggleMenu() {
    document.getElementById("navLinks")
        .classList.toggle("open");
}

function toggleLanguage() {
    hindi = !hindi;

    document.querySelectorAll("[data-en]").forEach(element => {
        const text = hindi
            ? element.dataset.hi
            : element.dataset.en;

        if (text) {
            element.textContent = text;
        }
    });

    document.documentElement.lang = hindi ? "hi" : "en";
}

window.addEventListener("scroll", () => {
    document.getElementById("navbar").classList.toggle(
        "sticky",
        window.scrollY > 70
    );
});

document.addEventListener("DOMContentLoaded", () => {
    setupGallery();

    if (!("IntersectionObserver" in window)) {
        document.querySelectorAll(".reveal").forEach(el => {
            el.classList.add("visible");
        });
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: .08
    });

    document.querySelectorAll(".reveal").forEach(el => {
        observer.observe(el);
    });
});
</script>

</body>
</html>
"""

# ==========================================================
# HOME PAGE HTML
# ==========================================================

HOME_HTML = r"""
{% extends "base.html" %}
{% block content %}

<section class="hero">

{% if hero %}
<img class="hero-photo"
src="{{ hero }}"
alt="Pabiana Village">
{% endif %}

<div class="hero-shade"></div>

<div class="container hero-content">

<div class="eyebrow">
WELCOME TO THE HEART OF HIMACHAL
</div>

<h1>
Pabiana
<em>Village.</em>
</h1>

<p>
A place where mountains embrace the sky,
traditions live in every home, and every road
tells a beautiful story.
</p>

<div class="actions">

<a href="#explore" class="btn btn-gold">
EXPLORE OUR VILLAGE ↗
</a>

<a href="/gallery" class="btn btn-outline">
VIEW PHOTOS ↗
</a>

</div>
</div>
</section>

<section class="intro" id="about">
<div class="container intro-grid">

<div class="intro-image reveal">

{% if intro %}
<img src="{{ intro }}" alt="Beautiful mountains">
{% endif %}

</div>

<div class="reveal">

<div class="label">
WELCOME TO OUR WORLD
</div>

<h2 class="title">
A little village.<br>
<em>A beautiful story.</em>
</h2>

<p class="copy">
Nestled among the beautiful hills of Himachal Pradesh,
Pabiana is a village surrounded by natural charm,
peaceful landscapes and a strong sense of community.
</p>

<p class="copy">
Discover the places, traditions, educational institutions
and scenic beauty that make our village special.
</p>

<a href="#explore" class="btn btn-dark">
DISCOVER MORE ↗
</a>

</div>
</div>
</section>

<section class="places" id="explore">
<div class="container">

<div class="places-heading reveal">

<div class="label">
EXPLORE OUR VILLAGE
</div>

<h2 class="title">
Places that make<br>
<em>Pabiana beautiful.</em>
</h2>

<p class="copy">
A journey through mountains, education,
faith, community and scenic roads.
</p>

</div>

{% for section in sections %}

<article class="place {% if loop.index is even %}reverse{% endif %}">

<div class="place-visual reveal">

{% if section.url %}

<img src="{{ section.url }}"
alt="{{ section.name }}"
loading="lazy">

{% else %}

<div class="placeholder">
{{ section.name }}
</div>

{% endif %}

<div class="place-badge">
{{ section.tag }}
</div>

</div>

<div class="place-content reveal">

<div class="number">
{{ "%02d"|format(loop.index) }}
</div>

<h3
data-en="{{ section.title }}"
data-hi="{{ section.title_hi }}">
{{ section.title }}
</h3>

<div class="place-line"></div>

<div class="place-name"
data-en="{{ section.name }}"
data-hi="{{ section.name_hi }}">
{{ section.name }}
</div>

<p
data-en="{{ section.text }}"
data-hi="{{ section.text_hi }}">
{{ section.text }}
</p>

<div class="caption-line">
{{ section.caption }}
</div>

<a class="btn btn-dark"
href="/gallery"
style="margin-top:25px">
EXPLORE PHOTOS ↗
</a>

</div>

</article>

{% endfor %}

</div>
</section>

<section class="quote">

<div class="label" style="color:#b8f4dc">
THE SPIRIT OF PABIANA
</div>

<h2>
"Some places are not just locations.
They are memories, emotions and home."
</h2>

</section>

<section class="gallery-section">
<div class="container">

<div class="gallery-heading reveal">

<div>
<div class="label">
OUR ORIGINAL PHOTO COLLECTION
</div>

<h2 class="title">
Every photograph<br>
<em>tells a story.</em>
</h2>
</div>

<p class="copy">
Explore the beautiful mountains, schools,
temples, village roads and unforgettable views.
</p>

</div>

<div class="gallery-grid">

{% for photo in photos[:9] %}

<button class="photo-card js-photo"
data-src="{{ photo.url }}"
aria-label="Open {{ photo.title }}">

<img src="{{ photo.url }}"
alt="{{ photo.title }}"
loading="lazy">

<span class="expand">↗</span>

</button>

{% else %}

<p>No photos uploaded yet.</p>

{% endfor %}

</div>

<div class="gallery-action">
<a href="/gallery" class="btn btn-dark">
VIEW ALL PHOTOS ↗
</a>
</div>

</div>
</section>

<section class="closing">
<div class="container">

<div class="label">
OUR HOME · OUR PRIDE
</div>

<h2 class="title">
Come for the views.<br>
<em>Stay for the memories.</em>
</h2>

<p class="copy">
Pabiana Village · Sirmaur · Himachal Pradesh
</p>

<a href="/gallery" class="btn btn-dark">
DISCOVER OUR GALLERY ↗
</a>

</div>
</section>

{% endblock %}
"""

# ==========================================================
# FULL GALLERY PAGE
# ==========================================================

GALLERY_HTML = r"""
{% extends "base.html" %}
{% block content %}

<section class="gallery-section"
style="padding-top:160px;min-height:80vh">

<div class="container">

<div class="label">
PABIANA PHOTO COLLECTION
</div>

<h1 class="title">
Our Village.<br>
<em>Our Memories.</em>
</h1>

<p class="copy">
Explore all photographs of our beautiful village.
Click any photo to view it in full size.
</p>

<div class="gallery-grid" style="margin-top:55px">

{% for photo in photos %}

<button class="photo-card js-photo"
data-src="{{ photo.url }}"
aria-label="View {{ photo.title }}">

<img src="{{ photo.url }}"
alt="{{ photo.title }}"
loading="lazy">

<span class="expand">↗</span>

</button>

{% else %}

<p>Photos will appear here when uploaded.</p>

{% endfor %}

</div>

<div style="text-align:center;margin-top:50px">

<a href="/" class="btn btn-dark">
← BACK TO HOME
</a>

</div>

</div>
</section>

{% endblock %}
"""

# ==========================================================
# ADMIN PANEL HTML
# ==========================================================

ADMIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pabiana Admin</title>
<style>{{ css|safe }}</style>
</head>

<body>

<div class="admin-body">

<div class="admin-box {% if login %}small{% endif %}">

<a href="/">← Back to Website</a>

<h1>
{% if login %}
Admin Login
{% else %}
Pabiana Photo Studio
{% endif %}
</h1>

{% for message in get_flashed_messages() %}
<div class="flash">{{ message }}</div>
{% endfor %}

{% if login %}

<form method="post">

<input type="hidden"
name="csrf"
value="{{ csrf_token() }}">

<label>
Username
<input name="username" required>
</label>

<label>
Password
<input name="password"
type="password"
required>
</label>

<button type="submit">
LOGIN ↗
</button>

</form>

{% else %}

<form method="post" action="/admin/logout">

<input type="hidden"
name="csrf"
value="{{ csrf_token() }}">

<button type="submit">LOGOUT</button>

</form>

<div class="admin-columns">

<div>

<h2>Upload New Photo</h2>

<form method="post" enctype="multipart/form-data">

<input type="hidden"
name="csrf"
value="{{ csrf_token() }}">

<label>
Choose Photo
<input type="file"
name="photo"
accept="image/png,image/jpeg,image/webp"
required>
</label>

<label>
Photo Title
<input name="title" maxlength="100" required>
</label>

<label>
Description
<textarea name="description" maxlength="400"></textarea>
</label>

<label>
Category
<select name="category">

{% for section in sections %}

<option value="{{ section.id }}">
{{ section.name }}
</option>

{% endfor %}

<option value="other">Other</option>

</select>
</label>

<button type="submit">
UPLOAD PHOTO ↗
</button>

</form>

</div>

<div>

<h2>Photo Management</h2>

<p class="copy">
Photos inside static/images appear automatically.
</p>

<p class="copy">
Required filenames:
pabiana.png, mountain.png, temple.png,
school.png, primary.png, panchayal.png,
resort.png and road.png.
</p>

<p class="copy">
Photos display fully without cropping.
</p>

</div>
</div>

<h2>Uploaded Photos</h2>

{% for photo in uploaded %}

<div class="admin-photo">

<img src="{{ url_for('uploaded_photo',filename=photo.filename) }}"
alt="{{ photo.title }}">

<div style="flex:1">
<strong>{{ photo.title }}</strong>
<p>{{ photo.category }}</p>
</div>

<form method="post"
action="{{ url_for('delete_photo',photo_id=photo.id) }}"
onsubmit="return confirm('Delete this photo?')">

<input type="hidden"
name="csrf"
value="{{ csrf_token() }}">

<button type="submit">
DELETE
</button>

</form>

</div>

{% else %}

<p>No additional photos uploaded yet.</p>

{% endfor %}

{% endif %}

</div>
</div>

</body>
</html>
"""

# ==========================================================
# PAGE RENDERER
# ==========================================================

from jinja2 import DictLoader

app.jinja_loader = DictLoader({
    "base.html": BASE_HTML,
    "home.html": HOME_HTML,
    "gallery.html": GALLERY_HTML
})


def render_page(template, **kwargs):
    return render_template_string(
        "{% extends '" + template + "' %}",
        css=CSS,
        year=datetime.now().year,
        developer_photo=(
            find_photo("vaibhav.jpg")
            or find_photo("vaibhav.png")
        ),
        **kwargs
    )

# ==========================================================
# PUBLIC ROUTES
# ==========================================================

@app.route("/")
def home():
    return render_page(
        "home.html",
        page_title=(
            "Pabiana Village | Sirmaur, Himachal Pradesh"
        ),
        hero=find_photo("pabiana.png"),
        intro=find_photo("mountain.png"),
        sections=prepared_sections(),
        photos=all_photos()
    )


@app.route("/gallery")
def gallery():
    return render_page(
        "gallery.html",
        page_title="Photo Gallery | Pabiana Village",
        photos=all_photos()
    )


@app.route("/uploads/<path:filename>")
def uploaded_photo(filename):
    return send_from_directory(UPLOADS, filename)


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        verify_csrf()

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get("password", "")

        with get_db() as conn:
            admin = conn.execute(
                "SELECT * FROM admins WHERE username=?",
                (username,)
            ).fetchone()

        if admin and check_password_hash(
            admin["password_hash"], password
        ):
            session.clear()
            session["admin"] = username

            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.")

    return render_template_string(
        ADMIN_HTML,
        css=CSS,
        login=True
    )


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():

    if request.method == "POST":
        verify_csrf()

        file = request.files.get("photo")

        title = request.form.get(
            "title", ""
        ).strip()[:100]

        description = request.form.get(
            "description", ""
        ).strip()[:400]

        category = request.form.get(
            "category", "other"
        )

        valid_categories = {
            section["id"] for section in SECTIONS
        } | {"other"}

        if category not in valid_categories:
            abort(400)

        if not file or not file.filename or not title:
            flash("Please provide a photo and title.")
            return redirect(url_for("admin_dashboard"))

        extension = Path(
            secure_filename(file.filename)
        ).suffix.lower()

        if extension not in UPLOAD_EXTENSIONS:
            flash("Only JPG, PNG and WEBP are supported.")
            return redirect(url_for("admin_dashboard"))

        raw = file.read()

        try:
            with Image.open(io.BytesIO(raw)) as image:
                image.verify()

            with Image.open(io.BytesIO(raw)) as image:
                actual_format = image.format

            expected_formats = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".webp": "WEBP"
            }

            if actual_format != expected_formats[extension]:
                raise ValueError("Image format mismatch")

        except (UnidentifiedImageError, OSError, ValueError):
            flash("Invalid image file.")
            return redirect(url_for("admin_dashboard"))

        photo_id = uuid.uuid4().hex
        filename = photo_id + extension

        (UPLOADS / filename).write_bytes(raw)

        with get_db() as conn:
            conn.execute("""
                INSERT INTO uploaded_photos
                (id, filename, title, description,
                 category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                photo_id,
                filename,
                title,
                description,
                category,
                datetime.now().isoformat()
            ))

        flash("Photo uploaded successfully!")

        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        uploaded = conn.execute(
            "SELECT * FROM uploaded_photos "
            "ORDER BY created_at DESC"
        ).fetchall()

    return render_template_string(
        ADMIN_HTML,
        css=CSS,
        login=False,
        sections=SECTIONS,
        uploaded=uploaded
    )


# ==========================================================
# DELETE PHOTO
# ==========================================================

@app.route(
    "/admin/delete/<photo_id>",
    methods=["POST"]
)
@admin_required
def delete_photo(photo_id):
    verify_csrf()

    with get_db() as conn:
        photo = conn.execute(
            "SELECT * FROM uploaded_photos WHERE id=?",
            (photo_id,)
        ).fetchone()

        if photo:
            conn.execute(
                "DELETE FROM uploaded_photos WHERE id=?",
                (photo_id,)
            )

    if photo:
        filename = Path(photo["filename"]).name
        path = UPLOADS / filename

        if path.is_file():
            path.unlink()

        flash("Photo deleted successfully.")

    return redirect(url_for("admin_dashboard"))


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    verify_csrf()
    session.clear()
    return redirect(url_for("home"))


# ==========================================================
# SEO
# ==========================================================

@app.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /admin/login\n"
    )

    return Response(
        content,
        mimetype="text/plain"
    )


@app.route("/sitemap.xml")
def sitemap():
    base_url = request.url_root.rstrip("/")

    urls = [
        base_url + "/",
        base_url + "/gallery"
    ]

    entries = "".join(
        f"<url><loc>{escape(url)}</loc></url>"
        for url in urls
    )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/'
        'schemas/sitemap/0.9">'
        + entries +
        '</urlset>'
    )

    return Response(
        xml,
        mimetype="application/xml"
    )


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
