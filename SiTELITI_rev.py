import io
from html import escape
import re
import streamlit as st
import pandas as pd
import pdfplumber


APP_CACHE_VERSION = "2026-09-15-03"


# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="SiTELITI",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 🎨 TEMA & GAYA TAMPILAN
# ============================================================

CUSTOM_CSS = """
<style>
:root {
    --siteliti-primary: #1f4e8c;
    --siteliti-primary-dark: #173c6b;
    --siteliti-teal: #147d72;
    --siteliti-amber: #b36b00;
    --siteliti-bg-soft: #f5f8fc;
    --siteliti-border: #dce5ef;
    --siteliti-text: #203047;
    --siteliti-muted: #5d6b7c;
}

/* Sisakan ruang untuk toolbar Streamlit di atas judul aplikasi. */
.block-container { padding-top: 4.5rem; padding-bottom: 2.5rem; }

/* Header: berwarna, tetapi tetap ringan dan formal. */
.siteliti-hero {
    background: linear-gradient(120deg, #eef5ff 0%, #f2fbf8 100%);
    border: 1px solid #d8e6f4;
    border-left: 5px solid var(--siteliti-primary);
    border-radius: 12px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 14px rgba(31, 78, 140, .07);
}
.siteliti-hero h1 {
    display: flex;
    align-items: center;
    gap: .7rem;
    color: var(--siteliti-primary-dark);
    font-size: 1.9rem;
    font-weight: 750;
    line-height: 1.35;
    margin: 0 0 .28rem;
    padding: .1rem 0;
    height: auto;
    white-space: normal;
    overflow-wrap: anywhere;
}
.siteliti-hero .hero-icon {
    display: inline-block;
    flex: 0 0 auto;
    margin-right: .75rem;
    font-size: 1.45rem;
    line-height: 1;
}
.siteliti-hero p {
    color: var(--siteliti-muted);
    font-size: .92rem;
    line-height: 1.6;
    margin: 0;
    white-space: normal;
    overflow-wrap: anywhere;
}

/* Ringkasan diberi aksen sesuai kategori. */
.siteliti-metric {
    position: relative;
    overflow: hidden;
    background: #ffffff;
    border: 1px solid var(--siteliti-border);
    border-radius: 10px;
    padding: .9rem 1rem .9rem 1.15rem;
    height: 100%;
    box-shadow: 0 3px 12px rgba(31, 55, 82, .055);
}
.siteliti-metric::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    background: var(--metric-color, var(--siteliti-primary));
}
.siteliti-metric .value {
    color: var(--metric-color, var(--siteliti-primary));
    font-size: 1.7rem;
    font-weight: 750;
    line-height: 1.2;
    margin: 0;
}
.siteliti-metric .label {
    color: var(--siteliti-muted);
    font-size: .85rem;
    font-weight: 550;
    margin: .3rem 0 0;
}

.siteliti-section-title {
    color: var(--siteliti-text);
    font-size: 1.1rem;
    font-weight: 700;
    margin: 1rem 0 .3rem;
}
.siteliti-section-sub {
    color: var(--siteliti-muted);
    font-size: .88rem;
    margin: 0 0 .8rem;
}

/* Sidebar dan kontrol memakai warna merek secara hemat. */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f5f8fc 0%, #ffffff 48%);
    border-right: 1px solid var(--siteliti-border);
}
section[data-testid="stSidebar"] h3 { color: var(--siteliti-primary-dark); }
.stButton button, .stDownloadButton button {
    border-radius: 7px;
    border-color: #b9cce0;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color: var(--siteliti-primary);
    color: var(--siteliti-primary);
}

/* Tab aktif terlihat jelas tanpa memenuhi layar dengan warna. */
button[data-baseweb="tab"] {
    color: var(--siteliti-muted);
    font-weight: 600;
    padding-left: 1rem;
    padding-right: 1rem;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--siteliti-primary);
    background: #edf4fc;
    border-radius: 8px 8px 0 0;
}
div[data-baseweb="tab-highlight"] { background-color: var(--siteliti-primary); }

div[data-testid="stDataFrame"] {
    border: 1px solid var(--siteliti-border);
    border-radius: 8px;
    overflow: hidden;
}
div[data-testid="stExpander"] {
    border-color: var(--siteliti-border);
    border-radius: 8px;
}

.siteliti-step-card {
    box-sizing: border-box;
    background: #ffffff;
    border: 1px solid var(--siteliti-border);
    border-top: 3px solid var(--siteliti-primary);
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
    min-height: 158px;
    box-shadow: 0 3px 12px rgba(31, 55, 82, .05);
}
.siteliti-step-card .step-num {
    display: inline-block;
    color: var(--siteliti-primary);
    background: #edf4fc;
    border-radius: 6px;
    padding: .18rem .45rem;
    font-size: .82rem;
    font-weight: 750;
    margin-bottom: .55rem;
}
.siteliti-step-card h4 {
    color: var(--siteliti-text);
    font-size: 1rem;
    margin: 0 0 .4rem;
    padding: 0;
}
.siteliti-step-card p {
    color: var(--siteliti-muted);
    font-size: .88rem;
    line-height: 1.6;
    margin: 0;
}

@media (max-width: 640px) {
    .block-container { padding-top: 4.5rem; }
    .siteliti-hero { padding: .95rem 1rem; }
    .siteliti-hero h1 { font-size: 1.6rem; }
    .siteliti-hero .hero-icon {
        font-size: 1.25rem;
    }
    .siteliti-metric { padding: .7rem .8rem .7rem 1rem; }
    .siteliti-step-card { min-height: auto; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_metric_card(value, label, color="#1f4e8c"):
    """Ringkasan sederhana; warna menekankan jumlah temuan."""
    st.markdown(
        f"""
        <div class="siteliti-metric" style="--metric-color:{escape(color)};">
            <p class="value">{escape(str(value))}</p>
            <p class="label">{escape(label)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_title(title, subtitle=None):
    """
    Menampilkan judul seksi dengan gaya konsisten,
    lengkap dengan subjudul opsional.
    """

    subtitle_html = (
        f'<p class="siteliti-section-sub">{escape(subtitle)}</p>'
        if subtitle else ""
    )

    st.markdown(
        f"""
        <p class="siteliti-section-title">{escape(title)}</p>
        {subtitle_html}
        """,
        unsafe_allow_html=True
    )


def style_status_column(df, column="Status"):
    """
    Memberi warna latar pada kolom status (Peringatan/Terdeteksi)
    agar tingkat urgensi temuan lebih mudah dikenali secara visual.
    """

    status_colors = {
        "Peringatan": "background-color:#fef3e2;color:#b5691a;font-weight:600;",
        "Terdeteksi": "background-color:#eaf7ef;color:#1f7a4d;font-weight:600;",
    }

    def _style(val):
        return status_colors.get(val, "")

    if column not in df.columns:
        return df

    styler = df.style

    style_fn = getattr(styler, "map", None) or styler.applymap

    return style_fn(_style, subset=[column])


# ============================================================
# ⚙️ BACKEND FUNCTIONS
# ============================================================


# ============================================================
# 1. MEMBERSIHKAN WATERMARK
# ============================================================

WATERMARK_TEXT_KEYWORDS = (
    "bps.go.id",
)


def is_watermark_text(
    text
):
    """
    Mengecek apakah suatu teks kemungkinan watermark BPS
    (mis. link "https://bintankab.bps.go.id" yang dicetak
    di halaman publikasi), berdasarkan isi teksnya —
    berlaku untuk domain BPS kabupaten/kota mana pun, bukan
    hanya satu daerah tertentu.
    """

    text_lower = str(
        text
    ).lower()

    return any(
        keyword in text_lower
        for keyword in WATERMARK_TEXT_KEYWORDS
    )


def strip_watermark_lines(
    text
):
    """
    Membuang baris yang mengandung watermark BPS (mis. link
    website BPS kabupaten/kota) dari teks hasil ekstraksi
    page.extract_text(), agar tidak ikut mengganggu deteksi
    nomor tabel, judul, maupun halaman indeks.
    """

    if not text:
        return text

    return "\n".join(
        line
        for line in str(text).splitlines()
        if not is_watermark_text(line)
    )


def clean_pdf_words(words):
    """
    Membersihkan hasil ekstraksi word PDF.

    Watermark diagonal biasanya memiliki:
        upright = False

    sehingga tidak digunakan dalam proses deteksi layout.

    Selain itu, watermark berupa link website BPS (mis.
    "https://bintankab.bps.go.id") kadang dicetak tegak
    (upright = True) sehingga tidak tertangkap oleh
    pengecekan di atas — kata semacam ini juga dibuang
    berdasarkan isi teksnya.
    """

    cleaned_words = []

    for word in words:

        if word.get("upright") is False:
            continue

        text = str(
            word.get("text", "")
        ).strip()

        if not text:
            continue

        if is_watermark_text(text):
            continue

        cleaned_words.append(word)

    return cleaned_words


# ============================================================
# 2. GROUP WORDS MENJADI BARIS
# ============================================================

def normalize_pdf_chars(chars):
    """Tandai superscript dari geometri, tanpa mengubah objek PDF asli.

    Karakter kecil yang terangkat dan berdekatan dengan teks utama
    diberi penanda ^. Posisi salinannya disejajarkan agar tidak menjadi
    baris terpisah. Tidak menebak superscript dari isi angka (20222).
    """
    chars = [dict(c) for c in chars if c.get("upright") is not False]
    ordered = sorted(chars, key=lambda c: c["x0"])
    active = []
    for char in ordered:
        size = float(char.get("size", char["bottom"] - char["top"]))
        if size <= 0 or not str(char.get("text", "")).strip():
            continue
        # Hanya karakter di kiri yang cukup dekat secara horizontal.
        active = [c for c in active if char["x0"] - c["x1"] <= 30]
        candidates = []
        for base in active:
            base_size = float(base.get("size", base["bottom"] - base["top"]))
            gap = char["x0"] - base["x1"]
            rise = base["bottom"] - char["bottom"]
            if (0.45 * base_size <= size <= 0.88 * base_size
                    and -0.5 <= gap <= max(2, 0.35 * base_size)
                    and 0.18 * base_size <= rise <= 0.75 * base_size
                    and char["bottom"] > base["top"]):
                candidates.append(base)
        if candidates:
            base = min(candidates, key=lambda c: abs(char["x0"] - c["x1"]))
            previous = next((c for c in reversed(active)
                             if c.get("_superscript_base") is base
                             and abs(char["x0"] - c["x1"]) <= 2), None)
            char["text"] = ("" if previous else "^") + char["text"]
            char["_superscript_base"] = base
            char["top"], char["bottom"] = base["top"], base["bottom"]
            char["doctop"] = base.get("doctop", base["top"])
        active.append(char)
    for char in chars:
        char.pop("_superscript_base", None)
    return chars


def extract_pdf_words(page):
    chars = normalize_pdf_chars(page.chars)
    return clean_pdf_words(pdfplumber.utils.extract_words(
        chars, x_tolerance=2, y_tolerance=3, keep_blank_chars=False
    ))


def extract_native_table(table, chars):
    """Gunakan sel asli untuk pemilihan karakter, lalu pulihkan superscript."""
    result = []
    for row in table.rows:
        values = []
        for cell in row.cells:
            if cell is None:
                values.append(None)
                continue
            x0, top, x1, bottom = cell
            selected = [c for c in chars
                        if x0 <= (c["x0"] + c["x1"]) / 2 < x1
                        and top <= (c["top"] + c["bottom"]) / 2 < bottom]
            words = clean_pdf_words(pdfplumber.utils.extract_words(
                normalize_pdf_chars(selected), x_tolerance=2, y_tolerance=3
            ))
            values.append("\n".join(line["text"]
                                    for line in group_words_into_lines(words)))
        result.append(values)
    return result


def group_words_into_lines(
    words,
    tolerance=3
):
    """
    Mengelompokkan word berdasarkan posisi vertikal.

    Kata-kata diurutkan dahulu berdasarkan posisi (top, x0),
    lalu dikelompokkan terhadap "top" acuan tetap (top kata
    pertama pada baris tsb) alih-alih nilai top yang terus
    diperbarui. Ini mencegah beberapa baris fisik yang
    berdekatan (mis. baris-baris data pada tabel yang padat)
    tergabung transitif menjadi satu baris raksasa, yang
    sebelumnya bisa membuat seluruh isi tabel terbaca sebagai
    judul tabel.
    """

    if not words:
        return []

    sorted_words = sorted(
        words,
        key=lambda w: (w["top"], w["x0"])
    )

    lines = []
    current_line = None

    for word in sorted_words:

        if (
            current_line is not None
            and abs(
                word["top"] - current_line["anchor_top"]
            ) <= tolerance
        ):

            current_line["words"].append(word)

            current_line["bottom"] = max(
                current_line["bottom"],
                word["bottom"]
            )

        else:

            current_line = {
                "top": word["top"],
                "anchor_top": word["top"],
                "bottom": word["bottom"],
                "words": [word]
            }

            lines.append(current_line)

    for line in lines:

        line["words"] = sorted(
            line["words"],
            key=lambda x: x["x0"]
        )

        line["top"] = min(
            w["top"] for w in line["words"]
        )

        line["text"] = " ".join(
            word["text"]
            for word in line["words"]
        ).strip()

        del line["anchor_top"]

    return lines


# ============================================================
# 3. DETEKSI HALAMAN DAFTAR TABEL
# ============================================================

def detect_index_pages(pdf):

    excluded_pages = set()

    for page_idx, page in enumerate(pdf.pages):

        text = page.extract_text() or ""

        text = strip_watermark_lines(
            text
        )

        text_lower = text.lower()

        # --------------------------------------------
        # Halaman yang memiliki heading Daftar Tabel
        # atau Daftar Lampiran
        # --------------------------------------------

        if re.search(
            r"\bdaftar\s+(tabel|lampiran)\b",
            text_lower
        ):

            excluded_pages.add(
                page_idx
            )

            # ----------------------------------------
            # Cek beberapa halaman setelahnya
            # ----------------------------------------

            for next_idx in range(
                page_idx + 1,
                min(
                    page_idx + 4,
                    len(pdf.pages)
                )
            ):

                next_text = (
                    pdf.pages[next_idx]
                    .extract_text() or ""
                )

                jumlah_tabel = len(
                    re.findall(
                        r"\b(?:Tabel|Lampiran)\s+\d+",
                        next_text,
                        re.IGNORECASE
                    )
                )

                jumlah_standalone = len(
                    re.findall(
                        r"^\s*(?:Tabel|Lampiran)\s*$",
                        next_text,
                        re.IGNORECASE |
                        re.MULTILINE
                    )
                )

                if (
                    jumlah_tabel >= 2
                    or jumlah_standalone >= 2
                ):

                    excluded_pages.add(
                        next_idx
                    )

                else:

                    break

    return excluded_pages


def detect_index_pages_from_texts(
    page_texts
):
    """
    Versi cepat detect_index_pages() jika teks halaman sudah
    tersedia dalam cache.
    """

    excluded_pages = set()

    for page_idx, text in enumerate(
        page_texts
    ):

        text = text or ""

        if re.search(
            r"\bdaftar\s+(tabel|lampiran)\b",
            text.lower()
        ):

            excluded_pages.add(
                page_idx
            )

            for next_idx in range(
                page_idx + 1,
                min(
                    page_idx + 4,
                    len(page_texts)
                )
            ):

                next_text = (
                    page_texts[
                        next_idx
                    ]
                    or ""
                )

                jumlah_tabel = len(
                    re.findall(
                        r"\b(?:Tabel|Lampiran)\s+\d+",
                        next_text,
                        re.IGNORECASE
                    )
                )

                jumlah_standalone = len(
                    re.findall(
                        r"^\s*(?:Tabel|Lampiran)\s*$",
                        next_text,
                        re.IGNORECASE |
                        re.MULTILINE
                    )
                )

                if (
                    jumlah_tabel >= 2
                    or jumlah_standalone >= 2
                ):

                    excluded_pages.add(
                        next_idx
                    )

                else:

                    break

    return excluded_pages


# ============================================================
# 4. POLA NOMOR TABEL
# ============================================================

TABLE_NUMBER_PATTERN = re.compile(
    r"^\s*\d+(?:\.\d+)*\.?\s*$"
)

TABLE_TITLE_PATTERN = re.compile(
    r"^\s*(Tabel|Table)\s+"
    r"(\d+(?:\.\d+)*)"
    r"(\.)?"
    r"(?:\s+.*)?$",
    re.IGNORECASE
)

CONTINUED_TABLE_PATTERN = re.compile(
    r"\b(?:Lanjutan\s+Tabel|Continued\s+Table)"
    r"(?:\s*/\s*(?:Lanjutan\s+Tabel|Continued\s+Table))?"
    r"\s+(\d+(?:\.\d+)*)",
    re.IGNORECASE
)

TITLE_LOWERCASE_EXCEPTIONS = {
    "dan",
    "di",
    "ke",
    "dari",
    "dalam",
    "dengan",
    "untuk",
    "yang",
    "atau",
    "pada",
    "per",
    "terhadap",
    "atas",
    "sebagai",
    "serta",
    "oleh",
    "antara",
    "antar",
    "hingga",
    "sampai",
    "sejak",
    "tanpa",
    "seperti",
    "yaitu",
    "yakni",
    "and",
    "or",
    "nor",
    "but",
    "of",
    "to",
    "in",
    "the",
    "by",
    "on",
    "for",
    "from",
    "with",
    "without",
    "into",
    "onto",
    "at",
    "as",
    "via",
    "versus",
    "mdpl",
    "mil",
    "miles",
}

TITLE_CONNECTOR_WORDS = {
    word
    for word in TITLE_LOWERCASE_EXCEPTIONS
    if word not in {
        "mdpl",
        "mil",
        "miles",
    }
}

UNIT_KEYWORDS = {
    "rp",
    "rupiah",
    "persen",
    "km",
    "km2",
    "kilometer",
    "kilometers",
    "kilometre",
    "kilometres",
    "sq",
    "square",
    "m",
    "m2",
    "m3",
    "meter",
    "meters",
    "metre",
    "metres",
    "ha",
    "kg",
    "kilogram",
    "kilograms",
    "kw",
    "kuintal",
    "quintal",
    "quintals",
    "ton",
    "tons",
    "liter",
    "liters",
    "litre",
    "litres",
    "l",
    "mdpl",
    "mbar",
    "det",
    "sec",
    "buah",
    "orang",
    "jiwa",
    "hektare",
    "hectare",
    "miliar",
    "juta",
}

# Kata "Sumber"/"Source" juga dapat menjadi header kolom.
# Hentikan pada label metadata (dengan titik dua atau berdiri sendiri),
# bukan pada frasa seperti "Sumber Penerangan Jalan Utama".
TABLE_STOP_LINE_PATTERN = re.compile(
    r"^\s*(?:"
    r"(?:Sumber|Source|Catatan|Note|Keterangan|Remarks)"
    r"(?:\s*/\s*(?:Sumber|Source|Catatan|Note|Keterangan|Remarks))?"
    r"\s*(?::|$)"
    r"|(?:Gambar|Figure|Grafik|Graph|"
    r"BAB\s+\d+|CHAPTER\s+\d+|"
    r"Produk\s+Domestik\s+Regional\s+Bruto\s+Kabupaten|"
    r"Gross\s+Regional\s+Domestic\s+Product)\b"
    r")",
    re.IGNORECASE
)


NEXT_TABLE_LINE_PATTERN = re.compile(
    r"^\s*(Tabel|Table)\s+\d+(?:\.\d+)*",
    re.IGNORECASE
)


def is_year_like_number(
    value
):
    """
    Menghindari baris seperti "Table 2025" dianggap sebagai
    nomor tabel.
    """

    return bool(
        re.fullmatch(
            r"(19|20)\d{2}",
            str(value).strip()
        )
    )


# ============================================================
# 5. DETEKSI JUDUL TABEL
# ============================================================

def detect_table_title(
    lines,
    index
):
    """
    Mendeteksi:

    FORMAT A
    Tabel 1.1

    FORMAT B
    Tabel 1.1 Judul

    FORMAT C
    Tabel
    1.1
    Table
    """

    current_line = lines[index]

    text = current_line["text"].strip()


    # ========================================================
    # FORMAT A
    # Tabel 1.1
    # ========================================================

    match = re.match(
        r"^\s*(Tabel|Table)\s+"
        r"(\d+(?:\.\d+)*)"
        r"(\.)?\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        if is_year_like_number(
            match.group(2)
        ):
            return None

        return {
            "nomor_tabel": match.group(2),
            "title_start_index": index,
            "title_end_index": index,
            "format": "satu_baris",
            "raw_title_line": text,
            "titik_setelah_nomor": bool(
                match.group(3)
            ),
            "top": current_line["top"],
            "bottom": current_line["bottom"]
        }


    # ========================================================
    # FORMAT B
    # Tabel 1.1 Judul
    # ========================================================

    match = re.match(
        r"^\s*(Tabel|Table)\s+"
        r"(\d+(?:\.\d+)*)"
        r"(\.)?\s+.+$",
        text,
        re.IGNORECASE
    )

    if match:

        if is_year_like_number(
            match.group(2)
        ):
            return None

        return {
            "nomor_tabel": match.group(2),
            "title_start_index": index,
            "title_end_index": index,
            "format": "satu_baris_dengan_judul",
            "raw_title_line": text,
            "titik_setelah_nomor": bool(
                match.group(3)
            ),
            "top": current_line["top"],
            "bottom": current_line["bottom"]
        }


    # ========================================================
    # FORMAT LANJUTAN
    # Lanjutan Tabel/Continued Table 1.1.1
    # ========================================================

    continued_match = CONTINUED_TABLE_PATTERN.search(
        text
    )

    if continued_match:

        return {
            "nomor_tabel": continued_match.group(1),
            "title_start_index": index,
            "title_end_index": index,
            "format": "lanjutan",
            "raw_title_line": text,
            "titik_setelah_nomor": False,
            "top": current_line["top"],
            "bottom": current_line["bottom"]
        }


    # ========================================================
    # FORMAT D
    #
    # Tabel Judul Indonesia
    # 1.1.3
    # Table Judul Inggris
    # ========================================================

    if (
        text.lower().startswith(
            "tabel "
        )
        and index + 1 < len(lines)
    ):

        number_line = lines[
            index + 1
        ]

        number_text = (
            number_line[
                "text"
            ].strip()
        )

        clean_number_text = re.sub(
            r"\s+[A-Za-z./:]{1,2}$",
            "",
            number_text
        ).strip()

        if (
            TABLE_NUMBER_PATTERN.match(
                clean_number_text
            )
            and not is_year_like_number(
                clean_number_text.rstrip(
                    "."
                )
            )
        ):

            table_line_index = None

            for lookahead_idx in range(
                index + 2,
                min(
                    index + 8,
                    len(lines)
                )
            ):

                table_line_text = (
                    lines[
                        lookahead_idx
                    ][
                        "text"
                    ].strip()
                )

                if table_line_text.lower().startswith(
                    "table"
                ):

                    table_line_index = (
                        lookahead_idx
                    )
                    break

                if re.search(
                    r"\(\s*1\s*\)",
                    table_line_text
                ):
                    break

            if table_line_index is None:

                table_line_index = (
                    index + 1
                )

            table_line_text = (
                lines[
                    table_line_index
                ][
                    "text"
                ].strip()
            )

            return {
                "nomor_tabel": clean_number_text.rstrip(
                    "."
                ),
                "title_start_index": index,
                "title_end_index": table_line_index,
                "format": "nomor_baris_terpisah",
                "raw_title_line": (
                    f"{text} {clean_number_text} "
                    f"{table_line_text}"
                ),
                "titik_setelah_nomor": (
                    clean_number_text.endswith(
                        "."
                    )
                ),
                "top": current_line["top"],
                "bottom": lines[
                    table_line_index
                ][
                    "bottom"
                ]
            }


    # ========================================================
    # FORMAT C
    #
    # Tabel
    # 1.1
    # Table
    # ========================================================

    if text.lower() == "tabel":

        if index + 2 >= len(lines):
            return None

        number_line = lines[index + 1]
        table_line = lines[index + 2]

        number_text = (
            number_line["text"].strip()
        )

        table_text = (
            table_line["text"].strip()
        )

        if not TABLE_NUMBER_PATTERN.match(
            number_text
        ):
            return None

        if table_text.lower() != "table":
            return None

        return {
            "nomor_tabel": number_text.rstrip("."),
            "title_start_index": index,
            "title_end_index": index + 2,
            "format": "tiga_baris",
            "raw_title_line": (
                f"{text} {number_text} {table_text}"
            ),
            "titik_setelah_nomor": (
                number_text.endswith(".")
            ),
            "top": current_line["top"],
            "bottom": table_line["bottom"]
        }


    return None


# ============================================================
# 6. MEMBANGUN JUDUL TABEL
# ============================================================

def build_table_title(
    lines,
    title_info
):
    """
    Menggabungkan nomor tabel dengan baris judul
    setelahnya.
    """

    end_index = (
        title_info["title_end_index"]
    )

    nomor_tabel = (
        title_info["nomor_tabel"]
    )

    title_parts = [
        f"Tabel {nomor_tabel}"
    ]

    if title_info.get(
        "format"
    ) == "nomor_baris_terpisah":

        for i in range(
            title_info[
                "title_start_index"
            ],
            min(
                title_info[
                    "title_end_index"
                ] + 4,
                len(lines)
            )
        ):

            text = lines[i][
                "text"
            ].strip()

            clean_number = re.sub(
                r"\s+[A-Za-z./:]{1,2}$",
                "",
                text
            ).strip()

            if not text:
                continue

            if TABLE_NUMBER_PATTERN.match(
                clean_number
            ):
                continue

            if re.search(
                r"\(\s*1\s*\)",
                text
            ):
                break

            number_count = len(
                re.findall(
                    r"\d+(?:[.,]\d+)?",
                    text
                )
            )

            word_count = len(
                lines[i][
                    "words"
                ]
            )

            if (
                i > title_info[
                    "title_end_index"
                ]
                and number_count >= 2
                and word_count >= 2
            ):
                break

            normalized = re.sub(
                r"^\s*(Tabel|Table)\s*",
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

            if normalized:

                title_parts.append(
                    normalized
                )

        return " ".join(
            title_parts
        )

    previous_bottom = (
        lines[end_index]["bottom"]
    )

    for i in range(
        end_index + 1,
        min(
            end_index + 6,
            len(lines)
        )
    ):

        line = lines[i]

        text = line["text"].strip()

        if not text:
            continue

        if re.fullmatch(
            r"[a-zA-Z./:]{1,2}",
            text
        ):
            continue

        gap = (
            line["top"]
            - previous_bottom
        )

        if gap > 35:
            break

        if re.match(
            r"^\s*(Tabel|Table)\s+\d+",
            text,
            re.IGNORECASE
        ):
            break

        if text.lower() in [
            "tabel",
            "table"
        ]:
            break

        number_count = len(
            re.findall(
                r"\d+(?:[.,]\d+)?",
                text
            )
        )

        word_count = len(
            line["words"]
        )

        if (
            number_count >= 3
            and word_count >= 3
        ):
            break

        title_parts.append(
            text
        )

        previous_bottom = (
            line["bottom"]
        )

    return " ".join(
        title_parts
    )


# ============================================================
# 7. DETEKSI BLOK ISI TABEL
# ============================================================

def find_table_body_on_page(
    lines,
    start_index
):
    """
    Mencari indikasi blok isi tabel.

    Nomor kolom TIDAK menjadi syarat.
    """

    search_start = (
        start_index + 1
    )

    search_end = len(lines)

    candidate_lines = lines[
        search_start:search_end
    ]

    if not candidate_lines:
        return None

    structural_lines = []

    for line in candidate_lines:

        text = line["text"].strip()

        if not text:
            continue

        if TABLE_STOP_LINE_PATTERN.match(
            text
        ):
            break

        # --------------------------------------------
        # Tabel berikutnya
        # --------------------------------------------

        if NEXT_TABLE_LINE_PATTERN.match(
            text
        ):
            break

        word_count = len(
            line["words"]
        )

        number_count = len(
            re.findall(
                r"\d+(?:[.,]\d+)?",
                text
            )
        )

        is_structural = False

        if word_count >= 3:
            is_structural = True

        if number_count >= 1:
            is_structural = True

        if is_structural:

            structural_lines.append(
                line
            )

    if len(structural_lines) < 3:
        return None

    body_start_line = structural_lines[0]

    for line in candidate_lines:

        text = line.get(
            "text",
            ""
        )

        if re.search(
            r"\(\s*1\s*\).{0,250}\(\s*2\s*\)",
            text,
            re.DOTALL
        ):

            column_number_index = lines.index(
                line
            )

            body_start_index = max(
                search_start,
                column_number_index - 3
            )

            body_start_line = lines[
                body_start_index
            ]

            break

    return {
        "body_top": body_start_line["top"],
        "body_bottom": structural_lines[-1]["bottom"],
        "body_start_index": lines.index(
            body_start_line
        ),
        "body_end_index": lines.index(
            structural_lines[-1]
        ),
        "structural_lines": structural_lines
    }


def find_table_end_index(
    lines,
    start_index,
    max_lines=None
):
    """
    Menentukan batas akhir area tabel agar audit tidak masuk
    ke catatan, sumber, grafik, narasi, atau tabel berikutnya.
    """

    end_index = start_index
    previous_bottom = (
        lines[start_index].get(
            "bottom",
            lines[start_index].get(
                "top",
                0
            )
        )
        if 0 <= start_index < len(lines)
        else 0
    )

    for idx in range(
        start_index,
        min(
            len(lines) if max_lines is None else start_index + max_lines,
            len(lines)
        )
    ):

        line = lines[idx]
        text = line.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        if (
            idx > start_index
            and NEXT_TABLE_LINE_PATTERN.match(
                text
            )
        ):
            break

        if TABLE_STOP_LINE_PATTERN.match(
            text
        ):
            break

        gap = (
            line.get(
                "top",
                previous_bottom
            )
            - previous_bottom
        )

        # Jarak besar juga dapat terjadi pada tabel dengan sel multi-baris.
        # Batas semantik (sumber/catatan/tabel berikutnya) lebih aman.

        end_index = idx
        previous_bottom = line.get(
            "bottom",
            previous_bottom
        )

    return end_index


def build_text_from_line_range(
    lines,
    start_index,
    end_index
):
    """
    Menggabungkan teks dari rentang baris inklusif.
    """

    if not lines:
        return ""

    start_index = max(
        0,
        start_index
    )

    end_index = min(
        end_index,
        len(lines) - 1
    )

    parts = []

    for line in lines[
        start_index:end_index + 1
    ]:

        text = line.get(
            "text",
            ""
        ).strip()

        if text:

            parts.append(
                text
            )

    return "\n".join(
        parts
    )


def truncate_before_table_header(
    text
):
    """
    Memotong teks judul sebelum area header kolom / isi tabel,
    yang ditandai salah satu dari pola berikut:

    1. Deretan tahun berurutan, mis. "2021 2022 2023 2024 2025"
    2. Penomoran kolom, mis. "(1) (2) (3)"
    3. Deretan angka data (desimal/ribuan) berurutan, mis.
       "37,33 62,67 100,00", yang menandai baris isi tabel
       SUDAH dimulai walau tabel tersebut tidak/belum memiliki
       nomor kolom maupun header tahun eksplisit.
    4. Deretan tanda strip berurutan ("-"), gaya BPS untuk
       menandai nilai kosong/nol pada baris isi tabel.

    Titik potong diambil tepat setelah kemunculan terakhir
    rentang tahun bergaya judul (mis. "2021-2025") sebelum
    tanda header/isi tersebut, karena judul BPS pada umumnya
    diakhiri dengan rentang tahun seperti itu (baik pada
    judul Indonesia maupun Inggris). Jika tidak ada rentang
    tahun semacam itu, dipotong tepat sebelum tanda tersebut.
    """

    text = str(
        text
    )

    header_signature_pattern = re.compile(
        r"(?:(?:19|20)\d{2}\*{0,2}\s+){2,}"
        r"(?:19|20)\d{2}\*{0,2}"
        r"|\(\s*1\s*\)\s*\(\s*2\s*\)\s*\(\s*3\s*\)"
        r"|(?:\d+(?:[.,]\d+)?\*{0,2}\s+){3,}"
        r"\d+(?:[.,]\d+)?\*{0,2}"
        r"|(?:[-–]\s+){2,}[-–]"
    )

    header_match = (
        header_signature_pattern.search(text)
    )

    if not header_match:
        return text

    year_range_pattern = re.compile(
        r"(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}"
    )

    last_year_range_end = None

    for match in year_range_pattern.finditer(
        text[:header_match.start()]
    ):

        last_year_range_end = match.end()

    if last_year_range_end is not None:
        return text[:last_year_range_end]

    return text[:header_match.start()]


def build_display_title_from_text(
    title_text,
    nomor_tabel
):
    """
    Membentuk judul tampilan dari area judul yang sudah
    dipotong sebelum header/body tabel.

    Sebagai pengaman, teks dipotong terlebih dahulu di titik
    mulainya header kolom tabel (lihat
    truncate_before_table_header). Sebagai lapisan tambahan,
    baris yang menyerupai baris isi tabel (banyak angka
    sekaligus banyak kata) juga dihentikan penyerapannya agar
    tidak ikut masuk ke judul.
    """

    title_text = truncate_before_table_header(
        title_text
    )

    parts = []

    for line in str(
        title_text
    ).splitlines():

        text = line.strip()

        if not text:
            continue

        clean_number = re.sub(
            r"\s+[A-Za-z./:]{1,2}$",
            "",
            text
        ).strip()

        if TABLE_NUMBER_PATTERN.match(
            clean_number
        ):
            continue

        # ----------------------------------------
        # Pengaman tambahan (fallback): hentikan hanya
        # jika baris ini sudah sangat jelas merupakan
        # baris isi tabel (bukan judul dwibahasa yang wajar
        # menyebut rentang tahun lebih dari sekali). Batas
        # dibuat tinggi karena pemotongan utama sudah
        # ditangani oleh truncate_before_table_header di atas.
        # ----------------------------------------

        number_count = len(
            re.findall(
                r"\d+(?:[.,]\d+)?",
                text
            )
        )

        word_count = len(
            re.findall(
                r"\S+",
                text
            )
        )

        if (
            number_count >= 10
            and word_count >= 20
        ):
            break

        text = re.sub(
            r"^\s*(Tabel|Table)\s*",
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

        text = re.sub(
            r"^\s*"
            + re.escape(
                str(
                    nomor_tabel
                )
            )
            + r"\.?\s*",
            "",
            text
        ).strip()

        if text:

            parts.append(
                text
            )

    if parts:

        return (
            f"Tabel {nomor_tabel} "
            + " ".join(
                parts
            )
        )

    return f"Tabel {nomor_tabel}"


def build_preview_text_from_lines(
    lines,
    start_index,
    max_lines=None
):
    """
    Preview cepat dari line cache, tanpa crop PDF ulang.
    """

    preview_parts = []

    for line in lines[
        start_index:None if max_lines is None else start_index + max_lines
    ]:

        text = line.get(
            "text",
            ""
        ).strip()

        if text:

            preview_parts.append(
                text
            )

    return "\n".join(
        preview_parts
    )


def find_raw_title_line(
    page_text,
    nomor_tabel
):
    """
    Mengambil baris judul mentah dari teks halaman untuk
    pemeriksaan titik setelah nomor tabel.
    """

    if not page_text or not nomor_tabel:
        return ""

    pattern = re.compile(
        r"\b(Tabel|Table)\s+"
        + re.escape(nomor_tabel)
        + r"\.?(?:\s+.*)?$",
        re.IGNORECASE
    )

    for line in page_text.splitlines():

        text = line.strip()

        if pattern.search(text):
            return text

    return ""


def has_dot_after_table_number(
    page_text,
    nomor_tabel
):
    """
    True jika ditemukan titik tepat setelah nomor tabel.
    """

    if not page_text or not nomor_tabel:
        return False

    pattern = re.compile(
        r"\b(Tabel|Table)\s+"
        + re.escape(nomor_tabel)
        + r"\.",
        re.IGNORECASE
    )

    return bool(
        pattern.search(page_text)
    )


# ============================================================
# ============================================================
# ENGINE 1
# NATIVE PDF TABLE DETECTION
# ============================================================
# ============================================================

def detect_tables_native(
    file_bytes
):
    """
    Engine 1.

    Menggunakan pdfplumber.extract_tables().

    Cocok untuk PDF yang struktur tabelnya masih dikenali
    sebagai tabel oleh PDF parser.
    """

    detected = []

    with pdfplumber.open(
        file_bytes
    ) as pdf:

        excluded_pages = (
            detect_index_pages(pdf)
        )

        for page_idx, page in enumerate(
            pdf.pages
        ):

            if page_idx in excluded_pages:
                continue

            try:

                tables = (
                    page.find_tables()
                )

            except Exception:

                tables = []

            for table_idx, native_table in enumerate(tables):
                raw_table = extract_native_table(native_table, page.chars)

                if not raw_table:
                    continue

                if len(raw_table) < 2:
                    continue

                # ----------------------------------------
                # Ambil teks halaman
                # ----------------------------------------

                page_text = (
                    page.extract_text()
                    or ""
                )

                page_text = (
                    strip_watermark_lines(
                        page_text
                    )
                )

                # ----------------------------------------
                # Cari nomor tabel yang muncul di halaman
                # ----------------------------------------

                table_numbers = [
                    match.group(1)
                    for match in re.finditer(
                        r"\b(?:Tabel|Table)\s+"
                        r"(\d+(?:\.\d+)*)",
                        page_text,
                        re.IGNORECASE
                    )
                    if not is_year_like_number(
                        match.group(1)
                    )
                ]

                # ----------------------------------------
                # Ambil nomor tabel berdasarkan urutan
                # ----------------------------------------

                nomor_tabel = None

                if table_idx < len(
                    table_numbers
                ):

                    nomor_tabel = (
                        table_numbers[
                            table_idx
                        ]
                    )

                detected.append({

                    "halaman": (
                        page_idx + 1
                    ),

                    "nomor_tabel": (
                        nomor_tabel
                    ),

                    "table_index": (
                        table_idx + 1
                    ),

                    "raw_table": (
                        raw_table
                    ),

                    "judul": (
                        f"Tabel {nomor_tabel}"
                        if nomor_tabel
                        else (
                            f"Tabel "
                            f"terdeteksi "
                            f"#{table_idx + 1}"
                        )
                    ),

                    "format_judul": (
                        "Native PDF Table"
                    ),

                    "sumber_detector": (
                        "Native Table Detection"
                    ),

                    "status": (
                        "Terdeteksi"
                    ),

                    "page_text": page_text,

                    "raw_title_line": (
                        find_raw_title_line(
                            page_text,
                            nomor_tabel
                        )
                    ),

                    "titik_setelah_nomor": (
                        has_dot_after_table_number(
                            page_text,
                            nomor_tabel
                        )
                    )

                })

    return detected


@st.cache_data(
    show_spinner=False
)
def detect_all_tables_cached(
    file_content,
    use_native_detection,
    cache_version
):
    """
    Cache hasil deteksi berdasarkan isi file dan mode deteksi.
    Streamlit tidak perlu mem-parsing ulang PDF saat widget berubah.
    """

    return detect_all_tables(
        io.BytesIO(
            file_content
        ),
        use_native_detection=use_native_detection
    )


# ============================================================
# ============================================================
# ENGINE 2
# TITLE / LAYOUT DETECTION
# ============================================================
# ============================================================

def detect_tables_by_title(
    file_bytes
):
    """
    Engine 2.

    Mendeteksi tabel berdasarkan:

    - Tabel 1.1
    - Tabel
      1.1
      Table

    lalu mencari blok isi tabel.

    Nomor kolom tidak diperlukan.
    """

    detected = []

    with pdfplumber.open(
        file_bytes
    ) as pdf:

        total_pages = len(
            pdf.pages
        )

        words_cache = {}
        text_cache = {}

        def get_page_lines(
            page_idx
        ):

            if page_idx not in words_cache:

                page = pdf.pages[
                    page_idx
                ]

                words = extract_pdf_words(page)

                words = clean_pdf_words(
                    words
                )

                words_cache[page_idx] = (
                    group_words_into_lines(
                        words
                    )
                    if words
                    else []
                )

            return words_cache[
                page_idx
            ]

        def get_page_text_from_lines(
            page_idx
        ):

            if page_idx not in text_cache:

                text_cache[page_idx] = "\n".join(
                    line.get(
                        "text",
                        ""
                    )
                    for line in get_page_lines(
                        page_idx
                    )
                )

            return text_cache[
                page_idx
            ]

        excluded_pages = set()

        def is_index_page_text(
            page_text
        ):

            text_lower = page_text.lower()

            if not re.search(
                r"\bdaftar\s+(tabel|lampiran)\b",
                text_lower
            ):
                return False

            jumlah_tabel = len(
                re.findall(
                    r"\b(?:Tabel|Lampiran)\s+\d+",
                    page_text,
                    re.IGNORECASE
                )
            )

            jumlah_nomor = len(
                re.findall(
                    r"^\s*\d+(?:\.\d+)+",
                    page_text,
                    re.MULTILINE
                )
            )

            return (
                jumlah_tabel >= 2
                or jumlah_nomor >= 4
            )

        for page_idx, page in enumerate(
            pdf.pages
        ):

            lines = get_page_lines(
                page_idx
            )

            if not lines:
                continue

            page_text = get_page_text_from_lines(
                page_idx
            )

            if is_index_page_text(
                page_text
            ):

                excluded_pages.add(
                    page_idx
                )
                continue

            if not re.search(
                r"\b(Tabel|Table)\b",
                page_text,
                re.IGNORECASE
            ):
                continue

            for i in range(
                len(lines)
            ):

                candidate = (
                    detect_table_title(
                        lines,
                        i
                    )
                )

                if candidate is None:
                    continue

                end_index = (
                    candidate[
                        "title_end_index"
                    ]
                )

                full_title = (
                    build_table_title(
                        lines,
                        candidate
                    )
                )

                # ----------------------------------------
                # Cari body halaman yang sama
                # ----------------------------------------

                body = (
                    find_table_body_on_page(
                        lines,
                        end_index
                    )
                )

                if body is not None:

                    body_start_index = body[
                        "body_start_index"
                    ]

                    table_end_index = (
                        find_table_end_index(
                            lines,
                            body_start_index
                        )
                    )

                    title_text = (
                        build_text_from_line_range(
                            lines,
                            candidate[
                                "title_start_index"
                            ],
                            max(
                                candidate[
                                    "title_end_index"
                                ],
                                body_start_index - 1
                            )
                        )
                    )

                    body_text = (
                        build_text_from_line_range(
                            lines,
                            body_start_index,
                            table_end_index
                        )
                    )

                    detected.append({

                        "halaman": (
                            page_idx + 1
                        ),

                        "nomor_tabel": (
                            candidate[
                                "nomor_tabel"
                            ]
                        ),

                        "judul": (
                            build_display_title_from_text(
                                title_text,
                                candidate[
                                    "nomor_tabel"
                                ]
                            )
                        ),

                        "format_judul": (
                            candidate[
                                "format"
                            ]
                        ),

                        "sumber_detector": (
                            "Title/Layout Detection"
                        ),

                        "status": (
                            "Terdeteksi"
                        ),

                        "page_text": (
                            get_page_text_from_lines(
                                page_idx
                            )
                        ),

                        "raw_title_line": (
                            candidate.get(
                                "raw_title_line",
                                ""
                            )
                        ),

                        "titik_setelah_nomor": (
                            candidate.get(
                                "titik_setelah_nomor",
                                False
                            )
                        ),

                        "preview_text": (
                            "\n".join(
                                part
                                for part in [
                                    title_text,
                                    body_text
                                ]
                                if part
                            )
                        ),

                        "title_text": (
                            title_text
                        ),

                        "body_text": (
                            body_text
                        ),

                        "bbox": (
                            0,
                            candidate["top"],
                            page.width,
                            page.height - 30
                        )

                    })

                    continue

                # ----------------------------------------
                # Jika isi ada di halaman berikutnya
                # ----------------------------------------

                if (
                    page_idx + 1
                    < total_pages
                ):

                    next_lines = get_page_lines(
                        page_idx + 1
                    )

                    if next_lines:

                        next_body = (
                            find_table_body_on_page(
                                next_lines,
                                -1
                            )
                        )

                        if next_body is not None:

                            next_body_start_index = (
                                next_body[
                                    "body_start_index"
                                ]
                            )

                            next_table_end_index = (
                                find_table_end_index(
                                    next_lines,
                                    next_body_start_index
                                )
                            )

                            title_text = (
                                build_text_from_line_range(
                                    lines,
                                    candidate[
                                        "title_start_index"
                                    ],
                                    len(lines) - 1
                                )
                            )

                            body_text = (
                                build_text_from_line_range(
                                    next_lines,
                                    next_body_start_index,
                                    next_table_end_index
                                )
                            )

                            detected.append({

                                "halaman": (
                                    page_idx + 1
                                ),

                                "nomor_tabel": (
                                    candidate[
                                        "nomor_tabel"
                                    ]
                                ),

                                "judul": (
                                    build_display_title_from_text(
                                        title_text,
                                        candidate[
                                            "nomor_tabel"
                                        ]
                                    )
                                ),

                                "format_judul": (
                                    candidate[
                                        "format"
                                    ]
                                ),

                                "sumber_detector": (
                                    "Title/Layout Detection"
                                ),

                                "status": (
                                    "Terdeteksi "
                                    "(isi halaman berikutnya)"
                                ),

                                "page_text": (
                                    get_page_text_from_lines(
                                        page_idx
                                    )
                                ),

                                "raw_title_line": (
                                    candidate.get(
                                        "raw_title_line",
                                        ""
                                    )
                                ),

                                "titik_setelah_nomor": (
                                    candidate.get(
                                        "titik_setelah_nomor",
                                        False
                                    )
                                ),

                                "preview_text": (
                                    "\n".join(
                                        part
                                        for part in [
                                            title_text,
                                            body_text
                                        ]
                                        if part
                                    )
                                ),

                                "title_text": (
                                    title_text
                                ),

                                "body_text": (
                                    body_text
                                ),

                                "bbox": (
                                    0,
                                    candidate["top"],
                                    page.width,
                                    page.height - 30
                                )

                            })

    return (
        detected,
        excluded_pages,
        total_pages
    )


# ============================================================
# ============================================================
# GABUNGKAN DUA ENGINE
# ============================================================
# ============================================================

def merge_table_detection_results(
    native_tables,
    layout_tables
):
    """
    Menggabungkan hasil Engine 1 dan Engine 2.

    Prioritas:

    - Kalau kedua engine menemukan tabel yang sama,
      hanya satu yang ditampilkan.
    - Kalau hanya salah satu engine yang menemukan,
      tetap dipertahankan.

    Pencocokan utama menggunakan:
        halaman + nomor tabel
    """

    merged = []

    # --------------------------------------------------------
    # Engine 1
    # --------------------------------------------------------

    for item in native_tables:

        merged.append(
            item.copy()
        )


    # --------------------------------------------------------
    # Engine 2
    # --------------------------------------------------------

    for item in layout_tables:

        duplicate_idx = None

        for idx, existing in enumerate(
            merged
        ):

            same_page = (
                existing.get("halaman")
                == item.get("halaman")
            )

            same_number = (
                existing.get("nomor_tabel")
                is not None
                and item.get("nomor_tabel")
                is not None
                and existing.get(
                    "nomor_tabel"
                )
                == item.get(
                    "nomor_tabel"
                )
            )

            if same_page and same_number:

                duplicate_idx = idx
                break


        # ----------------------------------------------------
        # Jika duplicate
        # ----------------------------------------------------

        if duplicate_idx is not None:

            existing = merged[
                duplicate_idx
            ]

            existing[
                "sumber_detector"
            ] = (
                "Native + Title/Layout Detection"
            )

            # Jika layout memiliki judul yang lebih lengkap
            if len(
                item.get("judul", "")
            ) > len(
                existing.get("judul", "")
            ):

                existing["judul"] = (
                    item["judul"]
                )

            # Simpan bbox jika ada
            if item.get("bbox"):

                existing["bbox"] = (
                    item["bbox"]
                )

            for key in [
                "page_text",
                "raw_title_line",
                "titik_setelah_nomor",
                "preview_text",
                "title_text",
                "body_text"
            ]:

                if item.get(key):

                    existing[key] = item[key]

            # Simpan format judul
            if item.get(
                "format_judul"
            ):

                existing[
                    "format_judul"
                ] = item[
                    "format_judul"
                ]

        else:

            merged.append(
                item.copy()
            )


    # --------------------------------------------------------
    # Bersihkan false positive native tanpa nomor tabel
    # --------------------------------------------------------

    merged = [
        item
        for item in merged
        if not (
            item.get("nomor_tabel") is None
            and item.get("sumber_detector")
            == "Native Table Detection"
        )
    ]


    # --------------------------------------------------------
    # Deduplikasi lintas halaman berdasarkan nomor tabel.
    # Tabel yang bersambung ke halaman berikutnya tidak
    # dihitung sebagai tabel baru.
    # --------------------------------------------------------

    deduped_by_number = {}
    unnumbered_items = []

    for item in merged:

        nomor = item.get(
            "nomor_tabel"
        )

        if nomor is None:

            unnumbered_items.append(
                item
            )

            continue

        existing = deduped_by_number.get(
            nomor
        )

        if existing is None:

            deduped_by_number[
                nomor
            ] = item

            continue

        # ------------------------------------------------
        # Tabel lanjutan (kolom bersambung ke halaman
        # berikutnya, ditandai "Lanjutan Tabel/Continued
        # Table X.X"): jangan dianggap tabel baru dan
        # jangan sampai menimpa judul asli dengan teks
        # penanda lanjutan. Isi kolom lanjutannya tetap
        # digabungkan ke tabel asli agar ikut diperiksa
        # pada audit format.
        # ------------------------------------------------

        item_is_continued = (
            item.get("format_judul")
            == "lanjutan"
        )

        if item_is_continued:

            existing_body = (
                existing.get("body_text")
                or ""
            )

            item_body = (
                item.get("body_text")
                or ""
            )

            if item_body:

                existing["body_text"] = (
                    (
                        existing_body
                        + "\n"
                        + item_body
                    )
                    if existing_body
                    else item_body
                )

            existing["preview_text"] = "\n".join(
                part for part in (existing.get("title_text", ""),
                                  existing.get("body_text", "")) if part
            )
            if existing.get("raw_table") and item.get("raw_table"):
                if len(existing["raw_table"][0]) == len(item["raw_table"][0]):
                    existing["raw_table"] = existing["raw_table"] + item["raw_table"]

            halaman_lanjutan = (
                existing.setdefault(
                    "halaman_lanjutan",
                    []
                )
            )

            if (
                item.get("halaman")
                not in halaman_lanjutan
            ):

                halaman_lanjutan.append(
                    item.get("halaman")
                )

            existing[
                "status"
            ] = "Terdeteksi"

            continue

        existing_is_layout = (
            "Title/Layout" in existing.get(
                "sumber_detector",
                ""
            )
        )

        item_is_layout = (
            "Title/Layout" in item.get(
                "sumber_detector",
                ""
            )
        )

        if (
            item_is_layout
            and not existing_is_layout
        ):

            deduped_by_number[
                nomor
            ] = item

        elif len(
            item.get("judul", "")
        ) > len(
            existing.get("judul", "")
        ):

            existing["judul"] = (
                item["judul"]
            )

        existing[
            "status"
        ] = "Terdeteksi"

    merged = (
        unnumbered_items
        + list(
            deduped_by_number.values()
        )
    )


    # --------------------------------------------------------
    # Urutkan halaman lalu nomor tabel
    # --------------------------------------------------------

    def sort_key(item):

        halaman = item.get(
            "halaman",
            0
        )

        nomor = item.get(
            "nomor_tabel"
        )

        if nomor is None:

            return (
                halaman,
                999,
                999,
                999
            )

        try:

            nomor_parts = [
                int(x)
                for x in nomor.split(".")
            ]

            return (
                halaman,
                *nomor_parts
            )

        except Exception:

            return (
                halaman,
                999,
                999,
                999
            )


    merged.sort(
        key=sort_key
    )

    return merged


# ============================================================
# MASTER TABLE DETECTOR
# ============================================================

def detect_all_tables(
    file_bytes,
    use_native_detection=False
):

    # ========================================================
    # ENGINE 1
    # ========================================================

    if use_native_detection:

        native_tables = (
            detect_tables_native(
                file_bytes
            )
        )

        file_bytes.seek(
            0
        )

    else:

        native_tables = []


    # ========================================================
    # ENGINE 2
    # ========================================================

    (
        layout_tables,
        excluded_pages,
        total_pages
    ) = (
        detect_tables_by_title(
            file_bytes
        )
    )


    # ========================================================
    # GABUNGKAN
    # ========================================================

    merged_tables = (
        merge_table_detection_results(
            native_tables,
            layout_tables
        )
    )


    return (
        merged_tables,
        native_tables,
        layout_tables,
        total_pages,
        excluded_pages
    )


# ============================================================
# ============================================================
# AUDIT FORMAT TABEL
# ============================================================
# ============================================================

def audit_table_format(
    extracted_data
):
    """
    Rule-based audit awal.

    CATATAN:
    Ini masih rule dasar.
    Nanti dapat kita tambah dengan rule format BPS.
    """

    log_errors = []

    error_cell_map = {}


    for item in extracted_data:

        hal = item["halaman"]

        t_idx = item[
            "tabel_ke"
        ]

        df = item[
            "dataframe"
        ]

        table_key = (
            hal,
            t_idx
        )

        error_cell_map[
            table_key
        ] = set()


        for row_idx, row in df.iterrows():

            for col_name in df.columns:

                val = (
                    str(
                        row[col_name]
                    ).strip()
                    if row[col_name]
                    is not None
                    else ""
                )


                # ==================================================
                # RULE 1
                # ==================================================

                if (
                    val == ""
                    or val.lower()
                    in [
                        "none",
                        "nan"
                    ]
                ):

                    log_errors.append({

                        "Halaman": hal,

                        "Tabel Ke": t_idx,

                        "Lokasi": (
                            f"Baris {row_idx + 1}, "
                            f"Kolom '{col_name}'"
                        ),

                        "Jenis Isu": (
                            "Sel Kosong "
                            "(Missing Value)"
                        ),

                        "Nilai Terbaca": "-",

                        "Status": "Peringatan"

                    })

                    error_cell_map[
                        table_key
                    ].add(
                        (
                            row_idx,
                            col_name
                        )
                    )


                # ==================================================
                # RULE 2
                # ==================================================

                elif val in [
                    "---",
                    "--",
                    "?",
                    "n/a",
                    "N/A"
                ]:

                    log_errors.append({

                        "Halaman": hal,

                        "Tabel Ke": t_idx,

                        "Lokasi": (
                            f"Baris {row_idx + 1}, "
                            f"Kolom '{col_name}'"
                        ),

                        "Jenis Isu": (
                            "Simbol Notasi "
                            "Tidak Standar"
                        ),

                        "Nilai Terbaca": val,

                        "Status": "Peringatan"

                    })

                    error_cell_map[
                        table_key
                    ].add(
                        (
                            row_idx,
                            col_name
                        )
                    )


        # ======================================================
        # RULE HEADER KOSONG
        # ======================================================

        for col_name in df.columns:

            if "Kolom_" in str(
                col_name
            ):

                log_errors.append({

                    "Halaman": hal,

                    "Tabel Ke": t_idx,

                    "Lokasi": (
                        f"Header Kolom "
                        f"'{col_name}'"
                    ),

                    "Jenis Isu": (
                        "Header Kolom "
                        "Kosong/Tidak Bernama"
                    ),

                    "Nilai Terbaca": "-",

                    "Status": "Peringatan"

                })


    df_log = pd.DataFrame(
        log_errors
    )

    return (
        df_log,
        error_cell_map
    )


def add_audit_warning(
    log_errors,
    halaman,
    tabel_ke,
    lokasi,
    jenis_isu,
    nilai_terbaca,
    aturan,
    konteks_baris=""
):
    """
    Menambahkan temuan sebagai warning. Sistem hanya
    memberi peringatan, perbaikan dilakukan manual.
    """

    log_errors.append({

        "Halaman": halaman,

        "Tabel Ke": tabel_ke,

        "Lokasi": lokasi,

        "Jenis Isu": jenis_isu,

        "Nilai Terbaca": (
            nilai_terbaca
            if nilai_terbaca
            else "-"
        ),

        "Konteks Baris": short_value(
            konteks_baris,
            limit=180
        ),

        "Aturan Pemeriksaan": aturan,

        "Status": "Peringatan"

    })


def short_value(
    value,
    limit=120
):
    """
    Memendekkan nilai panjang agar tabel temuan tetap mudah
    dibaca.
    """

    text = str(
        value
    ).strip()

    if len(text) <= limit:
        return text

    return (
        text[:limit - 3]
        + "..."
    )


def iter_table_cells(
    item
):
    """
    Menghasilkan pasangan lokasi dan nilai dari raw_table
    native. Header ikut dicek karena sebagian aturan format
    berada di header/satuan.
    """

    raw_table = item.get(
        "raw_table"
    )

    if not raw_table:
        return

    for row_idx, row in enumerate(
        raw_table,
        start=1
    ):

        if row is None:
            continue

        for col_idx, value in enumerate(
            row,
            start=1
        ):

            if value is None:
                continue

            text = str(
                value
            ).strip()

            if not text:
                continue

            yield (
                f"Baris {row_idx}, Kolom {col_idx}",
                text
            )


def extract_table_text_for_audit(
    item
):
    """
    Mengambil teks tabel dari raw_table jika ada. Untuk tabel
    layout, gunakan area crop agar tetap kompatibel dengan PDF
    yang tidak punya struktur tabel native.
    """

    if item.get("body_text"):
        return item["body_text"]

    raw_table = item.get(
        "raw_table"
    )

    if raw_table:

        rows = []

        for row in raw_table:

            if row is None:
                continue

            rows.append(
                " ".join(
                    str(cell).strip()
                    for cell in row
                    if cell is not None
                    and str(cell).strip()
                )
            )

        return "\n".join(
            row
            for row in rows
            if row
        )

    body_text = item.get(
        "body_text"
    )

    if body_text:

        return body_text

    preview_text = item.get(
        "preview_text"
    )

    if preview_text:

        return preview_text

    page = item.get(
        "page"
    )

    bbox = item.get(
        "bbox"
    )

    if page is not None and bbox:

        try:

            return (
                page.crop(
                    bbox
                ).extract_text()
                or ""
            )

        except Exception:

            pass

    return item.get(
        "page_text",
        ""
    )


def has_column_number_row(
    table_text
):
    """
    Nomor kolom biasanya muncul sebagai (1) (2) (3) ...
    """

    if not table_text:
        return False

    lines = [
        line.strip()
        for line in str(
            table_text
        ).splitlines()
        if line.strip()
    ]

    for idx, line in enumerate(
        lines
    ):

        nearby_text = " ".join(
            lines[
                idx:min(
                    idx + 2,
                    len(lines)
                )
            ]
        )

        numbers = [
            int(
                value
            )
            for value in re.findall(
                r"\(\s*(\d{1,2})\s*\)",
                nearby_text
            )
        ]

        if (
            1 in numbers
            and 2 in numbers
        ):
            return True

        if len(numbers) >= 2:

            sorted_numbers = sorted(
                set(
                    numbers
                )
            )

            for left, right in zip(
                sorted_numbers,
                sorted_numbers[1:]
            ):

                if right == left + 1:
                    return True

    return bool(
        re.search(
            r"\(\s*1\s*\)\D{0,250}\(\s*2\s*\)",
            table_text,
            re.DOTALL
        )
    )


def find_column_number_line_position(
    table_text
):
    """
    Mengembalikan posisi baris nomor kolom dalam teks tabel.
    Nilai berbasis 1 agar sama dengan tampilan lokasi audit.
    """

    lines = [
        line.strip()
        for line in str(
            table_text
        ).splitlines()
    ]

    for idx, line in enumerate(
        lines,
        start=1
    ):

        if re.search(
            r"\(\s*1\s*\).{0,250}\(\s*2\s*\)",
            line
        ):
            return idx

    return None


def find_title_capitalization_issues(
    title
):
    """
    Mencari kata pada judul yang diawali huruf kecil.
    Pengecualian dibuat konservatif untuk kata hubung/depan.

    Teks di dalam tanda kurung (mis. "(tangkai)", "(stalks)")
    dilewati sepenuhnya karena itu adalah satuan yang memang
    wajib huruf kecil — sudah diperiksa tersendiri oleh
    audit_title_unit_lowercase, sehingga tidak perlu (dan
    tidak boleh) ikut ditandai di sini.
    """

    if not title:
        return []

    if re.search(
        r"Tabel\s+terdeteksi",
        title,
        re.IGNORECASE
    ):
        return []

    title_body = re.sub(
        r"^\s*(Tabel|Table)\s+\d+(?:\.\d+)*\.?\s*",
        "",
        title,
        flags=re.IGNORECASE
    )

    title_body = re.sub(
        r"\([^)]*\)",
        " ",
        title_body
    )

    words = re.findall(
        r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-/][A-Za-zÀ-ÖØ-öø-ÿ]+)?",
        title_body
    )

    issues = []

    for word in words:

        if len(word) <= 1:
            continue

        lower_word = word.lower()

        if (
            lower_word in UNIT_KEYWORDS
            and word == lower_word
        ):
            continue

        if lower_word in TITLE_LOWERCASE_EXCEPTIONS:

            if (
                lower_word in TITLE_CONNECTOR_WORDS
                and word != lower_word
            ):

                issues.append(
                    f"{word} -> {lower_word}"
                )

            continue

        if word[0].islower():

            issues.append(
                word
            )

    return issues


def audit_number_format_in_text(
    log_errors,
    halaman,
    tabel_ke,
    lokasi,
    text
):
    """
    Pemeriksaan pemisah ribuan, desimal, nilai nol, dan
    rentang waktu pada sebuah nilai teks.
    """

    text = str(
        text
    ).strip()

    if not text:
        return

    # Pemisah ribuan harus titik. Angka 4 digit yang bukan
    # tahun diperingatkan karena berpotensi belum memakai
    # pemisah ribuan.
    for match in re.finditer(
        r"(?<![\d.,])\d{4,}(?![\d.,])",
        text
    ):

        value = match.group(0)

        if re.fullmatch(
            r"(19|20)\d{2}",
            value
        ):
            continue

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Pemisah Ribuan",
            value,
            "Angka ribuan menggunakan tanda titik (.).",
            text
        )

    for match in re.finditer(
        r"(?<!\d)\d{1,3}(?:,\d{3})+(?:\.\d+)?(?!\d)",
        text
    ):

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Pemisah Ribuan",
            match.group(0),
            "Angka ribuan menggunakan tanda titik (.), bukan koma.",
            text
        )

    # Pemisah desimal harus koma. Titik dengan 1-2 digit di
    # belakangnya diperingatkan sebagai kemungkinan desimal.
    for match in re.finditer(
        r"(?<![\w\d,./])\d+\.\d{1,2}(?![\w\d,./])",
        text
    ):

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Pemisah Desimal",
            match.group(0),
            "Angka desimal menggunakan tanda koma (,).",
            text
        )

    # Nilai 0 berdiri sendiri diberi warning untuk ditinjau
    # manual — kecuali jika "0" tersebut merupakan bagian dari
    # rentang angka (mis. kelompok umur "0-4"/"0–4"), karena
    # itu bukan nilai nol melainkan batas bawah rentang.
    range_spans = [
        (m.start(), m.end())
        for m in re.finditer(
            r"\d+\s*[-–—]\s*\d+",
            text
        )
    ]

    def _is_within_range_span(
        start,
        end
    ):
        return any(
            span_start <= start
            and end <= span_end
            for span_start, span_end in range_spans
        )

    for match in re.finditer(
        r"(?<![\d.,])0(?:,0+)?(?![\d.,])",
        text
    ):

        if _is_within_range_span(
            match.start(),
            match.end()
        ):
            continue

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Nilai 0 Mutlak",
            match.group(0),
            "Nilai 0 diberi warning untuk ditinjau manual.",
            text
        )

    for match in re.finditer(
        r"\b(19|20)\d{2}\s*-\s*(19|20)\d{2}\b",
        text
    ):

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Rentang Waktu",
            match.group(0),
            "Rentang waktu menggunakan en-dash (–), bukan hyphen (-).",
            text
        )


