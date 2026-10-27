
from flask import (
    Flask, render_template_string, url_for,
    request, redirect, jsonify, Response
)
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape
import os

# ============================================================
# PABIANA VILLAGE WEBSITE
# ROYAL PURPLE GLASS — OPTION 4
# UPDATED: TEMPLE + RESORT
# ALL PHOTOS DIRECTLY INSIDE STATIC
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    static_url_path="/static"
)

app.json.ensure_ascii = False

# ============================================================
# PHOTO FILENAMES
# ============================================================

PHOTO_NAMES = {
    "village": ["pabiana.png", "pabiana.jpg", "pabiana.jpeg"],
    "road": ["road.png", "road.jpg", "road.jpeg"],
    "school": ["school.png", "school.jpg", "school.jpeg"],
    "mountain": ["mountain.png", "mountain.jpg", "mountain.jpeg"],
    "primary": [
        "primary.png", "primaryschool.png",
        "primary_school.png", "primary.jpg"
    ],
    "panchayat": [
        "panchayat.png", "serjagas.png",
        "ser_jagas.png", "gram_panchayat.png"
    ],
    "temple": ["temple.png", "temple.jpg", "temple.jpeg"],
    "resort": ["resort.png", "resort.jpg", "resort.jpeg"],
    "creator": ["vaibhav.png"]
}

PHOTO_TITLES = {
    "village": "Pabiana Village",
    "road": "Main Road to Solan",
    "school": "Senior Secondary School Pabiana",
    "mountain": "Krol Tibba Solan",
    "primary": "Primary School Pabiana",
    "panchayat": "Gram Panchayat Ser Jagas",
    "temple": "Temple of Pabiana",
    "resort": "Resort & Mountain Retreat"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif"
}


def get_photo(key):
    choices = PHOTO_NAMES.get(key, [])

    for filename in choices:
        if (STATIC_DIR / filename).is_file():
            return url_for("static", filename=filename)

    available = {
        item.name.lower(): item.name
        for item in STATIC_DIR.iterdir()
        if item.is_file()
    }

    for filename in choices:
        actual = available.get(filename.lower())
        if actual:
            return url_for("static", filename=actual)

    return None


def get_gallery():
    photos = []
    used = set()

    for key, title in PHOTO_TITLES.items():
        photo = get_photo(key)

        if photo:
            photos.append({
                "src": photo,
                "title": title
            })
            used.add(photo.rsplit("/", 1)[-1].lower())

    for item in sorted(STATIC_DIR.iterdir()):
        if not item.is_file():
            continue

        if item.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        if item.name.lower() in used:
            continue

        if item.name.lower() == "vaibhav.png":
            continue

        photos.append({
            "src": url_for("static", filename=item.name),
            "title": item.stem.replace("_", " ").title()
        })

    return photos


# ============================================================
# VILLAGE CONTENT — TOTAL 8 SECTIONS
# ============================================================

SECTIONS = [
    {
        "id": "about",
        "photo": "village",
        "number": "01",
        "tag": "DISCOVER OUR VILLAGE",
        "title": "Welcome to Beautiful Pabiana",
        "hi_title": "सुंदर पबियाना गाँव में आपका स्वागत है",
        "description": (
            "Nestled among the beautiful hills of Sirmaur, "
            "Pabiana is a peaceful village in Himachal Pradesh. "
            "Its mountain landscapes, natural surroundings "
            "and village lifestyle make it a special place."
        ),
        "hi_description": (
            "हिमाचल प्रदेश के सिरमौर जिले की सुंदर "
            "पहाड़ियों में बसा पबियाना एक शांत गाँव है। "
            "यहाँ के प्राकृतिक नज़ारे और ग्रामीण जीवन "
            "इसकी खास पहचान हैं।"
        )
    },
    {
        "id": "road",
        "photo": "road",
        "number": "02",
        "tag": "SCENIC CONNECTIVITY",
        "title": "Main Road to Solan",
        "hi_title": "सोलन की ओर मुख्य सड़क",
        "description": (
            "The scenic main road towards Solan offers "
            "beautiful views of the surrounding hills. "
            "The distance to Solan is approximately 32 km."
        ),
        "hi_description": (
            "सोलन की ओर जाने वाली मुख्य सड़क आसपास की "
            "पहाड़ियों के सुंदर दृश्य दिखाती है। "
            "सोलन की दूरी लगभग 32 किलोमीटर है।"
        )
    },
    {
        "id": "school",
        "photo": "school",
        "number": "03",
        "tag": "EDUCATION & GROWTH",
        "title": "Senior Secondary School Pabiana",
        "hi_title": "वरिष्ठ माध्यमिक विद्यालय पबियाना",
        "description": (
            "Senior Secondary School Pabiana is an important "
            "educational landmark of our village, representing "
            "learning, opportunity and the future of students."
        ),
        "hi_description": (
            "वरिष्ठ माध्यमिक विद्यालय पबियाना गाँव का "
            "एक महत्वपूर्ण शैक्षणिक संस्थान है।"
        )
    },
    {
        "id": "mountain",
        "photo": "mountain",
        "number": "04",
        "tag": "MOUNTAIN BEAUTY",
        "title": "Krol Tibba Solan",
        "hi_title": "क्रोल टिब्बा सोलन",
        "description": (
            "The beautiful mountain scenery associated with "
            "Krol Tibba near Solan highlights the impressive "
            "natural landscape of this Himalayan region."
        ),
        "hi_description": (
            "सोलन के पास क्रोल टिब्बा का सुंदर "
            "पहाड़ी दृश्य इस क्षेत्र की प्राकृतिक "
            "सुंदरता को दर्शाता है।"
        )
    },
    {
        "id": "primary",
        "photo": "primary",
        "number": "05",
        "tag": "FOUNDATION OF LEARNING",
        "title": "Primary School Pabiana",
        "hi_title": "प्राथमिक विद्यालय पबियाना",
        "description": (
            "Primary School Pabiana is part of the village's "
            "educational identity and supports the early "
            "learning journey of children."
        ),
        "hi_description": (
            "प्राथमिक विद्यालय पबियाना गाँव के बच्चों "
            "की प्रारंभिक शिक्षा का महत्वपूर्ण केंद्र है।"
        )
    },
    {
        "id": "panchayat",
        "photo": "panchayat",
        "number": "06",
        "tag": "OUR LOCAL COMMUNITY",
        "title": "Gram Panchayat Ser Jagas",
        "hi_title": "ग्राम पंचायत सेर जगास",
        "description": (
            "Pabiana is associated with Gram Panchayat "
            "Ser Jagas in the Rajgarh development block "
            "of Sirmaur district, Himachal Pradesh."
        ),
        "hi_description": (
            "पबियाना गाँव हिमाचल प्रदेश के सिरमौर जिले "
            "के विकास खंड राजगढ़ की ग्राम पंचायत "
            "सेर जगास से संबंधित है।"
        )
    },
    {
        "id": "temple",
        "photo": "temple",
        "number": "07",
        "tag": "SPIRITUAL HERITAGE",
        "title": "Temple of Pabiana",
        "hi_title": "पबियाना का सुंदर मंदिर",
        "description": (
            "Explore the spiritual beauty and peaceful "
            "atmosphere of the temple in Pabiana. "
            "A place of faith, devotion and traditional "
            "Himachali culture, the temple adds a special "
            "charm to the village's identity."
        ),
        "hi_description": (
            "पबियाना का सुंदर मंदिर आस्था, भक्ति "
            "और हिमाचली संस्कृति की पहचान है। "
            "यह शांत वातावरण और आध्यात्मिक सुंदरता "
            "से जुड़ा एक विशेष स्थान है।"
        )
    },
    {
        "id": "resort",
        "photo": "resort",
        "number": "08",
        "tag": "NATURE & HOSPITALITY",
        "title": "Resort & Mountain Retreat",
        "hi_title": "रिसॉर्ट और पहाड़ी वातावरण",
        "description": (
            "Discover the resort and its beautiful "
            "mountain surroundings. The scenic setting "
            "reflects the peaceful atmosphere and "
            "natural charm of the Pabiana region, "
            "offering a wonderful glimpse of "
            "Himachal's hillside beauty."
        ),
        "hi_description": (
            "रिसॉर्ट और उसके आसपास का सुंदर "
            "पहाड़ी वातावरण इस क्षेत्र की "
            "प्राकृतिक खूबसूरती को दर्शाता है। "
            "यहाँ के मनोरम दृश्य हिमाचल की "
            "पहाड़ियों की खास पहचान हैं।"
        )
    }
]


