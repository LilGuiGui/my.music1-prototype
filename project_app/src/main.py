import sys
import os
import time
import json

from PyQt6.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QWidget,
                             QVBoxLayout, 
                             QPushButton, 
                             QStackedWidget, 
                             QSizePolicy,
                             QHBoxLayout, 
                             QLabel, 
                             QLineEdit,
                             QListWidget,
                             QComboBox, 
                             QFrame,
                             QProgressBar)

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QUrl, QSize

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from credentials import read_spotify_credentials
from reco import get_spotify_recommendations_based_on_genre, get_spotify_recommendations_based_on_artist,find_genre, find_closest_match,load_genre
from download import download_interface
from makedir import check_dir

def load_username():
    get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))        
    path_config = os.path.join (get_path, "config", "username.json")

    with open(path_config, 'r') as file:
        data = json.load(file)
    return data.get("username", "Guest")

class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(80)  # AdjustLATER

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        username = load_username()
        state = self.checktime()

        user_container = QLabel(f"Good {state}, {username}")
        user_container.setStyleSheet("font-size: 10px; font-weight: bold; color: gray;")

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Home")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        self.subtitle_label = QLabel("Get recommendation Based on Genre or Artist You like!")
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #CCCCCC;")
        
        title_layout.addWidget(user_container)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        layout.addWidget(title_container, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(0) 
        
        self.setStyleSheet("""
            HeaderWidget {
                background-color: rgb(48,52,60);
            }
        """)

    def checktime(self):
            hour = int(time.strftime("%H"))

            if 5 <= hour < 11:
                state = "morning"
            elif 11 <= hour < 15:
                state = "afternoon"
            elif 15 <= hour < 18:
                state = "evening"
            else:
                state = "night"
            return state
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyMusicOne 1.0")
        self.setGeometry(640, 480, 640, 480)
        self.setStyleSheet("background-color: rgb(48,52,60);") 

        #load api
        client_id, client_secret = read_spotify_credentials()
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

        #media loader
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.genres = load_genre()
        self.network_manager = QNetworkAccessManager()

        main_layout = QVBoxLayout()
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        #sd
        sidebar = QWidget()
        sidebar.setFixedWidth(90)
        sidebar.setStyleSheet("background-color: rgb(27, 29, 35); margin: 0; padding: 0;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        content_layout.addWidget(sidebar)

        self.load_icons()
                
        #home button
        home_btn = QPushButton(self)
        home_btn.setIcon(QIcon(self.home_icon_path))
        home_btn.setIconSize(QSize(24, 24))
        home_btn.setFlat(True)
        home_btn.setStyleSheet(f"""
            QPushButton {{
                padding: {20}px;
                margin: {20}px;
                border: none;
            }}
        """)

        #download button
        download_btn = QPushButton(self)
        download_btn.setIcon(QIcon(self.download_icon_path))
        download_btn.setIconSize(QSize(24, 24))
        download_btn.setFlat(True)
        download_btn.setStyleSheet(f"""
            QPushButton {{
                padding: {20}px;
                margin: {20}px;
                border: none;
            }}
        """)

        #settings button
        settings_btn = QPushButton(self)
        settings_btn.setIcon(QIcon(self.settings_icon_path))
        settings_btn.setIconSize(QSize(24, 24))
        settings_btn.setFlat(True)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                padding: {10}px;
                margin: {10}px;
                border: none;
            }}
        """)

        sidebar_layout.addWidget(home_btn)
        sidebar_layout.addWidget(download_btn)
        sidebar_layout.addStretch(1)
        sidebar_layout.addWidget(settings_btn)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)

        #page
        self.home_page = QWidget()
        self.download_page = QWidget()
        self.settings_page = QWidget()

        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.download_page)
        self.content_stack.addWidget(self.settings_page)

        # Signals
        home_btn.clicked.connect(lambda: self.show_page(0))
        download_btn.clicked.connect(lambda: self.show_page(1))
        settings_btn.clicked.connect(lambda: self.show_page(2))

        self.setup_home_page()
        self.setup_download_page()
        self.setup_settings_page()

        self.recommendations = []
        self.current_index = 0

    def load_icons(self):
        self.get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.home_icon_path = os.path.join(self.get_path, "icon", "home.png")
        self.download_icon_path = os.path.join(self.get_path, "icon", "download.png")
        self.settings_icon_path = os.path.join(self.get_path, "icon", "settings.png")
        self.search_icon_path = os.path.join(self.get_path, "icon", "search.png")
        
        self.spotify_icon_path = os.path.join(self.get_path, "icon", "spotify.png")
        self.youtube_icon_path = os.path.join(self.get_path, "icon", "youtube.png")
        self.downloadbtn_icon_path = os.path.join(self.get_path, "icon", "downloadbtn.png")
        self.refresh_icon_path = os.path.join(self.get_path, "icon", "refresh.png")

    def show_page(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 0:
            self.header.title_label.setText("Home")
            self.header.subtitle_label.setText("Get recommendation Based on Genre or Artist You like!")
        elif index == 1:
            self.header.title_label.setText("Downloads")
            self.header.subtitle_label.setText("Download Any Songs you like From Youtube or Spotify!")
        elif index == 2:
            self.header.title_label.setText("Settings")
            self.header.subtitle_label.setText("build later")

    def setup_home_page(self):
        mainlayout = QVBoxLayout(self.home_page)
        mainlayout.setSpacing(20)
        mainlayout.setContentsMargins(20, 20, 20, 20)

        search_layout = QHBoxLayout()
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Genre", "Artist"])
        self.search_type.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        
        search_widget = QWidget()
        search_widget.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 5px;
        """)
        search_input_layout = QHBoxLayout(search_widget)
        search_input_layout.setContentsMargins(0, 0, 0, 0)
        search_input_layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("HOYO-MiX")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 8px;
                color: white;
            }
        """)
        
        search_button = QPushButton()
        search_button.setIcon(QIcon(self.search_icon_path))
        search_button.setIconSize(QSize(24, 24))
        search_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
            }
        """)
        search_button.clicked.connect(self.get_recommendations)
        
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            color: #FF6B6B;
            font-size: 12px;
            padding: 5px;
        """)

        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(search_button)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_widget)
        mainlayout.addLayout(search_layout)
        mainlayout.addWidget(self.message_label)

        # Cover image 
        image_nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet("font-size: 24px; color: white; background: none; border: none;")
        self.prev_button.clicked.connect(self.show_previous)
        
        self.cover_image = QLabel()
        self.cover_image.setFixedSize(300, 300)
        self.cover_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_image.setStyleSheet("background-color: #2a2a2a; color: white;")
        self.cover_image.setText("SONG\nCOVER")
        
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet("font-size: 24px; color: white; background: none; border: none;")
        self.next_button.clicked.connect(self.show_next)
        
        image_nav_layout.addWidget(self.prev_button)
        image_nav_layout.addWidget(self.cover_image)
        image_nav_layout.addWidget(self.next_button)
        
        mainlayout.addLayout(image_nav_layout)

        self.track_info = QLabel("Artist")
        self.track_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_info.setStyleSheet("font-size: 24px; color: white;")
        mainlayout.addWidget(self.track_info)

        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton("PREVIEW")
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 10px 20px;
            }
        """)
        self.play_button.clicked.connect(self.play_preview)
        
        self.download_button = QPushButton("Download Me!")
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 10px 20px;
            }
        """)
        self.download_button.clicked.connect(self.download_current_track)
        
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.download_button)
        
        mainlayout.addLayout(button_layout)
        mainlayout.addStretch(1)

    def setup_download_page(self):
        layout = QVBoxLayout(self.download_page)
        download_button = QPushButton("Download Music")
        download_button.clicked.connect(self.download_music)
        layout.addWidget(download_button)

    def setup_settings_page(self):
        layout = QVBoxLayout(self.settings_page)
        layout.addWidget(QLabel("implemetn me"))

    def get_recommendations(self):
        search_term = self.search_input.text().strip()
        search_type = self.search_type.currentText()

        if not search_term:
            self.message_label.setText("Please enter a search term.")
            return

        if search_type == "Genre":
            genre = find_genre(self.genres, search_term)
            if genre != search_term:
                matches = find_closest_match(self.genres, search_term)
                if matches:
                    self.message_label.setText(f"Do you mean {', '.join(matches)}?")
                    return
                else:
                    self.message_label.setText("No matching genre exist in the database!")
                    return
            else:
                self.message_label.setText("") 
            self.recommendations = get_spotify_recommendations_based_on_genre(genre)
        else: 
            self.message_label.setText("")
            self.recommendations = get_spotify_recommendations_based_on_artist(search_term)
        
        self.current_index = 0
        self.update_display()

    def update_display(self):
        if self.recommendations:
            track = self.recommendations[self.current_index]
            self.track_info.setText(f"{track['name']}\n{track['artist']}")
            self.load_cover_image(track['album_cover'])
            self.message_label.setText("")
        else:
            self.track_info.setText("No recommendations found")
            self.cover_image.clear()
            self.message_label.setText("No recommendations found for the given input.")

    def update_display(self):
        if self.recommendations:
            track = self.recommendations[self.current_index]
            self.track_info.setText(f"{track['name']} by {track['artist']}")
            self.load_cover_image(track['album_cover'])

    def load_cover_image(self, url):
        if url:
            request = QNetworkRequest(QUrl(url))
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda: self.set_cover_image(reply))
        else:
            self.cover_image.clear()

    def set_cover_image(self, reply):
        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            self.cover_image.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.cover_image.clear() #if fail

    def show_previous(self):
        if self.recommendations:
            self.current_index = (self.current_index - 1) % len(self.recommendations)
            self.update_display()

    def show_next(self):
        if self.recommendations:
            self.current_index = (self.current_index + 1) % len(self.recommendations)
            self.update_display()

    def play_preview(self):
        if self.recommendations:
            track = self.recommendations[self.current_index]
            preview_url = track['preview_url']
            if preview_url:
                self.player.setSource(QUrl(preview_url))
                self.player.play()
            else:
                self.track_info.setText("No preview available for this track")
    
    def download_current_track(self):
        if self.recommendations:
            track = self.recommendations[self.current_index]
            url = track['url']
        
        from makedir import check_dir
        download_path = check_dir()
        
        if download_path:
            try:
                from download import download_spotify
                download_spotify(url, download_path)
                self.track_info.setText(f"Downloaded: {track['name']} by {track['artist']}")
            except Exception as e:
                self.track_info.setText(f"Download failed: {str(e)}")
        else:
            self.track_info.setText("Failed to create download directory")

    def setup_download_page(self):
        layout = QVBoxLayout(self.download_page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        platform_layout = QHBoxLayout()
        platform_label = QLabel("Platform:")
        platform_label.setStyleSheet("color: white;")
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Youtube", "Spotify"])
        self.platform_combo.setItemIcon(0, QIcon(self.youtube_icon_path))
        self.platform_combo.setItemIcon(1, QIcon(self.spotify_icon_path))
        self.platform_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo)

        # URL input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()

        self.update_placeholder()

        url_layout.addWidget(self.url_input)
        layout.addLayout(platform_layout)
        layout.addLayout(url_layout)

        self.platform_combo.currentTextChanged.connect(self.update_placeholder)

        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 8px;
            }
        """)

        download_button = QPushButton()
        download_button.setIcon(QIcon(self.downloadbtn_icon_path))
        download_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px 16px;
            }
        """)

        download_button.clicked.connect(self.start_download)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(download_button)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(self.warning_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 10px;
            }
        """)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: white;")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        downloaded_songs_label = QLabel("Your Downloaded Songs:")
        downloaded_songs_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.downloaded_songs_list = QListWidget()
        self.downloaded_songs_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 8px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3a3a3a;
            }
        """)
        
        
        refresh_button = QPushButton("Refresh List")
        refresh_button.setIcon(QIcon(self.refresh_icon_path))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        self.update_downloaded_songs_list()
        refresh_button.clicked.connect(self.update_downloaded_songs_list)
        
        layout.addLayout(platform_layout)
        layout.addLayout(url_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        layout.addWidget(separator)

        layout.addWidget(downloaded_songs_label)
        layout.addWidget(refresh_button)
        layout.addWidget(self.downloaded_songs_list)

    def update_placeholder(self):
        if self.platform_combo.currentText() == "Spotify":
            self.url_input.setPlaceholderText("https://open.spotify.com/track/12mJ5Du7ETzuywCYmKCrhg?si=823ac99e14944526")
        else:
            self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=QSJZyx8Sdxk")

    def start_download(self):
        url = self.url_input.text().strip()
        platform = self.platform_combo.currentText()

        if not url:
            self.warning_label.setText("URL Field must not BE EMPTY!")
            return

        if platform == "YouTube" and "youtube.com" not in url:
            self.warning_label.setText("Invalid YouTube URL.")
            return
        elif platform == "Spotify" and "spotify.com" not in url:
            self.warning_label.setText("Invalid Spotify URL.")
            return

        self.warning_label.setText("")
        self.status_label.setText("Begin Downloading")
        self.progress_bar.setValue(0)

        try:
            download_interface(url, platform, self.update_progress)
            self.status_label.setText("Download success!")
        except Exception as e:
            self.status_label.setText(f"Err: {str(e)}")

        self.progress_bar.setValue(100)

    def update_progress(self, percent, status):
        if isinstance(percent, (int, float)):
            self.progress_bar.setValue(int(percent))
        self.status_label.setText(status)

    def update_downloaded_songs_list(self):
        self.downloaded_songs_list.clear()
        download_path = check_dir()
        if download_path is not None:
            try:
                files = os.listdir(download_path)
                for file in files:
                    if file.endswith(('.mp3')):
                        self.downloaded_songs_list.addItem(file)
            except Exception as e:
                self.downloaded_songs_list.addItem(f"Err directory: {str(e)}")
        else:
            self.downloaded_songs_list.QLabel("You havent downloaded Any Songs!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())