def audit_age_range_format(log_errors, halaman, tabel_ke, title, table_text):
    """Periksa label rentang umur berdasarkan konteks judul/header tabel.

    Audit teks lengkap juga mencakup baris yang tidak tertangkap grid native.
    Batas 0–150 mencegah tahun/kode empat digit dianggap kelompok umur.
    """
    context = str(title) + "\n" + str(table_text)
    if not re.search(r"\b(?:kelompok\s+umur|age\s+groups?)\b", context,
                     re.IGNORECASE):
        return
    for line_idx, line in enumerate(str(table_text).splitlines(), start=1):
        match = re.match(r"^\s*(\d{1,3})\s*-\s*(\d{1,3})(?=\s|$)", line)
        if not match:
            continue
        lower, upper = int(match.group(1)), int(match.group(2))
        if not 0 <= lower < upper <= 150:
            continue
        add_audit_warning(
            log_errors, halaman, tabel_ke, f"Isi Tabel Baris {line_idx}",
            "Rentang Umur", match.group(0).strip(),
            "Rentang umur menggunakan en-dash (–), bukan hyphen (-). "
            f"Gunakan {match.group(1)}–{match.group(2)}.", line.strip()
        )


def audit_unit_format_in_text(
    log_errors,
    halaman,
    tabel_ke,
    lokasi,
    text
):
    """
    Satuan diperingatkan jika ditulis dengan huruf kapital.
    """

    text = str(
        text
    ).strip()

    if not text:
        return

    seen_units = set()

    def looks_like_unit(value):

        tokens = re.findall(
            r"[A-Za-z0-9]+",
            value.lower()
        )

        return any(
            token in UNIT_KEYWORDS
            for token in tokens
        )

    candidates = []

    for match in re.finditer(
        r"\(([^)]{1,80})\)",
        text
    ):

        inner_value = match.group(1).strip()

        if looks_like_unit(
            inner_value
        ):

            candidates.append(
                match.group(0)
            )

    unit_word_pattern = re.compile(
        r"\b("
        r"Miliar\s+Rupiah|Juta\s+Rupiah|Ribu\s+Rupiah|"
        r"Miliar\s+Rp|Juta\s+Rp|Ribu\s+Rp|"
        r"Rupiah|Persen|"
        r"KM2|Km2|KM|Km|MDPL|"
        r"Ha|HA|Hectare|Hectares|"
        r"Kg|KG|Kilogram|Kilograms|"
        r"Kuintal|Quintal|Quintals|"
        r"Ton|Tons|Liter|Liters|Litre|Litres|"
        r"Meter|Meters|Metre|Metres|"
        r"Kilometer|Kilometers|Kilometre|Kilometres|"
        r"Mbar"
        r")\b"
    )

    text_without_parentheses = re.sub(
        r"\([^)]*\)",
        " ",
        text
    )

    for match in unit_word_pattern.finditer(
        text_without_parentheses
    ):

        candidates.append(
            match.group(0)
        )

    for value in candidates:

        normalized_value = (
            value.strip("()")
            .strip()
            .lower()
        )

        if normalized_value in seen_units:
            continue

        seen_units.add(
            normalized_value
        )

        if not re.search(
            r"[A-Z]",
            value
        ):
            continue

        if re.fullmatch(
            r"\([0-9\s]+\)",
            value
        ):
            continue

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            lokasi,
            "Satuan",
            value,
            "Satuan menggunakan huruf kecil.",
            text
        )


