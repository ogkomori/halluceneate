import fitz
import docx
from pathlib import Path

class FileClassifier:
    def __init__(self):
        self.title_keywords = {
            "Resumes": ["cv", "resume", "curriculum vitae"],
            "Invoices": ["invoice", "receipt", "bill"],
            "Notes": ["notes", "lecture", "slides", "class"],
            "Transcripts": ["transcript", "results", "grades"],
        }

        self.content_keywords = {
            "Resumes": ["experience", "education", "skills", "projects"],
            "Invoices": ["total", "amount", "payment", "due"],
            "Notes": ["introduction", "summary", "topic", "chapter"],
            "Transcripts": ["semester", "grade", "credit", "gpa"],
        }

    def classify(self, file_path: Path) -> str:
        title = file_path.stem.lower()
        label = self.classify_by_title(title)
        if not label:
            content = self.extract_content(file_path)
            label = self.classify_by_content(content)
        return label or "Other"

    def classify_by_title(self, title: str) -> str | None:
        for label, keywords in self.title_keywords.items():
            if any(word in title for word in keywords):
                return label
        return None

    def classify_by_content(self, content: str) -> str | None:
        content_lower = content.lower()
        for label, keywords in self.content_keywords.items():
            if any(word in content_lower for word in keywords):
                return label
        return None

    def extract_content(self, file_path: Path) -> str | None:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        if ext in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        if ext in [".txt", ".md"]:
            return self.extract_text_from_txt(file_path)

        return None

    @staticmethod
    def extract_text_from_pdf(file_path: Path, max_pages=2) -> str:
        text = ""
        doc = fitz.open(file_path)
        for page in doc[:max_pages]:
            text += page.get_text()
        return text

    @staticmethod
    def extract_text_from_docx(file_path: Path):
        doc = docx.Document(str(file_path))
        return "\n".join([p.text for p in doc.paragraphs])

    @staticmethod
    def extract_text_from_txt(file_path: Path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