# ============================================================
# COMPLETE HTML + CSS + JAVASCRIPT
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Pabiana Village | Sirmaur, Himachal Pradesh</title>

<meta name="description"
content="Explore Pabiana Village, Sirmaur, Himachal Pradesh. Discover mountains, schools, village roads, temples, resort scenery and Gram Panchayat Ser Jagas.">

<meta name="keywords"
content="Pabiana, Pabiana Village, Sirmaur, Rajgarh, Himachal Pradesh, Temple Pabiana, Resort Pabiana, Krol Tibba, Ser Jagas">

<meta name="robots" content="index,follow">
<meta name="theme-color" content="#7043cb">

<meta property="og:type" content="website">
<meta property="og:title" content="Pabiana Village | Himachal Pradesh">
<meta property="og:description"
content="Discover the beauty, culture and mountain landscapes of Pabiana Village.">

{% if hero %}
<meta property="og:image"
content="{{ request.url_root.rstrip('/') }}{{ hero }}">
{% endif %}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">

<style>

/* =====================================================
   ROYAL PURPLE GLASS DESIGN SYSTEM
===================================================== */

:root {
    --royal: #7142ce;
    --royal-deep: #45218b;
    --violet: #a47af0;
    --lavender: #eee4ff;
    --soft: #faf7ff;
    --pink: #f6b7e8;
    --cyan: #91e7f4;
    --ink: #30204e;
    --muted: #786c8b;
    --white: #fff;
    --shadow: 0 24px 65px rgba(91,49,158,.15);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
    scroll-padding-top: 100px;
}

body {
    font-family: "DM Sans", sans-serif;
    background: var(--soft);
    color: var(--ink);
    overflow-x: hidden;
}

body.modal-open {
    overflow: hidden;
}

a {
    text-decoration: none;
    color: inherit;
}

button {
    font: inherit;
    cursor: pointer;
}

img {
    max-width: 100%;
}

::selection {
    background: #aa85ef;
    color: white;
}

/* =====================================================
   GLASS NAVIGATION
===================================================== */

.navbar {
    position: fixed;
    z-index: 1000;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    width: min(1240px,calc(100% - 32px));
    padding: 13px 23px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    background: rgba(255,255,255,.83);
    border: 1px solid rgba(255,255,255,.95);
    border-radius: 22px;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 15px 50px rgba(50,20,101,.15);
}

.brand {
    font-family: "Manrope",sans-serif;
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #452184;
}

.brand span {
    color: #ba7aeb;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 25px;
}

.nav-links a {
    font-size: 13px;
    font-weight: 700;
    color: #604e7b;
    transition: color .3s;
}

.nav-links a:hover {
    color: var(--royal);
}

.nav-actions {
    display: flex;
    gap: 9px;
}

.lang-btn, .menu-btn {
    border: 1px solid #e3d5f9;
    background: #f1e9ff;
    color: #5d31a6;
    border-radius: 11px;
    padding: 9px 15px;
    font-size: 12px;
    font-weight: 800;
}

.menu-btn {
    display: none;
    font-size: 21px;
    padding: 5px 12px;
}

/* =====================================================
   HERO — BRIGHT PURPLE + GLASS PHOTO
===================================================== */

