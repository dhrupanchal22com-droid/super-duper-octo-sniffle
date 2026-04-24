"""
Main PyQt5 GUI window
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QTabWidget, QFrame, QDropEvent
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt5.QtGui import QFont, QColor, QDragEnterEvent
import logging

logger = logging.getLogger(__name__)

class ProcessingThread(QThread):
    """Background thread for file processing"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
def run(self):
        try:
            from src.core.processor import DrawingProcessor
            processor = DrawingProcessor(self.file_path)
            self.progress.emit(f"Processing {Path(self.file_path).name}...")
            analysis = processor.process()
            self.finished.emit(analysis)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Architectural Drawing Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        self.current_analysis = None
        self.current_file = None
        self.processing_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setAcceptDrops(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🏢 Architectural Drawing Analyzer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # File upload section
        upload_frame = self._create_upload_frame()
        layout.addWidget(upload_frame)
        
        # Processing progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 5px; }")
        layout.addWidget(self.progress_bar)
        
        # Tabs for results
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Export button
        export_btn = QPushButton("📊 Export to Excel")
        export_btn.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "padding: 10px; border-radius: 5px; font-size: 12px;"
        )
        export_btn.setMinimumHeight(40)
        export_btn.clicked.connect(self.export_to_excel)
        layout.addWidget(export_btn)
        
        central_widget.setLayout(layout)
        
        # Enable drag-drop
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.current_file = files[0]
            self.file_label.setText(f"Selected: {Path(self.current_file).name}")
            self.process_file()
    
    def _create_upload_frame(self) -> QFrame:
        """Create file upload frame"""
        frame = QFrame()
        frame.setStyleSheet("border: 2px solid #007bff; border-radius: 5px; padding: 10px;")
        layout = QHBoxLayout()
        
        upload_btn = QPushButton("📁 Select Drawing File")
        upload_btn.setStyleSheet(
            "background-color: #007bff; color: white; font-weight: bold; "
            "padding: 10px; border-radius: 5px; font-size: 12px;"
        )
        upload_btn.setMinimumHeight(40)
        upload_btn.clicked.connect(self.select_file)
        layout.addWidget(upload_btn)
        
        self.file_label = QLabel("No file selected (or drag & drop)")
        self.file_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.file_label)
        
        layout.addStretch()
        
        process_btn = QPushButton("⚙️ Process Drawing")
        process_btn.setStyleSheet(
            "background-color: #ffc107; color: black; font-weight: bold; "
            "padding: 10px; border-radius: 5px; font-size: 12px;"
        )
        process_btn.setMinimumHeight(40)
        process_btn.clicked.connect(self.process_file)
        layout.addWidget(process_btn)
        
        frame.setLayout(layout)
        return frame
    
    def select_file(self):
        """Select file dialog""" 
        file_types = (
            "Drawing Files (*.dwg *.pdf *.png *.jpg *.jpeg);;"
            "DWG Files (*.dwg);;"
            "PDF Files (*.pdf);;"
            "Image Files (*.png *.jpg *.jpeg);;"
            "All Files (*)"
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Drawing File", "", file_types
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.setText(f"Selected: {Path(file_path).name}")
    
    def process_file(self):
        """Process selected file"""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.processing_thread = ProcessingThread(self.current_file)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()
    
    def update_progress(self, message: str):
        """Update progress message"""
        current = self.progress_bar.value()
        if current < 90:
            self.progress_bar.setValue(current + 10)
    
    def on_processing_finished(self, analysis):
        """Handle processing completion"""
        self.current_analysis = analysis
        self.progress_bar.setValue(100)
        
        # Display results
        self._display_results(analysis)
        
        QMessageBox.information(
            self, "Success",
            f"Processing complete!\n\n"
            f"Detected:\n"
            f"• {len(analysis.windows)} windows\n"
            f"• {len(analysis.doors)} doors\n\n"
            f"Processing Time: {analysis.processing_time_seconds:.2f}s"
        )
    
    def on_processing_error(self, error_msg: str):
        """Handle processing error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_msg}")
    
    def _display_results(self, analysis):
        """Display analysis results in tabs"""
        # Clear existing tabs
        self.tabs.clear()
        
        # Summary tab
        summary_table = self._create_summary_table(analysis)
        self.tabs.addTab(summary_table, "📊 Summary")
        
        # Windows tab
        windows_table = self._create_results_table(analysis.windows)
        self.tabs.addTab(windows_table, f"🪟 Windows ({len(analysis.windows)})")
        
        # Doors tab
        doors_table = self._create_results_table(analysis.doors)
        self.tabs.addTab(doors_table, f"🚪 Doors ({len(analysis.doors)})")
    
    def _create_summary_table(self, analysis) -> QTableWidget:
        """Create summary table"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        
        summary_data = [
            ("File Name", analysis.file_name),
            ("File Type", analysis.file_type),
            ("Status", analysis.status),
            ("Processing Time (s)", f"{analysis.processing_time_seconds:.2f}"),
            ("Detected Scale", f"{analysis.detected_scale} mm/unit"),
            ("Total Windows", str(len(analysis.windows))),
            ("Total Doors", str(len(analysis.doors))),
            ("Analysis Timestamp", str(analysis.analysis_timestamp)[:19]),
        ]
        
        table.setRowCount(len(summary_data))
        for row_idx, (prop, value) in enumerate(summary_data):
            table.setItem(row_idx, 0, QTableWidgetItem(prop))
            table.setItem(row_idx, 1, QTableWidgetItem(value))
        
        table.resizeColumnsToContents()
        return table
    
    def _create_results_table(self, items) -> QTableWidget:
        """Create results table"""
        table = QTableWidget()
        
        if not items:
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem("No items detected"))
            return table
        
        headers = list(items[0].to_dict().keys())
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            item_dict = item.to_dict()
            for col_idx, value in enumerate(item_dict.values()):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        
        table.resizeColumnsToContents()
        return table
    
    def export_to_excel(self):
        """Export results to Excel"""
        if not self.current_analysis:
            QMessageBox.warning(self, "Warning", "No analysis to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                from src.export.excel_generator import ExcelGenerator
                
                generator = ExcelGenerator(file_path)
                generator.create_summary_sheet(self.current_analysis)
                generator.create_windows_sheet(self.current_analysis.windows)
                generator.create_doors_sheet(self.current_analysis.doors)
                
                if generator.save():
                    QMessageBox.information(self, "Success", f"Excel file saved:\n{file_path}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save Excel file!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

def main():
    app = __import__('PyQt5.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()