import customtkinter as ctk
from tkinter import messagebox
import requests
from datetime import datetime, timedelta

api_key = '30d4741c779ba94c470ca1f63045390a'  # Thay bằng API key của bạn

class WeatherForecast:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.geometry("1028x720+300+50")
        self.root.title("Weather Forecast")

        self.frame = ctk.CTkFrame(master=self.root, width=300, height=500, corner_radius=15)
        self.frame.place(x=50, y=20)

        # Forecast Table
        self.forecast_frame = ctk.CTkFrame(master=self.root, width=600, height=500, corner_radius=15)
        self.forecast_frame.place(x=400, y=20)

        # Label Context
        self.label = ctk.CTkLabel(master=self.frame, text="Weather Forecast", font=('Arial', 18), text_color='#B3B3B3')
        self.label.pack(pady=10)

        self.show_weather_forecast("Ho Chi Minh City")

        self.root.mainloop()

    def show_weather_forecast(self, location):
        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&APPID={api_key}"
            ).json()

            if weather_data['cod'] != '200':
                messagebox.showerror("Error", "City Not Found")
                return

            # Clear existing widgets in the forecast frame
            for widget in self.forecast_frame.winfo_children():
                widget.destroy()

            days = {}
            for forecast in weather_data['list']:
                date = forecast['dt_txt'].split(' ')[0]
                temp = forecast['main']['temp']
                weather = forecast['weather'][0]['main']

                if date not in days:
                    days[date] = {"temps": [], "weather": []}

                days[date]["temps"].append(temp)
                days[date]["weather"].append(weather)

            row = 0
            for date, details in days.items():
                min_temp = min(details["temps"])
                max_temp = max(details["temps"])
                weather = max(set(details["weather"]), key=details["weather"].count)

                date_label = ctk.CTkLabel(self.forecast_frame, text=date, font=('Arial', 14), text_color="#FFFFFF")
                date_label.grid(row=row, column=0, padx=10, pady=5)

                weather_label = ctk.CTkLabel(self.forecast_frame, text=weather, font=('Arial', 14), text_color="#FFFFFF")
                weather_label.grid(row=row, column=1, padx=10, pady=5)

                temp_label = ctk.CTkLabel(self.forecast_frame,
                                          text=f"{min_temp}°C - {max_temp}°C",
                                          font=('Arial', 14), text_color="#FFFFFF")
                temp_label.grid(row=row, column=2, padx=10, pady=5)

                row += 1

        except Exception as e:
            messagebox.showerror("Error", f"Lỗi mạng hoặc dữ liệu không khả dụng: {e}")

# Run the app
WeatherForecast()