.hero {
    min-height: 100svh;
    position: relative;
    overflow: hidden;
    isolation: isolate;
    display: flex;
    align-items: center;
    padding: 145px max(6%,25px) 135px;
    background:
      radial-gradient(circle at 85% 25%,rgba(248,195,248,.68),transparent 37%),
      radial-gradient(circle at 12% 85%,rgba(130,93,235,.75),transparent 42%),
      linear-gradient(125deg,#4e279c,#8154dc 55%,#c18deb);
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    opacity: .22;
    background-image: radial-gradient(white 1px,transparent 1px);
    background-size: 30px 30px;
    mask-image: linear-gradient(90deg,transparent,black);
    z-index: -1;
}

.hero-inner {
    width: min(1250px,100%);
    margin: auto;
    display: grid;
    grid-template-columns: minmax(0,1fr) minmax(0,1fr);
    align-items: center;
    gap: clamp(25px,5vw,70px);
}

.hero-copy {
    color: white;
}

.hero-badge {
    display: inline-block;
    padding: 10px 16px;
    border-radius: 50px;
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.4);
    backdrop-filter: blur(15px);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero h1 {
    font-family: "Manrope",sans-serif;
    font-size: clamp(62px,9vw,130px);
    letter-spacing: -.075em;
    line-height: 1.09;
    font-weight: 800;
    margin: 25px 0 13px;
    text-shadow: 0 10px 35px rgba(39,12,83,.15);
}

.hero-subtitle {
    font-family: "Playfair Display",serif;
    color: #ffe3fc;
    font-size: clamp(22px,3vw,38px);
    line-height: 1.35;
    margin-bottom: 23px;
}

.hero-copy p {
    max-width: 540px;
    color: #f2eaff;
    font-size: 15px;
    line-height: 1.95;
}

.hero-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 13px;
    margin-top: 32px;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 15px 25px;
    border-radius: 14px;
    border: 1px solid transparent;
    font-weight: 800;
    font-size: 13px;
    transition: .3s ease;
}

.btn:hover {
    transform: translateY(-4px);
}

.btn-white {
    background: white;
    color: #5c2eb0;
    box-shadow: 0 15px 40px rgba(46,18,94,.23);
}

.btn-glass {
    background: rgba(255,255,255,.15);
    color: white;
    border-color: rgba(255,255,255,.45);
    backdrop-filter: blur(14px);
}

