import re

from pypdf import PdfReader


CLASS_PATTERN = re.compile(
    r"(\d{1,2})\.\s*S(ı|i)n(ı|i)f(?:-Hafif\s+Zihinsel)?\s*/\s*([A-E]|[Ö])\s*(Ş|S)ubesi",
    re.IGNORECASE,
)
STUDENT_LINE_PATTERN = re.compile(
    r"^\s*(\d+)\s+(.+?)\s+(Erkek|Kız)([A-ZÇĞİÖŞÜÂÊÎÔÛA-Za-zçğıöşü'`\- ]+?)\s+(\d+)\s*$"
)


def normalize_class_name(raw_text: str) -> str:
    return " ".join(raw_text.split())


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_pdf_rosters(pdf_path: str) -> dict[str, list[str]]:
    reader = PdfReader(pdf_path)
    rosters: dict[str, list[str]] = {}

    for pdf_page in reader.pages:
        page = pdf_page.extract_text() or ""
        if not page.strip():
            continue
        class_match = CLASS_PATTERN.search(page)
        if class_match is None:
            continue

        class_name = normalize_class_name(class_match.group(0))
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        names: list[str] = []
        for line in lines:
            if "Kız Öğrenci Sayısı" in line:
                break
            student_match = STUDENT_LINE_PATTERN.match(line)
            if student_match is None:
                continue
            first_names = " ".join(student_match.group(2).split())
            surname = " ".join(student_match.group(4).split())
            full_name = f"{first_names} {surname}".strip()
            if full_name:
                names.append(full_name)

        rosters[class_name] = names

    if not rosters:
        raise ValueError("No classes matched the expected regex in the selected PDF.")

    return rosters