# ----------------------------------------------------------
# Kata dalam kurung pada judul tabel yang BUKAN merupakan
# satuan (mis. penanda "(Lanjutan)"/"(Continued)"), sehingga
# tidak diperiksa sebagai satuan.
# ----------------------------------------------------------

NON_UNIT_PAREN_KEYWORDS = {
    "lanjutan",
    "continued",
    "concluded",
    "sambungan",
    "cont",
}


def is_abbreviation_of_preceding_words(
    inner_value,
    preceding_text
):
    """
    Mengecek apakah teks di dalam kurung merupakan singkatan dari
    beberapa kata yang tepat mendahuluinya (mis. "Rukun Warga (RW)",
    "Kepala Keluarga (KK)"), bukan satuan — dengan mencocokkan huruf
    awal kata-kata sebelum kurung terhadap huruf-huruf singkatan
    tersebut.
    """

    # Singkatan selalu berupa huruf kapital semua, tanpa spasi.
    if not re.fullmatch(
        r"[A-Z]{2,6}",
        inner_value
    ):
        return False

    preceding_words = re.findall(
        r"[A-Za-z]+",
        preceding_text
    )

    jumlah_huruf = len(inner_value)

    if len(preceding_words) < jumlah_huruf:
        return False

    candidate_words = preceding_words[
        -jumlah_huruf:
    ]

    initials = "".join(
        word[0].upper()
        for word in candidate_words
    )

    return initials == inner_value


