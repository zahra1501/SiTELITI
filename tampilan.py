import io
import re
import streamlit as st
import pandas as pd
import pdfplumber


# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="SiTELITI",
    page_icon="📑",
    layout="wide"
)


# ============================================================
# ⚙️ BACKEND FUNCTIONS
# ============================================================


# ============================================================
# 1. MEMBERSIHKAN WATERMARK
# ============================================================

def clean_pdf_words(words):
    """
    Membersihkan hasil ekstraksi word PDF.

    Watermark diagonal biasanya memiliki:
        upright = False

    sehingga tidak digunakan dalam proses deteksi layout.
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

        cleaned_words.append(word)

    return cleaned_words


# ============================================================
# 2. GROUP WORDS MENJADI BARIS
# ============================================================

def group_words_into_lines(
    words,
    tolerance=3
):
    """
    Mengelompokkan word berdasarkan posisi vertikal.
    """

    lines = []

    for word in words:

        placed = False

        for line in lines:

            if abs(
                word["top"] - line["top"]
            ) <= tolerance:

                line["words"].append(word)

                line["top"] = min(
                    line["top"],
                    word["top"]
                )

                line["bottom"] = max(
                    line["bottom"],
                    word["bottom"]
                )

                placed = True
                break

        if not placed:

            lines.append({
                "top": word["top"],
                "bottom": word["bottom"],
                "words": [word]
            })

    lines.sort(
        key=lambda x: x["top"]
    )

    for line in lines:

        line["words"] = sorted(
            line["words"],
            key=lambda x: x["x0"]
        )

        line["text"] = " ".join(
            word["text"]
            for word in line["words"]
        ).strip()

    return lines


# ============================================================
# 3. DETEKSI HALAMAN DAFTAR TABEL
# ============================================================

def detect_index_pages(pdf):

    excluded_pages = set()

    for page_idx, page in enumerate(pdf.pages):

        text = page.extract_text() or ""

        text_lower = text.lower()

        # --------------------------------------------
        # Halaman yang memiliki heading Daftar Tabel
        # --------------------------------------------

        if re.search(
            r"\bdaftar\s+tabel\b",
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
                        r"\bTabel\s+\d+",
                        next_text,
                        re.IGNORECASE
                    )
                )

                jumlah_standalone = len(
                    re.findall(
                        r"^\s*Tabel\s*$",
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
    r"^\s*\d+(?:\.\d+)+\.?\s*$"
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
        r"(\d+(?:\.\d+)+)\.?\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        return {
            "nomor_tabel": match.group(2),
            "title_start_index": index,
            "title_end_index": index,
            "format": "satu_baris",
            "top": current_line["top"],
            "bottom": current_line["bottom"]
        }


    # ========================================================
    # FORMAT B
    # Tabel 1.1 Judul
    # ========================================================

    match = re.match(
        r"^\s*(Tabel|Table)\s+"
        r"(\d+(?:\.\d+)+)\.?\s+.+$",
        text,
        re.IGNORECASE
    )

    if match:

        return {
            "nomor_tabel": match.group(2),
            "title_start_index": index,
            "title_end_index": index,
            "format": "satu_baris_dengan_judul",
            "top": current_line["top"],
            "bottom": current_line["bottom"]
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

    search_end = min(
        start_index + 40,
        len(lines)
    )

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

        # --------------------------------------------
        # Tabel berikutnya
        # --------------------------------------------

        if re.match(
            r"^\s*(Tabel|Table)\s+\d+",
            text,
            re.IGNORECASE
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

    return {
        "body_top": structural_lines[0]["top"],
        "body_bottom": structural_lines[-1]["bottom"],
        "structural_lines": structural_lines
    }


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
                    page.extract_tables()
                )

            except Exception:

                tables = []

            for table_idx, raw_table in enumerate(
                tables
            ):

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

                # ----------------------------------------
                # Cari nomor tabel yang muncul di halaman
                # ----------------------------------------

                table_numbers = re.findall(
                    r"\bTabel\s+"
                    r"(\d+(?:\.\d+)+)",
                    page_text,
                    re.IGNORECASE
                )

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

                    "page": page

                })

    return detected


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

        excluded_pages = (
            detect_index_pages(pdf)
        )

        total_pages = len(
            pdf.pages
        )

        for page_idx, page in enumerate(
            pdf.pages
        ):

            if page_idx in excluded_pages:
                continue

            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=3,
                keep_blank_chars=False
            )

            words = clean_pdf_words(
                words
            )

            if not words:
                continue

            lines = group_words_into_lines(
                words
            )

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
                            full_title
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

                        "page": page,

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

                    next_page = (
                        pdf.pages[
                            page_idx + 1
                        ]
                    )

                    next_words = (
                        next_page.extract_words(
                            x_tolerance=2,
                            y_tolerance=3,
                            keep_blank_chars=False
                        )
                    )

                    next_words = (
                        clean_pdf_words(
                            next_words
                        )
                    )

                    if next_words:

                        next_lines = (
                            group_words_into_lines(
                                next_words
                            )
                        )

                        next_body = (
                            find_table_body_on_page(
                                next_lines,
                                -1
                            )
                        )

                        if next_body is not None:

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
                                    full_title
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

                                "page": page,

                                "bbox": (
                                    0,
                                    candidate["top"],
                                    page.width,
                                    page.height - 30
                                )

                            })

    return detected


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
                999
            )

        try:

            nomor_parts = [
                int(x)
                for x in nomor.split(".")
            ]

            return (
                halaman,
                nomor_parts
            )

        except Exception:

            return (
                halaman,
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
    file_bytes
):

    # ========================================================
    # ENGINE 1
    # ========================================================

    native_tables = (
        detect_tables_native(
            file_bytes
        )
    )


    # ========================================================
    # ENGINE 2
    # ========================================================

    layout_tables = (
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
        layout_tables
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

                        "Status": "Kritis"

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

            "Halaman": item.get(
                "halaman"
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

    st.header(
        "⚙️ Pengaturan & Input"
    )


    uploaded_file = st.file_uploader(
        "Unggah Publikasi PDF",
        type=["pdf"]
    )


    st.divider()


    st.caption(
        "SiTELITI digunakan untuk membantu "
        "menelaah konsistensi format tabel "
        "pada publikasi statistik BPS."
    )


# ============================================================
# MAIN AREA
# ============================================================

st.title(
    "📑 SiTELITI"
)

st.caption(
    "Sistem Telaah Kesalahan Format Tabel Statistik"
)


# ============================================================
# FILE UPLOADED
# ============================================================

if uploaded_file is not None:

    # ========================================================
    # DETEKSI
    # ========================================================

    with st.spinner(
        "Mendeteksi tabel dari publikasi..."
    ):

        (
            detected_tables,
            native_tables,
            layout_tables
        ) = detect_all_tables(
            uploaded_file
        )


    total_pages = 0


    # Ambil jumlah halaman
    with pdfplumber.open(
        uploaded_file
    ) as pdf:

        total_pages = len(
            pdf.pages
        )

        excluded_pages = (
            detect_index_pages(
                pdf
            )
        )


    total_tables = len(
        detected_tables
    )


    # ========================================================
    # AUDIT ENGINE 1
    # ========================================================

    native_audit_data = (
        prepare_native_tables_for_audit(
            native_tables
        )
    )


    if native_audit_data:

        (
            df_log,
            error_map
        ) = audit_table_format(
            native_audit_data
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
                "📥 Unduh Daftar Tabel",
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
                "📥 Unduh Rekap Temuan",
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

    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        with st.container(
            border=True
        ):

            st.markdown(
                f"""
                <h1 style="
                    margin:0;
                    font-size:2.2rem;
                ">
                    {total_pages}
                </h1>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <p style="
                    margin:0;
                    color:gray;
                    font-size:1rem;
                ">
                    Halaman
                </p>
                """,
                unsafe_allow_html=True
            )


    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                f"""
                <h1 style="
                    margin:0;
                    font-size:2.2rem;
                ">
                    {total_tables}
                </h1>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <p style="
                    margin:0;
                    color:gray;
                    font-size:1rem;
                ">
                    Tabel Terdeteksi
                </p>
                """,
                unsafe_allow_html=True
            )


    with col3:

        accent_color = (
            "#ff4b4b"
            if total_temuan > 0
            else "#28a745"
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"""
                <h1 style="
                    margin:0;
                    font-size:2.2rem;
                    color:{accent_color};
                ">
                    {total_temuan}
                </h1>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <p style="
                    margin:0;
                    color:gray;
                    font-size:1rem;
                ">
                    Temuan Format
                </p>
                """,
                unsafe_allow_html=True
            )


    st.divider()


    # ========================================================
    # INFO DAFTAR TABEL
    # ========================================================

    if excluded_pages:

        excluded_numbers = ", ".join(
            str(x + 1)
            for x in sorted(
                excluded_pages
            )
        )

        st.info(
            "Halaman yang dikecualikan karena "
            "teridentifikasi sebagai Daftar Tabel: "
            f"**{excluded_numbers}**"
        )


    # ========================================================
    # DEBUG / INFORMASI DETECTOR
    # ========================================================

    with st.expander(
        "🔧 Informasi Deteksi"
    ):

        st.write(
            f"Native Table Detection: "
            f"**{len(native_tables)} tabel**"
        )

        st.write(
            f"Title/Layout Detection: "
            f"**{len(layout_tables)} tabel**"
        )

        st.write(
            f"Setelah penggabungan: "
            f"**{len(detected_tables)} tabel**"
        )

        st.caption(
            "Jika kedua engine menemukan tabel "
            "yang sama, tabel hanya dihitung satu kali."
        )


    # ========================================================
    # DAFTAR TABEL
    # ========================================================

    st.subheader(
        "📋 Daftar Tabel yang Terdeteksi"
    )


    if detected_tables:

        detection_df = (
            pd.DataFrame([

                {

                    "No.": i,

                    "Halaman": item.get(
                        "halaman"
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
            detection_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.warning(
            "Belum ada tabel yang terdeteksi."
        )


    # ========================================================
    # PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "🔍 Pratinjau Tabel"
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

        col_a, col_b, col_c = (
            st.columns(3)
        )


        with col_a:

            st.metric(
                "Nomor Tabel",
                active_table.get(
                    "nomor_tabel"
                )
                or "-"
            )


        with col_b:

            st.metric(
                "Halaman",
                active_table.get(
                    "halaman"
                )
            )


        with col_c:

            st.metric(
                "Detector",
                active_table.get(
                    "sumber_detector",
                    "-"
                )
            )


        st.markdown(
            f"""
            **Judul Tabel:**  
            {active_table.get("judul", "-")}
            """
        )


        st.caption(
            "Format judul: "
            f"`{active_table.get('format_judul', '-')}`"
        )


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

        elif active_table.get(
            "page"
        ):

            try:

                bbox = active_table.get(
                    "bbox"
                )


                if bbox:

                    cropped = (
                        active_table[
                            "page"
                        ].crop(
                            bbox
                        )
                    )


                    preview_text = (
                        cropped.extract_text()
                        or ""
                    )


                    if preview_text:

                        st.text_area(
                            "Teks yang terbaca:",
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


    # ========================================================
    # AUDIT FORMAT
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Daftar Temuan Format"
    )


    if not df_log.empty:

        st.dataframe(
            df_log,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Belum ada temuan format dari "
            "tabel yang dapat diekstrak."
        )


# ============================================================
# BELUM ADA FILE
# ============================================================

else:

    st.info(
        "Silakan unggah dokumen publikasi PDF "
        "di sidebar untuk memulai proses "
        "penelaahan."
    )


    st.markdown(
        """
        ### Cara kerja SiTELITI

        **1. Deteksi tabel**

        SiTELITI menggunakan dua metode:

        - **Native Table Detection**, untuk PDF yang
          struktur tabelnya dapat dibaca langsung
          oleh PDF parser.
        - **Title/Layout Detection**, untuk PDF yang
          tabelnya tidak terbaca sebagai objek tabel
          tetapi masih memiliki struktur teks dan
          posisi/layout.

        **2. Penggabungan hasil**

        Hasil dari kedua metode digabung dan tabel
        yang sama tidak dihitung dua kali.

        **3. Pemeriksaan format**

        Setelah tabel ditemukan, sistem dapat
        memeriksa aturan format seperti:

        - nomor kolom;
        - format angka;
        - tanda desimal;
        - pemisah ribuan;
        - simbol nol;
        - satuan;
        - dan aturan format lainnya.

        **Catatan:** nomor kolom tidak digunakan
        sebagai syarat pendeteksian tabel karena
        ketiadaan nomor kolom sendiri merupakan
        salah satu kesalahan yang perlu diperiksa.
        """
    )