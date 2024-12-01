import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image
from datetime import datetime


class WeatherPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.api_key = '30d4741c779ba94c470ca1f63045390a'
        self.colors = {
            'background': '#F0F4F8',  # Xám nhạt, tạo cảm giác không gian mở và sạch sẽ
            'primary': 'transparent',  # Nền trắng chính, tạo độ tương phản và sáng sủa
            'secondary': '#E6EAF0',  # Xám blue-tint nhẹ cho các phần phụ
            'accent': '#2196F3',  # Xanh dương (material design) - tượng trưng cho bầu trời
            'text_primary': '#2C3E50',  # Xanh navy đậm cho văn bản chính - dễ đọc
            'text_secondary': '#546E7A'  # Xám blue-grey nhạt cho văn bản phụ
        }
        self.configure(
            width=400,
            height=850,
            corner_radius = 20,
            fg_color=self.colors['background']
        )
        self.content_frame = None
        self._init_components()


    def _init_components(self):
        self.clock_label = self._create_clock()

        self.public_ip = self._get_public_ip()
        self.location_info = self._get_location_info()
        self.current_location = self.location_info.get('city', 'Unknown')

        self._create_location_input()
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent", width=350, height=450)
        self.content_frame.pack()

        self.show_weather(self.current_location)

    def _get_public_ip(self):
        try:
            response = requests.get("https://api64.ipify.org?format=json", timeout=5)
            return response.json().get("ip", None)
        except requests.RequestException:
            return None


    def _get_location_info(self):
        try:
            response = requests.get('http://ipinfo.io/json', timeout=5)
            data = response.json()

            city = data.get('city', 'Unknown')
            country = data.get('country', 'Unknown')

            return {"city": city, "country": country}
        except requests.RequestException as e:
            print(f"Error retrieving location: {e}")
            return {"city": "New York", "country": "US"}

    def _create_clock(self):
        clock_label = ctk.CTkLabel(
            self,
            width=60,
            height=50,
            font=('digital-7', 32),
            text_color=self.colors['accent'],
            fg_color="transparent"
        )
        clock_label.place(x=10, y=10)
        self._update_clock(clock_label)
        return clock_label

    def _update_clock(self, label):
        current_time = datetime.now()
        time_string = current_time.strftime("%I:%M:%S %p")
        label.configure(text=time_string)
        self.after(10, lambda: self._update_clock(label))

    def _create_location_input(self):
        input_frame = ctk.CTkFrame(
            self,
            width=350,
            height=250,
            corner_radius=25,
            fg_color= "transparent"
        )
        input_frame.pack(side = "bottom")

        location_label = ctk.CTkLabel(
            input_frame,
            text="Vị trí khác",
            font=('Roboto', 20, 'bold'),
            text_color=self.colors['text_primary']
        )
        location_label.pack(pady=10)

        self.location_textbox = ctk.CTkTextbox(
            input_frame,
            width=300,
            height=40,
            corner_radius=20,
            fg_color="transparent",
            text_color=self.colors['text_primary'],
            font=("Roboto", 16),
            border_width=2,
            border_color=self.colors['accent'],
            activate_scrollbars=False
        )
        self.location_textbox.bind("<Return>", self._handle_location_entry)
        self.location_textbox.pack(pady=10)

        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ok_button = ctk.CTkButton(
            button_frame,
            width=120,
            font=("Roboto", 15, 'bold'),
            text="Search",
            command=self._show_weather_for_location,
            corner_radius=20,
            fg_color=self.colors['accent'],
            hover_color='#2980B9',
            text_color=self.colors['text_primary']
        )
        ok_button.pack(side="left", padx=10)

        forecast_button = ctk.CTkButton(
            button_frame,
            width=120,
            text="Xem thêm",
            command=self._show_extended_forecast,
            font= ("Roboto", 15, 'bold'),
            corner_radius=20,
            fg_color=self.colors['accent'],
            hover_color='#2980B9',
            text_color=self.colors['text_primary']
        )
        forecast_button.pack(side="left", padx=10)

    def _handle_location_entry(self, event):
        if event.keysym == "Return":
            self._show_weather_for_location()

    def _show_weather_for_location(self):
        location = self.location_textbox.get("1.0", ctk.END).strip()
        if location:
            self.show_weather(location)
            self.location_textbox.delete("1.0", ctk.END)

    def show_weather(self, location):
        self._clear_content()
        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={self.api_key}",
                timeout=5
            )
            response.raise_for_status()
            weather_data = response.json()

            temp = round(weather_data['main']['temp'])
            temp_max = round(weather_data['main']['temp_max'])
            temp_min = round(weather_data['main']['temp_min'])
            description = weather_data['weather'][0]['main']
            humidity = weather_data['main']['humidity']
            visibility = weather_data.get('visibility', 0) // 1000
            wind_speed = weather_data['wind']['speed']

            self._display_weather_icon(description)

            details_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color=self.colors['primary'],
                corner_radius=25
            )
            details_frame.pack(pady=20)
            location_label = ctk.CTkLabel(
                details_frame,
                text=f"{location.title()}",
                font=('Roboto', 40, 'bold'),
                text_color=self.colors['text_primary']
            )
            location_label.pack(pady=20)

            temp_label = ctk.CTkLabel(
                details_frame,
                text=f"{temp}°C",
                font=('Roboto', 40, 'bold'),
                text_color=self.colors['accent']
            )
            temp_label.pack(pady=10)

            detail_icons_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color="transparent"
            )
            detail_icons_frame.pack(pady=20, fill="x", expand=True)

            icon_details = [
                ("Icon/temperature.png", f"{temp}°C"),
                ("Icon/temperaturerange.png", f"{temp_max}°C / {temp_min}°C"),
                ("Icon/weather.png", description),
                ("Icon/humidity.png", f"{humidity}%"),
                ("Icon/visibility.png", f"{visibility} km"),
                ("Icon/windSpeed.png", f"{wind_speed} m/s")
            ]

            for icon_path, text in icon_details:
                self._load_compact_icon(detail_icons_frame, icon_path, text)

            self.current_location = location
        except Exception as e:
            messagebox.showerror("Weather Error", str(e))

    def _load_compact_icon(self, parent_frame, icon_path, text):
        try:
            image = Image.open(icon_path)
            picture = ctk.CTkImage(dark_image=image, light_image=image, size=(40, 40))

            icon_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            icon_frame.pack(side="left", padx=10, expand=True)

            icon_label = ctk.CTkLabel(icon_frame, image=picture, text="")
            icon_label.pack()

            text_label = ctk.CTkLabel(
                icon_frame,
                text=text,
                font=("Roboto", 16),
                text_color="black"
            )
            text_label.pack()
        except Exception as e:
            print(f"Icon loading error: {e}")

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    def _display_weather_icon(self, description):
        icon_paths = {
            'Clear': "Icon/clear.png",
            'Clouds': "Icon/cloud.png",
            'Rain': "Icon/rain.png",
            'Snow': "Icon/snow.png",
            'Thunderstorm': "Icon/storm.png"
        }
        icon_path = icon_paths.get(description, "Icon/clear.png")
        icon_size = (250, 250)
        try:
            image = Image.open(icon_path)
            picture = ctk.CTkImage(dark_image=image, light_image=image, size=icon_size)
            icon_label = ctk.CTkLabel(self.content_frame, image=picture, text="")
            icon_label.pack()
        except Exception as e:
            print(f"Icon error: {e}")

    def _show_extended_forecast(self):
        try:
            self._clear_content()

            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={self.current_location}&units=metric&APPID={self.api_key}",
                timeout=5
            )
            response.raise_for_status()
            forecast_data = response.json()

            ctk.CTkLabel(
                self.content_frame,
                text=f"Dự báo thời tiết 5 ngày tới: {self.current_location}",
                font=('Roboto', 20, 'bold'),
                text_color='black'
            ).pack(pady=10)

            daily_forecasts = {}
            for forecast in forecast_data['list']:
                date = forecast['dt_txt'].split()[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(forecast)

            forecast_frame = ctk.CTkScrollableFrame(
                self.content_frame,
                width=350,
                height=400,
                fg_color=self.colors['primary'],
                corner_radius=25
            )
            forecast_frame.pack(pady=10)

            for date, forecasts in list(daily_forecasts.items())[:5]:
                midday_forecast = min(forecasts, key=lambda x: abs(int(x['dt_txt'].split()[1].split(':')[0]) - 12))

                forecast_item = ctk.CTkFrame(forecast_frame, fg_color="#f5f7fa",  width=300)
                forecast_item.pack(pady=5, fill="x")

                ctk.CTkLabel(
                    forecast_item,
                    text=datetime.strptime(date, "%Y-%m-%d").strftime("%B %d"),
                    font=('Roboto', 16, 'bold'),
                    text_color='#30cfd0'
                ).pack(pady=5)

                description = midday_forecast['weather'][0]['main']
                icon_paths = {
                    'Clear': "Icon/clear.png",
                    'Clouds': "Icon/cloud.png",
                    'Rain': "Icon/rain.png",
                    'Snow': "Icon/snow.png",
                    'Thunderstorm': "Icon/storm.png"
                }
                icon_path = icon_paths.get(description, "Icon/clear.png")

                image = Image.open(icon_path)
                picture = ctk.CTkImage(dark_image=image, light_image=image, size=(100, 100))
                icon_label = ctk.CTkLabel(forecast_item, image=picture, text="")
                icon_label.pack(pady=5)

                ctk.CTkLabel(
                    forecast_item,
                    text=f"{midday_forecast['main']['temp']:.1f}°C",
                    font=('Roboto', 20)
                ).pack()

                ctk.CTkLabel(
                    forecast_item,
                    text=description,
                    font=('Roboto', 14)
                ).pack(pady=5)

            back_button = ctk.CTkButton(
                self.content_frame,
                text="Back",
                command=lambda: self.show_weather(self.current_location)
            )
            back_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Forecast Error", str(e))

    def load_icon(self, icon_path, text):
        try:
            image = Image.open(icon_path)
            picture = ctk.CTkImage(dark_image=image, light_image=image, size=(60, 60))
            icon_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            icon_frame.pack(side="right", padx=10)

            icon_label = ctk.CTkLabel(icon_frame, image=picture, text="")
            icon_label.pack()

            text_label = ctk.CTkLabel(
                icon_frame,
                text=text,
                font=("Roboto", 16),
                text_color="black"
            )
            text_label.pack()
        except Exception as e:
            print(f"Icon loading error: {e}")