def audit_title_unit_lowercase(
    log_errors,
    halaman,
    tabel_ke,
    title
):
    """
    Semua teks di dalam tanda kurung pada judul tabel
    dianggap sebagai satuan, dan wajib ditulis dengan huruf
    kecil sesuai pedoman — tidak dibatasi hanya pada kata
    yang dikenali di UNIT_KEYWORDS.

    Terkecuali jika teks di dalam kurung merupakan singkatan
    dari kata-kata yang mendahuluinya (mis. "Rukun Warga
    (RW)"), karena itu bukan satuan.
    """

    title = str(
        title
    ).strip()

    if not title:
        return

    seen_units = set()

    for match in re.finditer(
        r"\(([^)]{1,80})\)",
        title
    ):

        inner_value = match.group(1).strip()

        if not inner_value:
            continue

        # Lewati kurung yang hanya berisi angka/simbol,
        # mis. "(1)" atau "(2020=100)"
        if re.fullmatch(
            r"[0-9\s.,\-–=]+",
            inner_value
        ):
            continue

        first_word = re.split(
            r"\s+",
            inner_value.lower()
        )[0].strip(".,")

        if first_word in NON_UNIT_PAREN_KEYWORDS:
            continue

        # Lewati singkatan dari kata sebelumnya,
        # mis. "Rukun Warga (RW)"
        if is_abbreviation_of_preceding_words(
            inner_value,
            title[:match.start()]
        ):
            continue

        normalized_value = inner_value.lower()

        if normalized_value in seen_units:
            continue

        seen_units.add(
            normalized_value
        )

        if not re.search(
            r"[A-Z]",
            inner_value
        ):
            continue

        add_audit_warning(
            log_errors,
            halaman,
            tabel_ke,
            "Judul Tabel",
            "Satuan",
            match.group(0),
            "Satuan pada judul tabel harus menggunakan huruf kecil.",
            title
        )


