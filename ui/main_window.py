from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
from typing import List
import asyncio
from agents.analytic_scoring_agent import AnalyticScoringAgent
from agents.holistic_scoring_agent import HolisticScoringAgent
from agents.off_topic_detection_agent import OffTopicDetectionAgent
from agents.score_adjustment_agent import ScoreAdjustmentAgent
from models.score_models import SpeakingPerformance
from utils.excel_utils import save_scores_to_excel
from utils.config_manager import ConfigManager
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QProgressBar, QTextEdit, QFileDialog, 
    QMessageBox, QGridLayout, QGroupBox,
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QCheckBox, QLabel, QProgressBar, QMessageBox,
    QTextEdit, QHBoxLayout
)
class ScoringWorker(QThread):
    progress = pyqtSignal(int, str) 
    finished = pyqtSignal(list)
    error = pyqtSignal(tuple)  
    
    def __init__(self, folder_path: str, scoring_options: dict):
        super().__init__()
        self.folder_path = folder_path
        self.scoring_options = scoring_options
        self._is_cancelled = False
        self.errors = [] 
        
    def save_error_log(self):
        """Save errors to a log file in the selected folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"error_log_{timestamp}.txt"
        log_path = os.path.join(self.folder_path, log_filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for error in self.errors:
                f.write(f"• {error}\n")
        
        return log_path
        
    def add_error(self, message):
        """Add error message to the list and emit progress update."""
        self.errors.append(message)
        self.progress.emit(0, "Error occurred")
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        try:
            audio_files = [f for f in os.listdir(self.folder_path) if f.endswith('.mp3')]
            if not audio_files:
                self.add_error("No MP3 files found in the selected folder.")
                self.error.emit((len(self.errors), self.save_error_log()))
                return
                
            performances = []
            failed_files = []
            total_files = len(audio_files)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for i, audio_file in enumerate(audio_files):
                    if self._is_cancelled:
                        self.add_error("Scoring process cancelled by user.")
                        break
                        
                    try:
                        file_path = os.path.join(self.folder_path, audio_file)
                        performance = SpeakingPerformance(
                            file_name=audio_file,
                            analytic_scores=None,
                            holistic_score=None,
                            off_topic_analysis=None,
                            adjusted_score=None
                        )
                        
                        scoring_failed = False
                        
                        if self.scoring_options['analytic']:
                            try:
                                agent = AnalyticScoringAgent()
                                performance.analytic_scores = loop.run_until_complete(
                                    agent.score_performance(file_path)
                                )
                            except Exception as e:
                                self.add_error(f"Analytic scoring failed for {audio_file}: {str(e)}")
                                scoring_failed = True
                        
                        if self.scoring_options['holistic']:
                            try:
                                agent = HolisticScoringAgent()
                                performance.holistic_score = loop.run_until_complete(
                                    agent.score_performance(file_path)
                                )
                            except Exception as e:
                                self.add_error(f"Holistic scoring failed for {audio_file}: {str(e)}")
                                scoring_failed = True
                        
                        if self.scoring_options['off_topic']:
                            try:
                                agent = OffTopicDetectionAgent()
                                performance.off_topic_analysis = loop.run_until_complete(
                                    agent.analyze_topic_relevance(file_path)
                                )
                            except Exception as e:
                                self.add_error(f"Off-topic detection failed for {audio_file}: {str(e)}")
                                scoring_failed = True
                        
                        if scoring_failed:
                            failed_files.append(audio_file)
                        else:
                            performances.append(performance)
                        
                        progress = int((i + 1) / total_files * 100)
                        self.progress.emit(progress, f"Processing: {audio_file}")
                        
                    except Exception as e:
                        self.add_error(f"Error processing {audio_file}: {str(e)}")
                        failed_files.append(audio_file)
                        continue
                
                if not self._is_cancelled and self.scoring_options['score_adjustment'] and performances:
                    try:
                        self.progress.emit(100, "Adjusting scores...")
                        agent = ScoreAdjustmentAgent()
                        performances = agent.adjust_scores(performances)
                    except Exception as e:
                        self.add_error(f"Score adjustment failed: {str(e)}")
                
            finally:
                loop.close()
            
            if self.errors:
                log_path = self.save_error_log()
                self.error.emit((len(self.errors), log_path))
            
            if performances:
                self.finished.emit(performances)
            elif not self.errors: 
                self.add_error("No performances were successfully processed.")
                log_path = self.save_error_log()
                self.error.emit((len(self.errors), log_path))
            
        except Exception as e:
            self.add_error(f"Critical error occurred: {str(e)}")
            self.error.emit((len(self.errors), self.save_error_log()))
            if 'loop' in locals() and loop is not None:
                loop.close()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOBB ETU - Automated Speaking Scorer")
        self.setMinimumSize(900, 750) 
        
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel[heading="true"] {
                font-size: 18px;
                font-weight: bold;
                color: #89b4fa;
                margin-bottom: 8px;
            }
            QCheckBox {
                color: #cdd6f4;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 1px solid #585b70;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border: 1px solid #89b4fa;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #cdd6f4;
                background-color: #45475a;
                border: none;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
            QPushButton:pressed {
                background-color: #313244;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #7f849c;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                text-align: center;
                height: 12px;
                background-color: #313244;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            QProgressBar::chunk {
                background-color: #a6e3a1;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                selection-background-color: #89b4fa;
                selection-color: #1e1e2e;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 24px;
                font-size: 15px;
                font-weight: bold;
                color: #89b4fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                left: 16px;
            }
            QFrame[separator="true"] {
                background-color: #45475a;
                min-height: 1px;
                max-height: 1px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        header_label = QLabel("Automated Speaking Scorer")
        header_label.setProperty("heading", "true")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        folder_group = QGroupBox("Audio Files")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setContentsMargins(16, 0, 16, 16)
        folder_layout.setSpacing(12)
        
        folder_section = QHBoxLayout()
        folder_section.setSpacing(12)
        
        self.select_folder_btn = QPushButton("📁 Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_folder_btn.setFixedSize(150, 40)
        self.select_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
        """)
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        
        folder_section.addWidget(self.select_folder_btn)
        folder_section.addWidget(self.folder_label, 1)
        folder_layout.addLayout(folder_section)
        
        main_layout.addWidget(folder_group)
        
        options_group = QGroupBox("Scoring Options")
        options_layout = QVBoxLayout(options_group)
        options_layout.setContentsMargins(16, 0, 16, 16)
        options_layout.setSpacing(10)
        
        options_info = QLabel("Each selection increases the scoring time:")
        options_info.setStyleSheet("color: #94e2d5; font-style: italic;")
        options_layout.addWidget(options_info)
        
        checkbox_grid = QGridLayout()
        checkbox_grid.setSpacing(16)
        
        self.analytic_checkbox = QCheckBox("Analytic Scoring")
        self.holistic_checkbox = QCheckBox("Holistic Scoring")
        self.off_topic_checkbox = QCheckBox("Off-topic Detection")
        self.score_adjustment_checkbox = QCheckBox("Score Adjustment")
        
        checkbox_grid.addWidget(self.analytic_checkbox, 0, 0)
        checkbox_grid.addWidget(self.holistic_checkbox, 0, 1)
        checkbox_grid.addWidget(self.off_topic_checkbox, 1, 0)
        checkbox_grid.addWidget(self.score_adjustment_checkbox, 1, 1)
        
        options_layout.addLayout(checkbox_grid)
        main_layout.addWidget(options_group)
        
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(16, 0, 16, 16)
        status_layout.setSpacing(12)
        
        status_row = QHBoxLayout()
        status_row.setSpacing(10)
        
        self.status_light = QLabel("⬤")
        self.status_light.setFixedSize(24, 24)
        self.status_light.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_light.setStyleSheet("color: #a6e3a1; font-size: 16px;")  # Green color
        
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("font-size: 15px;")
        
        status_row.addWidget(self.status_light)
        status_row.addWidget(self.progress_label, 1)
        status_layout.addLayout(status_row)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(status_group)
        
        summary_group = QGroupBox("Results")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setContentsMargins(16, 0, 16, 16)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setVisible(False)
        self.summary_text.setMinimumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        main_layout.addWidget(summary_group)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        
        btn_container = QWidget()
        btn_container_layout = QHBoxLayout(btn_container)
        btn_container_layout.setContentsMargins(0, 0, 0, 0)
        btn_container_layout.setSpacing(16)
        
        self.start_btn = QPushButton("Start Scoring")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_scoring)
        self.start_btn.setMinimumWidth(160)
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #7f849c;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_scoring)
        self.cancel_btn.setMinimumWidth(160)
        self.cancel_btn.setMinimumHeight(48)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #fab387;
            }
            QPushButton:pressed {
                background-color: #eba0ac;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #7f849c;
            }
        """)
        
        btn_container_layout.addStretch()
        btn_container_layout.addWidget(self.start_btn)
        btn_container_layout.addWidget(self.cancel_btn)
        btn_container_layout.addStretch()
        
        button_layout.addWidget(btn_container, 1)
        
        self.config_btn = QPushButton("⚙ Config")
        self.config_btn.setFixedSize(120, 40)
        self.config_btn.clicked.connect(self.show_config)
        self.config_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        
        button_layout.addWidget(self.config_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        main_layout.addLayout(button_layout)
        
        self.folder_path = None
        
        self.analytic_checkbox.setChecked(True)
        self.score_adjustment_checkbox.setChecked(True)
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"{folder}")
            self.start_btn.setEnabled(True)
            self.summary_text.setVisible(False)
    
    def start_scoring(self):
        if not self.folder_path:
            QMessageBox.warning(self, "Error", "Please select a folder first.")
            return
            
        scoring_options = {
            'analytic': self.analytic_checkbox.isChecked(),
            'holistic': self.holistic_checkbox.isChecked(),
            'off_topic': self.off_topic_checkbox.isChecked(),
            'score_adjustment': self.score_adjustment_checkbox.isChecked()
        }
        
        if not any(scoring_options.values()):
            QMessageBox.warning(self, "Error", "Please select at least one scoring option.")
            return
        
        self.disable_ui()
        
        self.worker = ScoringWorker(self.folder_path, scoring_options)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.scoring_finished)
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def cancel_scoring(self):
        """Cancel the scoring process."""
        if hasattr(self, 'worker'):
            self.worker.cancel()
            self.progress_label.setText("Cancelling...")
    
    def disable_ui(self):
        """Disable UI elements during scoring process."""
        self.select_folder_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.analytic_checkbox.setEnabled(False)
        self.holistic_checkbox.setEnabled(False)
        self.off_topic_checkbox.setEnabled(False)
        self.score_adjustment_checkbox.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.summary_text.clear()
        self.summary_text.setVisible(False)
    
    def enable_ui(self):
        """Enable UI elements after scoring process."""
        self.select_folder_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.analytic_checkbox.setEnabled(True)
        self.holistic_checkbox.setEnabled(True)
        self.off_topic_checkbox.setEnabled(True)
        self.score_adjustment_checkbox.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Ready")
        self.status_light.setStyleSheet("color: #a6e3a1;")  
    
    def update_progress(self, value, message):
        """Update progress bar value and message."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        if "Error" in message:
            self.status_light.setStyleSheet("color: #f38ba8;")  # Red
        elif "Processing" in message:
            self.status_light.setStyleSheet("color: #89b4fa;")  # Blue
        elif "Starting" in message:
            self.status_light.setStyleSheet("color: #fab387;")  # Orange
        elif "Ready" in message:
            self.status_light.setStyleSheet("color: #a6e3a1;")  # Green
        elif "Cancelling" in message:
            self.status_light.setStyleSheet("color: #f9e2af;")  # Yellow
    
    def generate_summary(self, performances: List[SpeakingPerformance], failed_files: List[str] = None) -> str:
        """Generate a summary of scoring results."""
        summary = []
        summary.append("=== Scoring Summary ===\n")
        
        total_attempted = len(performances) + (len(failed_files) if failed_files else 0)
        summary.append(f"Success Rate: {len(performances)} / {total_attempted}")
        if failed_files:
            summary.append(f"Failed files: {len(failed_files)}")
            summary.append("\nThere were some issues with the following files:\n")
            for file in failed_files:
                summary.append(f"  {file}\n")
        summary.append("")
        
        if any(p.off_topic_analysis for p in performances):
            off_topic_count = sum(1 for p in performances if p.off_topic_analysis and p.off_topic_analysis.is_off_topic)
            total_with_analysis = sum(1 for p in performances if p.off_topic_analysis)
            summary.append(f"\nOff-topic Analysis:")
            summary.append(f"  Off-topic Responses: {off_topic_count} out of {total_with_analysis}")
        
        return "\n".join(summary)
    
    def scoring_finished(self, performances):
        """Handle completion of scoring process."""
        try:
            failed_files = getattr(self.worker, 'failed_files', []) if hasattr(self, 'worker') else []
            
            summary = self.generate_summary(performances, failed_files)
            self.summary_text.setVisible(True)
            self.summary_text.setText(summary)
            
            filepath = save_scores_to_excel(performances, self.folder_path)
            
            if failed_files:
                message = (f"Scoring completed with {len(failed_files)} failures.\n"
                          f"Successful results saved to:\n{filepath}")
            else:
                message = f"Scoring completed successfully!\nResults saved to:\n{filepath}"
            
            QMessageBox.information(self, "Process Complete", message)
            
        except Exception as e:
            self.show_error(f"Error saving results: {str(e)}")
        
        finally:
            self.enable_ui()
    
    def show_error(self, error_info):
        """Show notification about errors and log file location."""
        error_count, log_path = error_info
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Errors Occurred")
        msg_box.setText(f"{error_count} error(s) occurred during processing.\n\n"
                       f"Error details have been saved to:\n{log_path}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()
        self.enable_ui()
    
    def show_config(self):
        """Show the configuration dialog."""
        if ConfigManager.setup_config(self):
            QMessageBox.information(
                self,
                "Configuration Saved",
                "Configuration has been updated successfully."
            )