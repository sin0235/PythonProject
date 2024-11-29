from typing import Any
from NewsPanel import *
from SchedulePanel import *
from WeatherForecastPanel import *



class ApplicationConfig:
    DEFAULT_CONFIG = {
        "appearance_mode": "light",
        "color_theme": "blue",
        "window_size": {"width": 1400, "height": 900},
        "news_sources": {
            "Giải trí": [
                {"name": "VnExpress", "url": "https://vnexpress.net/rss/giai-tri.rss"},
                {"name": "Dân Trí", "url": "https://dantri.com.vn/giai-tri.rss"}
            ],
            "Thể thao": [
                {"name": "VnExpress", "url": "https://vnexpress.net/rss/the-thao.rss"},
                {"name": "Tuổi Trẻ", "url": "https://tuoitre.vn/rss/the-thao.rss"}
            ],
            "Công nghệ": [
                {"name": "VnExpress", "url": "https://vnexpress.net/rss/so-hoa.rss"},
                {"name": "ICTNews", "url": "https://ictnews.vietnamnet.vn/rss/cong-nghe.rss"}
            ],
            "Kinh tế": [
                {"name": "VnExpress", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
                {"name": "Dân Trí", "url": "https://dantri.com.vn/kinh-doanh.rss"}
            ],
            "Chính trị": [
                {"name": "VnExpress", "url": "https://vnexpress.net/rss/thoi-su.rss"},
                {"name": "Tuổi Trẻ", "url": "https://tuoitre.vn/rss/thoi-su.rss"}
            ]
        },
        "api_keys": {
            "weather": "",
            "news": ""
        },
        "gradient_colors": {
            "Giải trí": ("#FF69B4", "#FF1493"),  # Màu hồng rực rỡ
            "Thể thao": ("#4CAF50", "#2E7D32"),  # Xanh lá mạnh mẽ
            "Công nghệ": ("#2196F3", "#1976D2"),  # Xanh dương sáng
            "Kinh tế": ("#9C27B0", "#673AB7"),  # Tím quyền lực
            "Chính trị": ("#FF5722", "#F44336")  # Cam đỏ nổi bật
        }
    }

    @staticmethod
    def load_config(config_path: str = 'app_config.json') -> dict[str, Any]:
        try:
            if not os.path.exists(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(ApplicationConfig.DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
                return ApplicationConfig.DEFAULT_CONFIG

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            merged_config = {**ApplicationConfig.DEFAULT_CONFIG, **config}
            return merged_config

        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Configuration load error: {e}")
            return ApplicationConfig.DEFAULT_CONFIG

class FunctionExecute:

    def __init__(self):
        self.setup_logging()

        self.config = ApplicationConfig.load_config()

        self.setup_main_window()

        self.create_layout()

        self.initialize_panels()

    def setup_logging(self):
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def setup_main_window(self):
        ctk.set_appearance_mode(self.config.get('appearance_mode', 'light'))
        ctk.set_default_color_theme(self.config.get('color_theme', 'blue'))

        self.root = ctk.CTk()
        self.root.title("Ứng dụng xà lơ")

        window_size = self.config.get('window_size', {'width': 1400, 'height': 900})
        self.root.geometry(f"{window_size['width']}x{window_size['height']}")
        self.root.minsize(1100, 700)

        self.root.iconbitmap('bieuTuong.ico')

    def create_layout(self):
        self.main_container = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=15,
            fg_color="#FFFFFF"
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=250,
            corner_radius=15,
            fg_color="#F0F2F5"
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="App gì gì đó",
            font=("Arial", 22, "bold"),
            text_color="#2C3E50"
        )
        logo_label.pack(pady=(30, 40))

        nav_items = [
            {"category": "Thông Tin", "items": [
                {"name": "Tin Tức", "icon": "📰", "color": "#2980B9", "method": self.show_news_panel},
                {"name": "Thời Tiết", "icon": "☔", "color": "#27AE60", "method": self.show_weather_panel}
            ]},
            {"category": "Quản Lý", "items": [
                {"name": "Lịch Trình", "icon": "📅", "color": "#8E44AD", "method": self.show_schedule_panel}
            ]},
            {"category": "Hệ Thống", "items": [
                {"name": "Cài Đặt", "icon": "⚙️", "color": "#F39C12", "method": self.show_settings_panel}
            ]}
        ]

        for section in nav_items:
            category_label = ctk.CTkLabel(
                self.sidebar,
                text=section["category"],
                font=("Arial", 15, "bold"),
                text_color="#34495E"
            )
            category_label.pack(pady=(15, 10), anchor="w", padx=20)

            for item in section["items"]:
                button = ctk.CTkButton(
                    self.sidebar,
                    text=f"{item['icon']} {item['name']}",
                    command=item['method'],
                    corner_radius=12,
                    hover_color=item['color'],
                    fg_color="transparent",
                    border_width=2,
                    border_color=item['color'],
                    text_color=item['color'],
                    font=("Arial", 15, "bold"),
                    anchor="w",
                    width=210
                )

                button.pack(pady=5, padx=10)

    def initialize_panels(self):

        panel_classes = {
            'news': self.create_news_panel,
            'weather': self.create_weather_panel,
            'schedule': self.create_schedule_panel,
            'settings': self.create_settings_panel
        }

        self.panels = {}
        for name, creator in panel_classes.items():
            self.panels[name] = creator()

        self.show_panel('news')

    def create_panel_frame(self):
        return ctk.CTkFrame(
            self.content_frame,
            corner_radius=15,
            fg_color="#FFFFFF"
        )

    def create_news_panel(self):
        panel = NewsPanel(self.content_frame, self.config["news_sources"], self.config["gradient_colors"])
        return panel

    def create_weather_panel(self):
        panel = WeatherPanel(self.content_frame)
        return panel

    def create_schedule_panel(self):
        panel = CalendarPanel(self.content_frame)
        return panel

    def create_settings_panel(self):
        panel = self.create_panel_frame()
        title_label = ctk.CTkLabel(
            panel,
            text="Cài Đặt Ứng Dụng",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        return panel

    def show_panel(self, panel_name: str):
        for name, panel in self.panels.items():
            panel.pack_forget() if name != panel_name else panel.pack(fill="both", expand=True)

    def show_news_panel(self):
        self.show_panel('news')

    def show_weather_panel(self):
        self.show_panel('weather')

    def show_schedule_panel(self):
        self.show_panel('schedule')

    def show_settings_panel(self):
        self.show_panel('settings')

    def run(self):
        try:
            logging.info("Application started successfully")
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Application runtime error: {e}")
            messagebox.showerror("Lỗi Ứng Dụng", str(e))
        finally:
            logging.info("Application closed")



def main():
    app = FunctionExecute()
    app.run()


if __name__ == "__main__":
    main()