def audit_detected_tables(
    detected_tables
):
    """
    Audit warning-only untuk 8 kebutuhan:
    kapitalisasi judul, pemisah ribuan, pemisah desimal,
    nilai nol, nomor kolom, rentang waktu, satuan, dan titik
    setelah nomor tabel.
    """

    log_errors = []

    error_cell_map = {}

    for table_idx, item in enumerate(
        detected_tables,
        start=1
    ):

        halaman = item.get(
            "halaman",
            "-"
        )

        nomor_tabel = item.get(
            "nomor_tabel"
        )

        tabel_ke = (
            nomor_tabel
            if nomor_tabel
            else table_idx
        )

        table_key = (
            halaman,
            tabel_ke
        )

        error_cell_map[
            table_key
        ] = set()

        title = item.get(
            "judul",
            ""
        )

        raw_title = (
            item.get(
                "raw_title_line"
            )
            or title
        )

        table_text = (
            extract_table_text_for_audit(
                item
            )
        )

        audit_age_range_format(
            log_errors, halaman, tabel_ke, title, table_text
        )

        capitalization_issues = (
            find_title_capitalization_issues(
                title
            )
        )

        if capitalization_issues:

            add_audit_warning(
                log_errors,
                halaman,
                tabel_ke,
                "Judul Tabel",
                "Capitalization Judul Tabel",
                ", ".join(
                    capitalization_issues
                ),
                (
                    "Kata utama diawali huruf kapital; "
                    "kata hubung/depan ditulis huruf kecil."
                ),
                title
            )

        if item.get(
            "titik_setelah_nomor"
        ):

            add_audit_warning(
                log_errors,
                halaman,
                tabel_ke,
                "Judul Tabel",
                "Titik Setelah Nomor Tabel",
                short_value(
                    raw_title
                ),
                "Tidak terdapat titik setelah nomor tabel.",
                raw_title
            )

        audit_title_unit_lowercase(
            log_errors,
            halaman,
            tabel_ke,
            title
        )

        if not has_column_number_row(
            table_text
        ):

            add_audit_warning(
                log_errors,
                halaman,
                tabel_ke,
                "Struktur Tabel",
                "Keberadaan Nomor Kolom",
                "-",
                "Harus ada nomor kolom pada tabel sesuai pedoman.",
                table_text
            )

        raw_table = item.get(
            "raw_table"
        )

        if raw_table:

            for lokasi, value in iter_table_cells(
                item
            ):

                audit_number_format_in_text(
                    log_errors,
                    halaman,
                    tabel_ke,
                    lokasi,
                    value
                )

                audit_unit_format_in_text(
                    log_errors,
                    halaman,
                    tabel_ke,
                    lokasi,
                    value
                )

        else:

            column_number_line = (
                find_column_number_line_position(
                    table_text
                )
            )

            for line_idx, line in enumerate(
                table_text.splitlines(),
                start=1
            ):

                value = line.strip()

                if not value:
                    continue

                if (
                    column_number_line
                    and line_idx < column_number_line
                ):

                    lokasi = (
                        f"Judul/Header Tabel Baris {line_idx}"
                    )

                else:

                    lokasi = (
                        f"Isi Tabel Baris {line_idx}"
                    )

                audit_number_format_in_text(
                    log_errors,
                    halaman,
                    tabel_ke,
                    lokasi,
                    value
                )

                audit_unit_format_in_text(
                    log_errors,
                    halaman,
                    tabel_ke,
                    lokasi,
                    value
                )

    df_log = pd.DataFrame(
        log_errors
    )

    return (
        df_log,
        error_cell_map
    )


