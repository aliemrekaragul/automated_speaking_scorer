import os
import sys
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QMessageBox,
                           QTextEdit, QTabWidget, QWidget, QScrollArea)
from PyQt6.QtCore import Qt

CONFIG_FILE = 'config.json'

class SessionData:
    def __init__(self, session_id, tasks=None):
        self.session_id = session_id
        self.tasks = tasks or {}  

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Speaking Scorer Configuration")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.session_data = [] 
        self.current_session_index = 0
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        api_tab = QWidget()
        api_layout = QVBoxLayout()
        
        api_desc = QLabel("Enter your Google API Keys from https://makersuite.google.com/app/apikey")
        api_desc.setWordWrap(True)
        api_layout.addWidget(api_desc)
        
        self.key_inputs = {}
        for key_name in ['ANALYTIC_SCORING_API_KEY', 'HOLISTIC_SCORING_API_KEY', 'OFF_TOPIC_DETECTION_API_KEY']:
            key_layout = QHBoxLayout()
            key_layout.addWidget(QLabel(f"{key_name.replace('_', ' ').title()}:"))
            
            key_input = QLineEdit()
            current_key = ConfigManager.get_api_key(key_name)
            if current_key:
                key_input.setText(current_key)
            key_input.setEchoMode(QLineEdit.EchoMode.Password)
            key_layout.addWidget(key_input)
            
            show_btn = QPushButton("Show")
            show_btn.setCheckable(True)
            show_btn.clicked.connect(lambda checked, input=key_input, btn=show_btn: 
                self.toggle_key_visibility(checked, input, btn))
            key_layout.addWidget(show_btn)
            
            api_layout.addLayout(key_layout)
            self.key_inputs[key_name] = key_input
        
        api_layout.addStretch()
        api_tab.setLayout(api_layout)
        
        task_tab = QWidget()
        task_layout = QVBoxLayout()
        
        task_desc = QLabel("Define speaking tasks for each session")
        task_desc.setWordWrap(True)
        task_layout.addWidget(task_desc)
        
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous Session")
        self.next_btn = QPushButton("Next Session →")
        self.session_label = QLabel("Session 1/1")
        self.prev_btn.clicked.connect(self.show_previous_session)
        self.next_btn.clicked.connect(self.show_next_session)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.session_label)
        nav_layout.addWidget(self.next_btn)
        task_layout.addLayout(nav_layout)
        
        # Single session container
        self.current_session_container = QVBoxLayout()
        task_layout.addLayout(self.current_session_container)
        
        # Add Session button
        add_session_btn = QPushButton("+ Add Session")
        add_session_btn.clicked.connect(self.add_new_session)
        task_layout.addWidget(add_session_btn)
        
        task_tab.setLayout(task_layout)
        
        # Load initial sessions from config
        current_tasks = ConfigManager.get_task_definitions()
        if current_tasks:
            for session_id, task_data in current_tasks.items():
                try:
                    clean_task_data = task_data.rstrip(',').strip()
                    task_dict = json.loads(clean_task_data)
                    session = SessionData(session_id, task_dict)
                    self.session_data.append(session)
                except json.JSONDecodeError as e:
                    print(f"Error parsing task data for session {session_id}: {e}")
        
        self.update_navigation()
        self.show_current_session()
        
        tabs.addTab(api_tab, "API Keys")
        tabs.addTab(task_tab, "Task Definitions")
        layout.addWidget(tabs)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def toggle_key_visibility(self, checked, key_input, button):
        key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        button.setText("Hide" if checked else "Show")
    
    def get_api_keys(self):
        return {name: input.text().strip() 
                for name, input in self.key_inputs.items()}
    
    def show_current_session(self):
        while self.current_session_container.count():
            item = self.current_session_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.session_data:
            self.update_navigation()
            return
            
        session = self.session_data[self.current_session_index]
        session_frame = self.create_session_widget(session)
        self.current_session_container.addWidget(session_frame)
        
        self.update_navigation()

    def update_navigation(self):
        total_sessions = len(self.session_data)
        current_num = self.current_session_index + 1 if self.session_data else 0
        
        self.session_label.setText(f"Session {current_num}/{total_sessions}")
        self.prev_btn.setEnabled(self.current_session_index > 0)
        self.next_btn.setEnabled(self.current_session_index < total_sessions - 1)

    def show_previous_session(self):
        if self.current_session_index > 0:
            self.current_session_index -= 1
            self.show_current_session()

    def show_next_session(self):
        if self.current_session_index < len(self.session_data) - 1:
            self.current_session_index += 1
            self.show_current_session()

    def create_session_widget(self, session):
        session_frame = QWidget()
        session_layout = QVBoxLayout(session_frame)
        
        header_layout = QHBoxLayout()
        session_label = QLabel(f"Session {session.session_id}")
        header_layout.addWidget(session_label)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_session())
        header_layout.addWidget(delete_btn)
        header_layout.addStretch()
        
        session_layout.addLayout(header_layout)
        
        tasks_scroll = QScrollArea()
        tasks_scroll.setWidgetResizable(True)
        tasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        tasks_content = QWidget()
        tasks_container = QVBoxLayout(tasks_content)
        
        for task_key, task_value in session.tasks.items():
            if isinstance(task_value, str):
                task_value = task_value.replace('\\n', '\n')
            self.add_task_input(tasks_container, task_key, task_value)
        
        add_task_btn = QPushButton("+ Add Task")
        add_task_btn.clicked.connect(lambda: self.add_task_input(tasks_container))
        
        tasks_scroll.setWidget(tasks_content)
        session_layout.addWidget(tasks_scroll)
        session_layout.addWidget(add_task_btn)
        
        return session_frame

    def add_task_input(self, container, task_key=None, task_value=None):
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        
        if task_key is None:
            task_count = container.count() + 1
            task_key = f"t{task_count}"
        
        key_label = QLabel(task_key)
        key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_label.setStyleSheet("background-color: #4a5568; color: white; border-radius: 3px; padding: 4px;")
        key_label.setMaximumWidth(40) 
        
        value_input = QTextEdit()
        value_input.setPlaceholderText("Task description")
        if task_value:
            value_input.setText(task_value)
        value_input.setMaximumHeight(100)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_task(task_widget, container))
        
        task_layout.addWidget(key_label)
        task_layout.addWidget(value_input)
        task_layout.addWidget(delete_btn)
        
        container.addWidget(task_widget)
        
        value_input.setFocus()
    
    def delete_task(self, task_widget, container):
        container.removeWidget(task_widget)
        task_widget.hide()
        task_widget.deleteLater()
        
        self.renumber_tasks(container)

    def renumber_tasks(self, container):
        for i in range(container.count()):
            task_widget = container.itemAt(i).widget()
            if task_widget:
                task_layout = task_widget.layout()
                key_label = task_layout.itemAt(0).widget()
                key_label.setText(f"t{i+1}")
    
    def delete_session(self):
        if self.session_data:
            del self.session_data[self.current_session_index]
            
            if not self.session_data:
                self.current_session_index = 0
            elif self.current_session_index >= len(self.session_data):
                self.current_session_index = len(self.session_data) - 1
                
            self.show_current_session()
    
    def add_new_session(self):
        next_id = str(len(self.session_data) + 1)
        new_session = SessionData(next_id)
        self.session_data.append(new_session)
        self.current_session_index = len(self.session_data) - 1
        self.show_current_session()
    
    def get_task_definitions(self):
        tasks = {}
        
        for session in self.session_data:
            current_tasks = self.collect_current_session_tasks()
            
            if self.current_session_index < len(self.session_data):
                self.session_data[self.current_session_index].tasks = current_tasks
            
            if session.tasks:
                tasks[session.session_id] = json.dumps(session.tasks)
        
        return tasks
    
    def collect_current_session_tasks(self):
        """Collect tasks from the current UI session"""
        session_tasks = {}
        
        if self.current_session_container.count() == 0:
            return session_tasks
            
        session_frame = self.current_session_container.itemAt(0).widget()
        if not session_frame:
            return session_tasks
            
        session_layout = session_frame.layout()
        tasks_scroll = session_layout.itemAt(1).widget()
        if not tasks_scroll:
            return session_tasks
            
        tasks_content = tasks_scroll.widget()
        if not tasks_content:
            return session_tasks
            
        tasks_container = tasks_content.layout()
        
        for i in range(tasks_container.count()):
            task_widget = tasks_container.itemAt(i).widget()
            if task_widget:
                task_layout = task_widget.layout()
                key_label = task_layout.itemAt(0).widget()
                value_input = task_layout.itemAt(1).widget()
                
                task_key = key_label.text().strip()
                task_value = value_input.toPlainText().strip().replace('\n', '\\n')
                
                if task_key and task_value:
                    session_tasks[task_key] = task_value
        
        return session_tasks

class ConfigManager:
    @staticmethod
    def get_config_path():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(base_dir)  
        return os.path.join(base_dir, CONFIG_FILE)
    
    @staticmethod
    def load_config():
        config_path = ConfigManager.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_config(config):
        config_path = ConfigManager.get_config_path()
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    @staticmethod
    def get_api_key(key_name='ANALYTIC_SCORING_API_KEY'):
        config = ConfigManager.load_config()
        return config.get(key_name)
    
    @staticmethod
    def get_task_definitions():
        config = ConfigManager.load_config()
        return config.get('TASK_DEFINITIONS', {})
    
    @staticmethod
    def setup_config(parent=None):
        dialog = ConfigDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_keys = dialog.get_api_keys()
            task_definitions = dialog.get_task_definitions()
            
            if not all(api_keys.values()):
                QMessageBox.warning(
                    parent,
                    "Configuration Error",
                    "All API keys are required."
                )
                return False
            
            config = {
                **api_keys,
                'TASK_DEFINITIONS': task_definitions
            }
            ConfigManager.save_config(config)
            
            for key, value in api_keys.items():
                os.environ[key] = value
            return True
        return False 