.btn-purple {
    background: linear-gradient(115deg,#6936ca,#a36aea);
    color: white;
    box-shadow: 0 12px 32px rgba(97,48,183,.25);
}

/* =====================================================
   FLOATING HERO PHOTO
===================================================== */

.hero-visual {
    position: relative;
    padding: 35px 16px 35px 0;
}

.hero-photo {
    padding: 12px;
    border-radius: 32px;
    background: rgba(255,255,255,.18);
    border: 1px solid rgba(255,255,255,.65);
    backdrop-filter: blur(20px);
    box-shadow: 0 35px 85px rgba(40,12,86,.31);
    animation: heroFloat 7s ease-in-out infinite;
}

.hero-photo img {
    display: block;
    width: 100%;
    height: auto;
    max-height: 490px;
    object-fit: contain;
    border-radius: 23px;
    background: #e7d8f5;
}

.hero-placeholder {
    min-height: 340px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #6238ad;
    background: #e9dbff;
    border-radius: 22px;
}

.floating-card {
    position: absolute;
    background: rgba(255,255,255,.87);
    border: 1px solid white;
    backdrop-filter: blur(20px);
    color: #462875;
    border-radius: 18px;
    padding: 14px 19px;
    box-shadow: 0 20px 50px rgba(43,15,92,.19);
    animation: cardFloat 6s ease-in-out infinite;
}

.float-top {
    top: 5px;
    right: -5px;
}

.float-bottom {
    bottom: 3px;
    left: -20px;
    animation-delay: -2s;
}

.floating-card strong {
    display: block;
    font-family: "Manrope",sans-serif;
    font-size: 15px;
}

.floating-card span {
    font-size: 11px;
    color: #827196;
}

.hero-wave {
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 100%;
    height: 115px;
    fill: var(--soft);
}

@keyframes heroFloat {
    0%,100% {transform: translateY(0) rotate(2deg)}
    50% {transform: translateY(-13px) rotate(1deg)}
}

@keyframes cardFloat {
    0%,100% {transform: translateY(0)}
    50% {transform: translateY(-11px)}
}

/* =====================================================
   INTRO
===================================================== */

.intro {
    padding: 95px 24px 45px;
    max-width: 1050px;
    margin: auto;
    text-align: center;
}

.kicker {
    color: #9562db;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 800;
}

.intro h2,
.gallery-heading h2,
.closing h2 {
    font-family: "Manrope",sans-serif;
    font-size: clamp(34px,5.5vw,65px);
    line-height: 1.2;
    letter-spacing: -.055em;
    margin: 18px 0;
}

.gradient-text {
    background: linear-gradient(110deg,#6836ca,#cb75c3);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.intro p,
.gallery-heading p {
    max-width: 680px;
    margin: auto;
    color: var(--muted);
    font-size: 15px;
    line-height: 1.95;
}

/* =====================================================
   LOCATION FACT CARDS
===================================================== */

.facts {
    max-width: 1200px;
    margin: 30px auto 110px;
    padding: 0 25px;
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 20px;
}

.fact-card {
    position: relative;
    padding: 30px;
    background: rgba(255,255,255,.82);
    border: 1px solid white;
    border-radius: 25px;
    box-shadow: var(--shadow);
    transition: .35s;
    overflow: hidden;
}

.fact-card::before {
    content: "";
    position: absolute;
    height: 4px;
    top: 0;
    left: 25px;
    right: 25px;
    border-radius: 0 0 10px 10px;
    background: linear-gradient(90deg,#8655eb,#f1a9e4,#8be2f2);
}

.fact-card:hover {
    transform: translateY(-8px);
}

.fact-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: #eee2ff;
    color: #7748c8;
    font-size: 25px;
    margin-bottom: 18px;
}

.fact-card h3 {
    font-family: "Manrope",sans-serif;
    font-size: 22px;
    color: #452776;
}

.fact-card p {
    color: #847590;
    font-size: 12px;
    margin-top: 6px;
}

/* =====================================================
   ALTERNATING STORY SECTIONS
===================================================== */

.stories {
    padding: 80px 0 65px;
    background:
      radial-gradient(circle at 95% 12%,#e8d9ff,transparent 27%),
      radial-gradient(circle at 5% 75%,#f5e3fa,transparent 30%),
      #f7f2ff;
}

.story {
    width: min(1300px,100%);
    margin: 0 auto 115px;
    padding: 0 35px;
    display: grid;
    grid-template-columns: minmax(0,1.05fr) minmax(0,1fr);
    gap: clamp(35px,6vw,95px);
    align-items: center;
}

.story:last-child {
    margin-bottom: 30px;
}

.story.reverse .story-photo {
    order: 2;
}

.story.reverse .story-content {
    order: 1;
}

.story-photo {
    position: relative;
    min-width: 0;
}

.photo-backdrop {
    position: absolute;
    inset: -17px 15px 18px -17px;
    border-radius: 34px;
    background: linear-gradient(145deg,#b39aff,#f5c9f3,#a9e5f6);
    transform: rotate(-3deg);
    opacity: .68;
}

.story.reverse .photo-backdrop {
    transform: rotate(3deg);
}

.photo-glass {
    position: relative;
    padding: 13px;
    background: rgba(255,255,255,.86);
    border: 1px solid white;
    border-radius: 29px;
    box-shadow: 0 28px 75px rgba(99,51,172,.17);
    transition: .4s;
}

.photo-glass:hover {
    transform: translateY(-7px);
    box-shadow: 0 35px 85px rgba(99,51,172,.23);
}

.photo-display {
    min-height: 220px;
    background: #f0e9fa;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.photo-display img {
    width: 100%;
    height: auto;
    max-height: 530px;
    object-fit: contain;
    display: block;
    transition: transform .55s;
}

.photo-glass:hover img {
    transform: scale(1.025);
}

.photo-caption {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    padding: 14px 8px 3px;
    color: #5b348e;
    font-size: 12px;
    font-weight: 800;
}

.photo-caption span:last-child {
    color: #aa8cc9;
}

.photo-placeholder {
    width: 100%;
    min-height: 260px;
    padding: 35px;
    background: linear-gradient(135deg,#e9dcff,#f9e9fc);
    color: #8b70b6;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    text-align: center;
    gap: 10px;
}

.story-content {
    padding: 12px 0;
}

.story-number {
    font-size: 13px;
    letter-spacing: 3px;
    font-weight: 800;
    color: #a97ad6;
}

.story-tag {
    display: inline-block;
    margin: 20px 0 17px;
    padding: 8px 13px;
    border-radius: 50px;
    border: 1px solid #dcc6fa;
    background: #e9dcff;
    color: #7946bd;
    font-size: 10px;
    letter-spacing: 1.4px;
    font-weight: 800;
}

.story-content h2 {
    font-family: "Manrope",sans-serif;
    font-size: clamp(32px,4vw,53px);
    line-height: 1.25;
    letter-spacing: -.05em;
    color: #392064;
    margin-bottom: 20px;
}

.story-content p {
    color: #716381;
    font-size: 15px;
    line-height: 2;
}

.story-line {
    width: 76px;
    height: 4px;
    border-radius: 10px;
    margin: 25px 0;
    background: linear-gradient(90deg,#804ce4,#ed9de0);
}

.story-link {
    display: inline-block;
    color: #733ac8;
    font-weight: 800;
    font-size: 13px;
    margin-top: 23px;
    transition: .3s;
}

.story-link:hover {
    color: #bd55b2;
    transform: translateX(5px);
}

/* =====================================================
   GALLERY
===================================================== */

.gallery-section {
    background: white;
    padding: 110px 24px 120px;
}

.gallery-heading {
    max-width: 1000px;
    margin: auto;
    text-align: center;
}

.gallery-grid {
    max-width: 1250px;
    margin: 50px auto 35px;
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 22px;
}

.gallery-card {
    border: 1px solid #e8dbf7;
    background: #faf7ff;
    border-radius: 23px;
    overflow: hidden;
    text-align: left;
    color: #44256f;
    box-shadow: 0 12px 35px rgba(77,40,137,.07);
    transition: .35s;
}

.gallery-card:hover {
    transform: translateY(-8px);
    border-color: #c29cf4;
    box-shadow: 0 25px 55px rgba(89,42,156,.17);
}

.gallery-image {
    height: 255px;
    padding: 12px;
    background: linear-gradient(135deg,#f4eaff,#fff5fc);
    display: flex;
    align-items: center;
    justify-content: center;
}

.gallery-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 12px;
}

.gallery-card h3 {
    font-family: "Manrope",sans-serif;
    font-size: 14px;
    padding: 18px 19px 21px;
}

.gallery-actions {
    text-align: center;
    margin-top: 35px;
}

/* =====================================================
   LIGHTBOX
===================================================== */

.lightbox {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 3000;
    background: rgba(21,9,45,.97);
    backdrop-filter: blur(20px);
    align-items: center;
    justify-content: center;
    flex-direction: column;
    padding: 70px 65px;
}

.lightbox.active {
    display: flex;
}

.lightbox img {
    max-width: 100%;
    max-height: 74vh;
    width: auto;
    height: auto;
    object-fit: contain;
    border-radius: 12px;
}

.lightbox-title {
    color: #f0e5ff;
    margin-top: 20px;
    font-weight: 800;
    text-align: center;
}

.lightbox-count {
    color: #c6b3e4;
    font-size: 12px;
    margin-top: 5px;
}

.lightbox-control {
    position: absolute;
    border: 1px solid rgba(255,255,255,.25);
    background: rgba(255,255,255,.13);
    color: white;
    width: 47px;
    height: 47px;
    border-radius: 50%;
    font-size: 25px;
}

.lightbox-close {
    top: 20px;
    right: 22px;
}

.lightbox-prev {
    left: 15px;
    top: 50%;
}

.lightbox-next {
    right: 15px;
    top: 50%;
}

/* =====================================================
   CLOSING
===================================================== */

.closing {
    position: relative;
    overflow: hidden;
    text-align: center;
    padding: 115px 25px;
    background:
      radial-gradient(circle at 15% 30%,rgba(249,177,239,.35),transparent 35%),
      radial-gradient(circle at 85% 70%,rgba(147,228,250,.23),transparent 35%),
      linear-gradient(135deg,#ede1ff,#faf3ff);
}

.closing h2 {
    color: #3e2371;
}

.closing p {
    color: #79688b;
    max-width: 650px;
    margin: 0 auto 30px;
    line-height: 1.9;
}

/* =====================================================
   FOOTER — CREATED BY VAIBHAV BHATIA
===================================================== */

footer {
    padding: 65px 24px 25px;
    background: linear-gradient(135deg,#29134f,#512895,#7641b4);
    color: white;
}

.footer-main {
    max-width: 1200px;
    margin: auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 35px;
    padding-bottom: 38px;
}

.footer-brand {
    font-family: "Manrope",sans-serif;
    font-size: 35px;
    font-weight: 800;
    letter-spacing: -1.8px;
}

.footer-brand span {
    color: #dcaaff;
}

.footer-description {
    color: #d7c8ed;
    font-size: 13px;
    margin-top: 12px;
    line-height: 1.9;
}

.creator-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 20px;
    border-radius: 22px;
    background: rgba(255,255,255,.11);
    border: 1px solid rgba(255,255,255,.25);
    backdrop-filter: blur(18px);
    box-shadow: 0 18px 45px rgba(20,7,53,.18);
    width: fit-content;
    max-width: 100%;
    justify-self: end;
    transition: .35s;
}

.creator-card:hover {
    transform: translateY(-5px);
    background: rgba(255,255,255,.17);
}

.creator-avatar {
    width: 66px;
    height: 66px;
    border-radius: 50%;
    padding: 3px;
    flex-shrink: 0;
    background: linear-gradient(135deg,#f5b3ef,#a7e8ff,#d1a8ff);
    box-shadow: 0 0 25px rgba(223,155,255,.42);
    animation: avatarGlow 4s ease-in-out infinite;
}

.creator-avatar img {
    width: 100%;
    height: 100%;
    display: block;
    border-radius: 50%;
    object-fit: cover;
    object-position: center;
    background: #bca0e9;
}

.creator-fallback {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #8055bc;
    color: white;
    font-size: 25px;
    font-weight: 800;
}

.creator-info small {
    display: block;
    font-size: 10px;
    letter-spacing: 1.8px;
    font-weight: 800;
    color: #e1c6ff;
}

.creator-info strong {
    display: block;
    font-family: "Manrope",sans-serif;
    font-size: 19px;
    margin-top: 4px;
}

.creator-info span {
    display: block;
    font-size: 11px;
    color: #e1d0f6;
    margin-top: 3px;
}

@keyframes avatarGlow {
    0%,100% {
        box-shadow: 0 0 17px rgba(223,155,255,.30);
    }
    50% {
        box-shadow: 0 0 32px rgba(223,155,255,.65);
    }
}

.footer-bottom {
    max-width: 1200px;
    margin: auto;
    border-top: 1px solid rgba(255,255,255,.22);
    padding-top: 24px;
    display: flex;
    justify-content: space-between;
    gap: 15px;
    color: #d8c9ee;
    font-size: 12px;
}

.footer-bottom a {
    color: #f0d5ff;
}

/* =====================================================
   SCROLL ANIMATIONS
===================================================== */

.reveal {
    opacity: 0;
    transform: translateY(40px);
    transition:
        opacity .85s ease,
        transform .85s cubic-bezier(.2,.8,.2,1);
}

.reveal.from-left {
    transform: translateX(-55px);
}

.reveal.from-right {
    transform: translateX(55px);
}

.reveal.visible {
    opacity: 1;
    transform: translate(0,0);
}

/* =====================================================
   RESPONSIVE
===================================================== */

@media(max-width:950px) {
    .nav-links {
        display: none;
        position: absolute;
        top: calc(100% + 10px);
        left: 0;
        right: 0;
        padding: 20px;
        background: rgba(255,255,255,.97);
        border: 1px solid white;
        border-radius: 19px;
        box-shadow: 0 18px 45px rgba(50,20,101,.17);
        flex-direction: column;
        gap: 18px;
    }

    .nav-links.open {
        display: flex;
    }

    .menu-btn {
        display: block;
    }

    .hero-inner {
        gap: 30px;
    }
}

@media(max-width:720px) {
    .navbar {
        top: 10px;
        width: calc(100% - 20px);
        padding: 11px 14px;
    }

    .brand {
        font-size: 20px;
    }

    .hero {
        padding: 135px 23px 125px;
    }

    .hero-inner {
        grid-template-columns: 1fr;
        gap: 30px;
    }

    .hero h1 {
        font-size: clamp(60px,15vw,90px);
    }

    .hero-copy p {
        font-size: 14px;
    }

    .hero-visual {
        padding: 15px 13px 25px;
    }

    .hero-photo img {
        max-height: none;
    }

    .floating-card {
        padding: 10px 12px;
    }

    .floating-card strong {
        font-size: 12px;
    }

    .floating-card span {
        font-size: 10px;
    }

    .float-bottom {
        left: 0;
    }

    .intro {
        padding: 75px 22px 30px;
    }

    .facts {
        grid-template-columns: 1fr;
        margin-bottom: 70px;
    }

    .fact-card {
        padding: 23px;
    }

    .stories {
        padding-top: 60px;
    }

    .story {
        grid-template-columns: 1fr;
        padding: 0 23px;
        gap: 25px;
        margin-bottom: 75px;
    }

    .story-photo {
        order: 1 !important;
    }

    .story-content {
        order: 2 !important;
    }

    .story-content h2 {
        font-size: 33px;
    }

    .photo-glass {
        padding: 9px;
        border-radius: 21px;
    }

    .photo-display {
        min-height: 170px;
        border-radius: 14px;
    }

    .photo-display img {
        max-height: none;
    }

    .gallery-section {
        padding: 80px 17px;
    }

    .gallery-grid {
        grid-template-columns: repeat(2,minmax(0,1fr));
        gap: 12px;
    }

    .gallery-image {
        height: 165px;
        padding: 7px;
    }

    .gallery-card h3 {
        font-size: 12px;
        padding: 12px;
    }

    .lightbox {
        padding: 65px 15px;
    }

    .lightbox-prev {
        left: 10px;
        top: auto;
        bottom: 28px;
    }

    .lightbox-next {
        right: 10px;
        top: auto;
        bottom: 28px;
    }

    .footer-main {
        grid-template-columns: 1fr;
    }

    .creator-card {
        justify-self: start;
    }

    .footer-bottom {
        flex-direction: column;
        text-align: center;
    }
}

@media(max-width:390px) {
    .hero h1 {
        font-size: 54px;
    }

    .hero-buttons {
        gap: 9px;
    }

    .btn {
        padding: 13px 17px;
        font-size: 12px;
    }

    .creator-info strong {
        font-size: 16px;
    }
}

@media(prefers-reduced-motion:reduce) {
    *,
    *::before,
    *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
        scroll-behavior: auto !important;
    }

    .reveal {
        opacity: 1;
        transform: none;
    }
}

</style>
</head>

<body>

<!-- ==================================================
     NAVBAR
================================================== -->

<nav class="navbar">

    <a class="brand" href="#home">
        PABIANA<span>.</span>
    </a>

    <div class="nav-links" id="navLinks">
        <a href="#home" data-en="Home" data-hi="होम">Home</a>
        <a href="#about" data-en="Discover" data-hi="जानें">Discover</a>
        <a href="#school" data-en="Education" data-hi="शिक्षा">Education</a>
        <a href="#temple" data-en="Temple" data-hi="मंदिर">Temple</a>
        <a href="#resort" data-en="Resort" data-hi="रिसॉर्ट">Resort</a>
        <a href="#gallery" data-en="Gallery" data-hi="गैलरी">Gallery</a>
    </div>

    <div class="nav-actions">
        <button class="lang-btn" id="langBtn"
                type="button" onclick="toggleLanguage()">
            हिंदी
        </button>

        <button class="menu-btn" type="button"
                aria-label="Toggle menu"
                aria-expanded="false"
                onclick="toggleMenu()">☰</button>
    </div>

</nav>

<!-- ==================================================
     HERO
================================================== -->

<header class="hero" id="home">

    <div class="hero-inner">

        <div class="hero-copy">

            <div class="hero-badge">
                ✦ SIRMAUR · HIMACHAL PRADESH
            </div>

            <h1>PABIANA.</h1>

            <div class="hero-subtitle"
                 data-en="A little paradise in the hills."
                 data-hi="पहाड़ों में बसा एक सुंदर स्वर्ग।">
                A little paradise in the hills.
            </div>

            <p data-en="Welcome to Pabiana, a beautiful village surrounded by the scenic hills of Himachal Pradesh. Explore its landscapes, schools, roads, temple, resort and local community."
               data-hi="हिमाचल प्रदेश की सुंदर पहाड़ियों में बसे पबियाना गाँव में आपका स्वागत है। यहाँ के प्राकृतिक नज़ारों, विद्यालयों, सड़कों, मंदिर, रिसॉर्ट और ग्रामीण जीवन को जानें।">
                Welcome to Pabiana, a beautiful village
                surrounded by the scenic hills of Himachal
                Pradesh. Explore its landscapes, schools,
                roads, temple, resort and local community.
            </p>

            <div class="hero-buttons">
                <a href="#about" class="btn btn-white"
                   data-en="Explore Pabiana ↗"
                   data-hi="पबियाना देखें ↗">
                    Explore Pabiana ↗
                </a>

                <a href="#gallery" class="btn btn-glass"
                   data-en="View All Photos"
                   data-hi="सभी तस्वीरें देखें">
                    View All Photos
                </a>
            </div>

        </div>

        <div class="hero-visual">

            <div class="hero-photo">
                {% if hero %}
                <img src="{{ hero }}"
                     alt="Beautiful Pabiana Village">
                {% else %}
                <div class="hero-placeholder">
                    Pabiana Village Photo
                </div>
                {% endif %}
            </div>

            <div class="floating-card float-top">
                <strong>✦ Pabiana</strong>
                <span>Beautiful Himachal</span>
            </div>

            <div class="floating-card float-bottom">
                <strong>⌖ Sirmaur</strong>
                <span>Himachal Pradesh · India</span>
            </div>

        </div>

    </div>

    <svg class="hero-wave" viewBox="0 0 1440 120"
         preserveAspectRatio="none"
         aria-hidden="true">
        <path d="M0,60 C230,120 460,5 720,55 C970,110 1180,10 1440,65 L1440,120 L0,120 Z"></path>
    </svg>

</header>

<!-- ==================================================
     INTRO
================================================== -->

<section class="intro reveal">

    <div class="kicker">WELCOME TO OUR WORLD</div>

    <h2>
        Discover the magic of
        <span class="gradient-text">Pabiana.</span>
    </h2>

    <p data-en="A place of peaceful mountain scenery, beautiful village roads, education, spiritual heritage and community. Explore the places that make our village special."
       data-hi="शांत पहाड़ी नज़ारों, सुंदर सड़कों, शिक्षा, आध्यात्मिक विरासत और ग्रामीण जीवन से जुड़ा हमारा पबियाना गाँव। आइए इसकी खास जगहों को जानें।">
        A place of peaceful mountain scenery,
        beautiful village roads, education, spiritual
        heritage and community. Explore the places
        that make our village special.
    </p>

</section>

<!-- ==================================================
     FACT CARDS
================================================== -->

<section class="facts">

    <div class="fact-card reveal">
        <div class="fact-icon">⌖</div>
        <h3>Sirmaur</h3>
        <p data-en="District · Himachal Pradesh"
           data-hi="जिला · हिमाचल प्रदेश">
            District · Himachal Pradesh
        </p>
    </div>

    <div class="fact-card reveal">
        <div class="fact-icon">✧</div>
        <h3>Rajgarh</h3>
        <p data-en="Development Block"
           data-hi="विकास खंड">
            Development Block
        </p>
    </div>

    <div class="fact-card reveal">
        <div class="fact-icon">❖</div>
        <h3>Ser Jagas</h3>
        <p data-en="Gram Panchayat"
           data-hi="ग्राम पंचायत">
            Gram Panchayat
        </p>
    </div>

</section>

<!-- ==================================================
     8 LEFT-RIGHT STORY SECTIONS
================================================== -->

<main class="stories">

{% for section in sections %}

<section class="story {% if loop.index is even %}reverse{% endif %}"
         id="{{ section.id }}">

    <div class="story-photo reveal {% if loop.index is even %}from-right{% else %}from-left{% endif %}">

        <div class="photo-backdrop"></div>

        <div class="photo-glass">

            <div class="photo-display">

                {% if section.image_url %}

                <img src="{{ section.image_url }}"
                     alt="{{ section.title }}"
                     loading="lazy">

                {% else %}

                <div class="photo-placeholder">
                    <div style="font-size:38px">✧</div>
                    <strong>{{ section.title }}</strong>
                    <small>Photo coming soon</small>
                </div>

                {% endif %}

            </div>

            <div class="photo-caption">
                <span>{{ section.title }}</span>
                <span>{{ section.number }} / 08</span>
            </div>

        </div>

    </div>

    <div class="story-content reveal {% if loop.index is even %}from-left{% else %}from-right{% endif %}">

        <div class="story-number">
            {{ section.number }} — PABIANA
        </div>

        <div class="story-tag">
            ✦ {{ section.tag }}
        </div>

        <h2 data-en="{{ section.title }}"
            data-hi="{{ section.hi_title }}">
            {{ section.title }}
        </h2>

        <div class="story-line"></div>

        <p data-en="{{ section.description }}"
           data-hi="{{ section.hi_description }}">
            {{ section.description }}
        </p>

        <a href="#gallery" class="story-link"
           data-en="Explore our photo gallery ↗"
           data-hi="हमारी फोटो गैलरी देखें ↗">
            Explore our photo gallery ↗
        </a>

    </div>

</section>

{% endfor %}

</main>

<!-- ==================================================
     PHOTO GALLERY
================================================== -->

<section class="gallery-section" id="gallery">

    <div class="gallery-heading reveal">

        <div class="kicker">THE PABIANA COLLECTION</div>

        <h2>
            Our village,
            <span class="gradient-text">in pictures.</span>
        </h2>

        <p data-en="Explore photographs of Pabiana Village, mountains, local schools, roads, temples, resort scenery and our community."
           data-hi="पबियाना गाँव, पहाड़ों, विद्यालयों, सड़कों, मंदिर, रिसॉर्ट और हमारी स्थानीय जगहों की तस्वीरें देखें।">
            Explore photographs of Pabiana Village,
            mountains, local schools, roads, temples,
            resort scenery and our community.
        </p>

    </div>

    <div class="gallery-grid">

        {% for photo in photos %}

        <button class="gallery-card reveal"
                type="button"
                onclick="openLightbox({{ loop.index0 }})">

            <div class="gallery-image">
                <img src="{{ photo.src }}"
                     alt="{{ photo.title }}"
                     loading="lazy">
            </div>

            <h3>{{ photo.title }}</h3>

        </button>

        {% endfor %}

    </div>

    {% if not photos %}
    <div class="gallery-actions">
        <p>Photos will appear when added to the static folder.</p>
    </div>
    {% endif %}

    <div class="gallery-actions">
        <a href="#home" class="btn btn-purple"
           data-en="Back to Top ↑"
           data-hi="ऊपर जाएँ ↑">
            Back to Top ↑
        </a>
    </div>

</section>

<!-- ==================================================
     CLOSING
================================================== -->

<section class="closing">

    <div class="kicker">OUR HOME · OUR IDENTITY</div>

    <h2>
        A beautiful place.<br>
        <span class="gradient-text">Forever Pabiana.</span>
    </h2>

    <p data-en="A village surrounded by natural beauty and a strong sense of belonging. Discover Pabiana in Sirmaur, Himachal Pradesh."
       data-hi="प्राकृतिक सुंदरता और अपनेपन से भरा हमारा गाँव पबियाना। सिरमौर, हिमाचल प्रदेश में आपका स्वागत है।">
        A village surrounded by natural beauty
        and a strong sense of belonging.
        Discover Pabiana in Sirmaur, Himachal Pradesh.
    </p>

    <a href="#gallery" class="btn btn-purple"
       data-en="Explore Gallery ↗"
       data-hi="गैलरी देखें ↗">
        Explore Gallery ↗
    </a>

</section>

<!-- ==================================================
     FOOTER — CREATED BY VAIBHAV BHATIA
================================================== -->

<footer>

    <div class="footer-main">

        <div>
            <div class="footer-brand">
                PABIANA<span>.</span>
            </div>

            <p class="footer-description">
                A beautiful village in Sirmaur,<br>
                Himachal Pradesh, India.<br>
                Gram Panchayat Ser Jagas · Rajgarh
            </p>
        </div>

        <div class="creator-card">

            <div class="creator-avatar">

                {% if creator %}
                <img src="{{ creator }}"
                     alt="Vaibhav Bhatia profile picture"
                     loading="lazy">
                {% else %}
                <div class="creator-fallback">VB</div>
                {% endif %}

            </div>

            <div class="creator-info">
                <small>CREATED BY</small>
                <strong>Vaibhav Bhatia</strong>
                <span>Website Designer & Developer</span>
            </div>

        </div>

    </div>

    <div class="footer-bottom">
        <span>© {{ year }} Pabiana Village. All Rights Reserved.</span>
        <span>Made with ♡ for Pabiana, Himachal Pradesh.</span>
    </div>

</footer>

<!-- ==================================================
     FULLSCREEN GALLERY
================================================== -->

<div class="lightbox" id="lightbox"
     role="dialog"
     aria-modal="true"
     aria-label="Photo gallery"
     aria-hidden="true">

    <button class="lightbox-control lightbox-close"
            type="button"
            aria-label="Close gallery"
            onclick="closeLightbox()">×</button>

    <button class="lightbox-control lightbox-prev"
            type="button"
            aria-label="Previous photo"
            onclick="changePhoto(-1)">‹</button>

    <img id="lightboxImage" alt="Pabiana photograph">

    <div class="lightbox-title" id="lightboxTitle"></div>
    <div class="lightbox-count" id="lightboxCount"></div>

    <button class="lightbox-control lightbox-next"
            type="button"
            aria-label="Next photo"
            onclick="changePhoto(1)">›</button>

</div>

<script>

// ==================================================
// GALLERY DATA
// ==================================================

const photos = {{ photos | tojson }};
let currentPhoto = 0;
let currentLanguage = "en";
let previousFocus = null;

// ==================================================
// LANGUAGE
// ==================================================

function toggleLanguage() {
    currentLanguage =
        currentLanguage === "en" ? "hi" : "en";

    document.documentElement.lang = currentLanguage;

    document.querySelectorAll("[data-en][data-hi]")
        .forEach(element => {
            element.textContent =
                element.dataset[currentLanguage];
        });

    document.getElementById("langBtn").textContent =
        currentLanguage === "en" ? "हिंदी" : "English";

    try {
        localStorage.setItem(
            "pabiana_language",
            currentLanguage
        );
    } catch(error) {}
}

try {
    if (localStorage.getItem("pabiana_language") === "hi") {
        toggleLanguage();
    }
} catch(error) {}

// ==================================================
// MOBILE MENU
// ==================================================

function toggleMenu() {
    const nav = document.getElementById("navLinks");
    const button = document.querySelector(".menu-btn");

    nav.classList.toggle("open");

    button.setAttribute(
        "aria-expanded",
        nav.classList.contains("open") ? "true" : "false"
    );
}

document.querySelectorAll(".nav-links a")
    .forEach(link => {
        link.addEventListener("click", () => {
            document.getElementById("navLinks")
                .classList.remove("open");

            document.querySelector(".menu-btn")
                .setAttribute("aria-expanded", "false");
        });
    });

// ==================================================
// SCROLL ANIMATIONS
// ==================================================

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.08
    });

    document.querySelectorAll(".reveal")
        .forEach(element => observer.observe(element));
} else {
    document.querySelectorAll(".reveal")
        .forEach(element => element.classList.add("visible"));
}

// ==================================================
// FULLSCREEN GALLERY
// ==================================================

function openLightbox(index) {
    if (!photos.length) return;

    previousFocus = document.activeElement;
    currentPhoto = index;

    const modal = document.getElementById("lightbox");

    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");

    document.body.classList.add("modal-open");

    showPhoto();
    document.querySelector(".lightbox-close").focus();
}

function showPhoto() {
    if (!photos.length) return;

    const photo = photos[currentPhoto];

    document.getElementById("lightboxImage").src = photo.src;
    document.getElementById("lightboxImage").alt = photo.title;
    document.getElementById("lightboxTitle").textContent =
        photo.title;

    document.getElementById("lightboxCount").textContent =
        (currentPhoto + 1) + " / " + photos.length;
}

function changePhoto(direction) {
    if (!photos.length) return;

    currentPhoto =
        (currentPhoto + direction + photos.length)
        % photos.length;

    showPhoto();
}

function closeLightbox() {
    const modal = document.getElementById("lightbox");

    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");

    document.body.classList.remove("modal-open");

    if (previousFocus) previousFocus.focus();
}

document.getElementById("lightbox")
    .addEventListener("click", event => {
        if (event.target.id === "lightbox") {
            closeLightbox();
        }
    });

document.addEventListener("keydown", event => {
    const modal = document.getElementById("lightbox");

    if (!modal.classList.contains("active")) return;

    if (event.key === "Escape") closeLightbox();
    if (event.key === "ArrowRight") changePhoto(1);
    if (event.key === "ArrowLeft") changePhoto(-1);

    if (event.key === "Tab") {
        const controls = Array.from(
            modal.querySelectorAll("button")
        );

        const first = controls[0];
        const last = controls[controls.length - 1];

        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (
            !event.shiftKey &&
            document.activeElement === last
        ) {
            event.preventDefault();
            first.focus();
        }
    }
});

</script>

</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    prepared_sections = []

    for item in SECTIONS:
        section = dict(item)
        section["image_url"] = get_photo(section["photo"])
        prepared_sections.append(section)

    return render_template_string(
        HTML,
        sections=prepared_sections,
        hero=get_photo("village"),
        creator=get_photo("creator"),
        photos=get_gallery(),
        year=datetime.now().year
    )


@app.route("/gallery")
def gallery():
    return redirect(url_for("home") + "#gallery")


@app.route("/api/photos")
def photos_api():
    return jsonify({
        "village": "Pabiana",
        "photos": get_gallery()
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "website": "Pabiana Village",
        "photos_found": len(get_gallery()),
        "sections": len(SECTIONS)
    })


@app.route("/robots.txt")
def robots():
    sitemap_url = request.url_root.rstrip("/") + "/sitemap.xml"

    return Response(
        "User-agent: *\nAllow: /\nSitemap: "
        + sitemap_url + "\n",
        mimetype="text/plain"
    )


@app.route("/sitemap.xml")
def sitemap():
    home_url = request.url_root

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>'
        + escape(home_url)
        + '</loc></url>'
        '</urlset>'
    )

    return Response(xml, mimetype="application/xml")


# ============================================================
# WINDOWS + RENDER
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