# ============================================================
# ============================================================
# EXTRACT NATIVE TABLE DATA
# ============================================================
# ============================================================

def prepare_native_tables_for_audit(
    native_tables
):
    """
    Mengubah hasil Engine 1 menjadi format yang bisa
    digunakan oleh audit_table_format().
    """

    extracted_data = []


    for item in native_tables:

        raw_table = item[
            "raw_table"
        ]

        if (
            not raw_table
            or len(raw_table) < 2
        ):
            continue


        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        headers = [

            str(col).strip()
            if col
            else f"Kolom_{i+1}"

            for i, col in enumerate(
                raw_table[0]
            )

        ]


        data_rows = (
            raw_table[1:]
        )


        try:

            df = pd.DataFrame(
                data_rows,
                columns=headers
            )

        except Exception:

            continue


        extracted_data.append({

            "halaman": item[
                "halaman"
            ],

            "tabel_ke": item[
                "table_index"
            ],

            "dataframe": df

        })


    return extracted_data


# ============================================================
# ============================================================
# EXCEL REPORT
# ============================================================
# ============================================================

def format_halaman_display(
    item
):
    """
    Menampilkan nomor halaman, ditambah keterangan halaman
    lanjutan jika tabel ini bersambung ke halaman berikutnya
    (ditandai "Lanjutan Tabel/Continued Table").
    """

    halaman = item.get(
        "halaman"
    )

    halaman_lanjutan = item.get(
        "halaman_lanjutan"
    )

    if not halaman_lanjutan:
        return halaman

    lanjutan_str = ", ".join(
        str(h)
        for h in halaman_lanjutan
    )

    return (
        f"{halaman} "
        f"(lanjutan: hal. {lanjutan_str})"
    )


