"""PDF to Markdown Converter - PySide6 GUI Application with Figma-style design."""

import os
import sys
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QMimeData,
    QPropertyAnimation,
    QSize,
    Qt,
    QThread,
    Signal,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pdf_converter.converter import convert_pdf_to_markdown
from pdf_converter.styles import COLORS, FIGMA_STYLESHEET


class ConvertWorker(QThread):
    """Worker thread for PDF conversion to keep the GUI responsive."""

    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, pdf_path: str, output_path: str, extract_images: bool):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.extract_images = extract_images

    def run(self):
        try:
            result = convert_pdf_to_markdown(
                self.pdf_path,
                self.output_path,
                extract_imgs=self.extract_images,
                progress_callback=self._on_progress,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, current: int, total: int):
        self.progress.emit(current, total)


class DropZone(QFrame):
    """Drag-and-drop zone for PDF files."""

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; border: none; background: transparent;")
        layout.addWidget(icon_label)

        title = QLabel("PDF 파일을 드래그 & 드롭하세요")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};"
            " border: none; background: transparent;"
        )
        layout.addWidget(title)

        subtitle = QLabel("또는 아래 버튼을 클릭하여 파일을 선택하세요")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: 13px; color: {COLORS['text_muted']};"
            " border: none; background: transparent;"
        )
        layout.addWidget(subtitle)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    self.setStyleSheet(
                        f"""QFrame#dropZone {{
                            background-color: {COLORS['bg_hover']};
                            border: 2px dashed {COLORS['accent']};
                            border-radius: 16px;
                            padding: 40px;
                        }}"""
                    )
                    return

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".pdf"):
                self.file_dropped.emit(file_path)
                return