def generate_excel_detection_report(
    detected_tables
):

    data = []


    for i, item in enumerate(
        detected_tables,
        start=1
    ):

        data.append({

            "No.": i,

            "Halaman": (
                format_halaman_display(
                    item
                )
            ),

            "Nomor Tabel": item.get(
                "nomor_tabel"
            ),

            "Judul Tabel": item.get(
                "judul"
            ),

            "Format Judul": item.get(
                "format_judul"
            ),

            "Detector": item.get(
                "sumber_detector"
            ),

            "Status": item.get(
                "status"
            )

        })


    df = pd.DataFrame(
        data
    )


    output = io.BytesIO()


    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Tabel Terdeteksi"
        )


    return output.getvalue()


# ============================================================
# 🖥️ SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### Dokumen")
    st.caption("Pilih publikasi yang akan ditelaah.")

    uploaded_file = st.file_uploader(
        "Unggah Publikasi PDF",
        type=["pdf"],
        help="Unggah dokumen publikasi statistik dalam format PDF."
    )


    with st.expander(
        "Opsi lanjutan",
        expanded=False
    ):

        use_native_detection = st.checkbox(
            "Gunakan Native Table Detection",
            value=False,
            help=(
                "Nonaktifkan untuk mode cepat. Aktifkan hanya jika "
                "perlu membaca struktur tabel PDF sebagai DataFrame."
            )
        )

        if st.button(
            "Bersihkan cache deteksi",
            use_container_width=True
        ):

            st.cache_data.clear()
            st.rerun()


    st.divider()
    st.caption("SiTELITI · Telaah format tabel publikasi statistik BPS")


# ============================================================
# MAIN AREA
# ============================================================

st.markdown(
    """
    <div class="siteliti-hero">
        <h1><span class="hero-icon" aria-hidden="true">🔍</span><span>SiTELITI</span></h1>
        <p>Sistem Telaah Konsistensi Format Tabel Publikasi Statistik</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILE UPLOADED
# ============================================================

if uploaded_file is not None:

    file_content = uploaded_file.getvalue()

    # ========================================================
    # DETEKSI
    # ========================================================

    with st.spinner(
        "Mendeteksi tabel dari publikasi..."
    ):

        (
            detected_tables,
            native_tables,
            layout_tables,
            total_pages,
            excluded_pages
        ) = detect_all_tables_cached(
            file_content,
            use_native_detection,
            APP_CACHE_VERSION
        )


    total_tables = len(
        detected_tables
    )


    # ========================================================
    # AUDIT WARNING-ONLY
    # ========================================================

    if detected_tables:

        (
            df_log,
            error_map
        ) = audit_detected_tables(
            detected_tables
        )

    else:

        df_log = pd.DataFrame()

        error_map = {}


    total_temuan = len(
        df_log
    )


    # ========================================================
    # SIDEBAR DOWNLOAD
    # ========================================================

    with st.sidebar:

        if detected_tables:

            excel_data = (
                generate_excel_detection_report(
                    detected_tables
                )
            )


            st.download_button(
                "Unduh daftar tabel",
                data=excel_data,
                file_name=(
                    "daftar_tabel_siteliti.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )


        if not df_log.empty:

            st.download_button(
                "Unduh rekap temuan",
                data=(
                    io.BytesIO(
                        df_log.to_csv(
                            index=False
                        ).encode(
                            "utf-8"
                        )
                    ).getvalue()
                ),
                file_name=(
                    "rekap_temuan_siteliti.csv"
                ),
                mime="text/csv"
            )


    # ========================================================
    # METRICS
    # ========================================================

    st.caption(f"Dokumen: {uploaded_file.name}")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card(total_pages, "Halaman")
    with col2:
        render_metric_card(total_tables, "Tabel terdeteksi", color="#147d72")
    with col3:
        render_metric_card(total_temuan, "Temuan format",
                           color="#b36b00" if total_temuan else "#147d72")

    # ========================================================
    # INFO DAFTAR TABEL
    # ========================================================

    # DAFTAR TABEL
    # ========================================================

    tab_temuan, tab_preview, tab_daftar = st.tabs(
        ["Temuan format", "Pratinjau tabel", "Daftar tabel"]
    )

    with tab_temuan:
        render_section_title(
            "Temuan format",
            "Tinjau peringatan berikut dan bandingkan dengan tabel aslinya."
        )


        if not df_log.empty:

            st.dataframe(
                style_status_column(df_log, column="Status"),
                use_container_width=True,
                hide_index=True
            )

        elif detected_tables:

            st.success(
                "Tidak ada temuan format pada tabel yang berhasil diekstrak."
            )


        else:
            st.info("Temuan belum tersedia karena belum ada tabel yang terdeteksi.")


    with tab_preview:
        render_section_title(
            "Pratinjau tabel",
            "Pilih salah satu tabel untuk melihat detail dan isi datanya."
        )


        if detected_tables:

            table_options = [

                (
                    f"Tabel "
                    f"{item.get('nomor_tabel', '?')} "
                    f"— Hal. "
                    f"{item.get('halaman')}"
                )

                for item in detected_tables

            ]


            selected_idx = st.selectbox(
                "Pilih tabel:",
                range(
                    len(table_options)
                ),
                format_func=lambda x:
                    table_options[x]
            )


            active_table = (
                detected_tables[
                    selected_idx
                ]
            )


            # ----------------------------------------------------
            # Informasi
            # ----------------------------------------------------

            st.caption(f"Tabel {active_table.get('nomor_tabel', '-')} · "
                       f"Halaman {format_halaman_display(active_table)}")

            st.markdown(
                f"""
                **Judul Tabel:**  
                {active_table.get("judul", "-")}
                """
            )


            with st.expander("Detail deteksi tabel"):
                st.caption(f"Metode: {active_table.get('sumber_detector', '-')}")
                st.caption(f"Format judul: {active_table.get('format_judul', '-')}")

            # ----------------------------------------------------
            # Jika native table → tampilkan DataFrame
            # ----------------------------------------------------

            if active_table.get(
                "raw_table"
            ):

                raw_table = (
                    active_table[
                        "raw_table"
                    ]
                )


                if len(raw_table) >= 2:

                    headers = [

                        str(col).strip()
                        if col
                        else f"Kolom_{i+1}"

                        for i, col in enumerate(
                            raw_table[0]
                        )

                    ]


                    preview_df = pd.DataFrame(
                        raw_table[1:],
                        columns=headers
                    )


                    st.dataframe(
                        preview_df,
                        use_container_width=True
                    )


            # ----------------------------------------------------
            # Jika layout detector
            # ----------------------------------------------------

            if active_table.get(
                "preview_text"
            ):

                try:

                    preview_text = active_table.get(
                        "preview_text",
                        ""
                    )


                    if preview_text:

                        st.text_area(
                            "Teks hasil ekstraksi",
                            preview_text,
                            height=400
                        )

                    else:

                        st.warning(
                            "Area tabel berhasil "
                            "ditemukan, tetapi teks "
                            "tidak dapat diekstrak."
                        )

                except Exception:

                    st.warning(
                        "Preview tabel tidak dapat "
                        "ditampilkan."
                    )


        else:

            st.info(
                "Belum ada tabel untuk ditampilkan."
            )


    with tab_daftar:
        render_section_title(
            "Daftar tabel",
            "Daftar tabel yang ditemukan dalam dokumen."
        )


        if detected_tables:

            detection_df = (
                pd.DataFrame([

                    {

                        "No.": i,

                        "Halaman": (
                            format_halaman_display(
                                item
                            )
                        ),

                        "Nomor Tabel": item.get(
                            "nomor_tabel"
                        ),

                        "Judul Tabel": item.get(
                            "judul"
                        ),

                        "Format Judul": item.get(
                            "format_judul"
                        ),

                        "Detector": item.get(
                            "sumber_detector"
                        ),

                        "Status": item.get(
                            "status"
                        )

                    }

                    for i, item in enumerate(
                        detected_tables,
                        start=1
                    )

                ])
            )


            st.dataframe(
                style_status_column(detection_df, column="Status"),
                use_container_width=True,
                hide_index=True
            )


        else:

            st.warning(
                "Belum ada tabel yang terdeteksi."
            )



    # ========================================================
    # DEBUG / INFORMASI DETECTOR
    # ========================================================

    with st.expander(
        "Informasi deteksi"
    ):

        if excluded_pages:

            excluded_numbers = ", ".join(
                str(x + 1)
                for x in sorted(
                    excluded_pages
                )
            )

            st.info(
                "Halaman yang dikecualikan karena "
                "teridentifikasi sebagai Daftar Tabel / "
                "Daftar Lampiran: "
                f"**{excluded_numbers}**"
            )


        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric(
                "Native Table Detection",
                f"{len(native_tables)} tabel"
            )

        with info_col2:
            st.metric(
                "Title/Layout Detection",
                f"{len(layout_tables)} tabel"
            )

        with info_col3:
            st.metric(
                "Setelah Penggabungan",
                f"{len(detected_tables)} tabel"
            )

        st.caption(
            "Jika kedua engine menemukan tabel "
            "yang sama, tabel hanya dihitung satu kali."
        )




# ============================================================
# BELUM ADA FILE
# ============================================================

else:
    render_section_title("Mulai telaah publikasi", "Unggah PDF melalui sidebar untuk melihat tabel dan temuan format.")
    step1, step2, step3 = st.columns(3)
    for column, number, title, description in (
        (step1, "01", "Unggah dokumen", "Pilih publikasi statistik dalam format PDF."),
        (step2, "02", "Tinjau temuan", "Periksa peringatan nomor kolom, angka, rentang, dan satuan."),
        (step3, "03", "Periksa tabel", "Lihat teks hasil ekstraksi dan unduh rekap untuk tindak lanjut."),
    ):
        with column:
            st.markdown(
                f'<div class="siteliti-step-card"><div class="step-num">{number}</div>'
                f'<h4>{title}</h4><p>{description}</p></div>',
                unsafe_allow_html=True
            )