class MainWindow(QMainWindow):
    """Main application window with Figma-inspired design."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF → Markdown 변환기")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.worker = None

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(0)

        # --- Header ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_label = QLabel("PDF → Markdown 변환기")
        title_label.setObjectName("titleLabel")
        title_row.addWidget(title_label)
        title_row.addStretch()
        header_layout.addLayout(title_row)

        subtitle_label = QLabel("PDF 문서를 깔끔한 Markdown 파일로 변환합니다")
        subtitle_label.setObjectName("subtitleLabel")
        header_layout.addWidget(subtitle_label)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(24)

        # --- Content Area (Splitter) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # == Left Panel ==
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 16, 0)
        left_layout.setSpacing(16)

        # Section: Input
        input_section_label = QLabel("입력")
        input_section_label.setObjectName("sectionLabel")
        left_layout.addWidget(input_section_label)

        # Drop Zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_selected)
        left_layout.addWidget(self.drop_zone)

        # File select button
        select_btn = QPushButton("📁  파일 선택")
        select_btn.setObjectName("secondaryButton")
        select_btn.clicked.connect(self._browse_file)
        left_layout.addWidget(select_btn)

        # Selected file display
        file_info_frame = QFrame()
        file_info_frame.setObjectName("card")
        file_info_layout = QVBoxLayout(file_info_frame)
        file_info_layout.setSpacing(8)

        file_label = QLabel("선택된 파일")
        file_label.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLORS['text_muted']};"
        )
        file_info_layout.addWidget(file_label)

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("PDF 파일 경로...")
        self.file_path_input.setReadOnly(True)
        file_info_layout.addWidget(self.file_path_input)

        left_layout.addWidget(file_info_frame)

        # Section: Options
        options_frame = QFrame()
        options_frame.setObjectName("card")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(12)

        options_label = QLabel("옵션")
        options_label.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLORS['text_muted']};"
        )
        options_layout.addWidget(options_label)

        self.extract_images_cb = QCheckBox("이미지 추출")
        self.extract_images_cb.setChecked(True)
        self.extract_images_cb.setToolTip("PDF에서 이미지를 추출하여 별도 파일로 저장합니다")
        options_layout.addWidget(self.extract_images_cb)

        # Output path
        output_label = QLabel("출력 경로")
        output_label.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLORS['text_muted']};"
        )
        options_layout.addWidget(output_label)

        output_row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("자동 생성 (PDF와 같은 폴더)")
        output_row.addWidget(self.output_path_input)

        output_browse_btn = QPushButton("...")
        output_browse_btn.setObjectName("iconButton")
        output_browse_btn.setToolTip("출력 폴더 선택")
        output_browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(output_browse_btn)
        options_layout.addLayout(output_row)

        left_layout.addWidget(options_frame)

        # Convert button + Progress
        self.convert_btn = QPushButton("⚡  변환 시작")
        self.convert_btn.setObjectName("primaryButton")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._start_conversion)
        left_layout.addWidget(self.convert_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        left_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("파일을 선택하면 변환을 시작할 수 있습니다")
        self.status_label.setObjectName("statusLabel")
        left_layout.addWidget(self.status_label)

        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # == Right Panel (Preview) ==
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 0, 0, 0)
        right_layout.setSpacing(12)

        preview_header = QHBoxLayout()
        preview_label = QLabel("미리보기")
        preview_label.setObjectName("sectionLabel")
        preview_header.addWidget(preview_label)
        preview_header.addStretch()

        self.copy_btn = QPushButton("📋  복사")
        self.copy_btn.setObjectName("iconButton")
        self.copy_btn.setToolTip("Markdown 내용을 클립보드에 복사합니다")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setMinimumWidth(80)
        preview_header.addWidget(self.copy_btn)

        self.save_btn = QPushButton("💾  저장")
        self.save_btn.setObjectName("iconButton")
        self.save_btn.setToolTip("다른 이름으로 저장합니다")
        self.save_btn.clicked.connect(self._save_as)
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumWidth(80)
        preview_header.addWidget(self.save_btn)

        right_layout.addLayout(preview_header)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText(
            "변환된 Markdown 내용이 여기에 표시됩니다..."
        )
        right_layout.addWidget(self.preview_text)

        # File info bar
        self.info_bar = QLabel("")
        self.info_bar.setStyleSheet(
            f"font-size: 12px; color: {COLORS['text_muted']}; padding: 4px 0;"
        )
        right_layout.addWidget(self.info_bar)

        splitter.addWidget(right_panel)

        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter, 1)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF 파일 선택", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self._on_file_selected(file_path)

    def _on_file_selected(self, file_path: str):
        self.file_path_input.setText(file_path)
        self.convert_btn.setEnabled(True)

        file_size = os.path.getsize(file_path)
        size_str = self._format_size(file_size)
        self.status_label.setText(f"✓ 파일 선택됨 — {Path(file_path).name} ({size_str})")
        self.status_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS['success']}; padding: 4px 0px;"
        )

        if not self.output_path_input.text():
            output_path = str(Path(file_path).with_suffix(".md"))
            self.output_path_input.setPlaceholderText(output_path)

    def _browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "출력 파일 저장", "", "Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith(".md"):
                file_path += ".md"
            self.output_path_input.setText(file_path)

    def _start_conversion(self):
        pdf_path = self.file_path_input.text()
        if not pdf_path:
            return

        output_path = self.output_path_input.text()
        if not output_path:
            output_path = str(Path(pdf_path).with_suffix(".md"))

        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("⏳ 변환 중...")
        self.status_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS['warning']}; padding: 4px 0px;"
        )

        self.worker = ConvertWorker(
            pdf_path, output_path, self.extract_images_cb.isChecked()
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_conversion_finished)
        self.worker.error.connect(self._on_conversion_error)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"⏳ 변환 중... ({current}/{total} 페이지)")

    def _on_conversion_finished(self, markdown_content: str):
        self.preview_text.setPlainText(markdown_content)
        self.progress_bar.setValue(100)
        self.convert_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        line_count = markdown_content.count("\n") + 1
        char_count = len(markdown_content)
        self.info_bar.setText(f"{line_count} 줄  |  {self._format_size(char_count)}")

        self.status_label.setText("✓ 변환 완료!")
        self.status_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS['success']}; padding: 4px 0px;"
        )

        self.progress_bar.setVisible(False)

    def _on_conversion_error(self, error_msg: str):
        self.status_label.setText(f"✗ 오류: {error_msg}")
        self.status_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS['error']}; padding: 4px 0px;"
        )
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _copy_to_clipboard(self):
        text = self.preview_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText("📋 클립보드에 복사되었습니다!")
            self.status_label.setStyleSheet(
                f"font-size: 13px; color: {COLORS['accent']}; padding: 4px 0px;"
            )

    def _save_as(self):
        text = self.preview_text.toPlainText()
        if not text:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Markdown 파일 저장", "", "Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith(".md"):
                file_path += ".md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_label.setText(f"✓ 저장 완료: {Path(file_path).name}")
            self.status_label.setStyleSheet(
                f"font-size: 13px; color: {COLORS['success']}; padding: 4px 0px;"
            )

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setStyleSheet(FIGMA_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
