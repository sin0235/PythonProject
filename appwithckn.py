import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from customtkinter import CTkImage
import io
from datetime import datetime, timedelta

from pygments.styles.dracula import background

api_key = '30d4741c779ba94c470ca1f63045390a'
# api_key = '5dc4c93a4b357abf361daa99a99cd63b'
# Lấy địa chỉ IP công cộng

public_ip = requests.get("https://api64.ipify.org?format=json").json()["ip"]

# Tra cứu vị trí
response = requests.get(f"http://ip-api.com/json/{public_ip}").json()
country = response.get("country", "Unknown")
city = response.get("city", "Unknown")
class Clock:
    def __init__(self, root):
        self.root = root
        self.clock_label = ctk.CTkLabel(self.root, width=50, height=40, font=('digital-7', 32), text_color="skyblue", 
                                        fg_color= "transparent")
        self.clock_label.place(x=3, y=3)
        self.update_clock()

    def update_clock(self):
        clock = datetime.now()
        h = int(clock.hour)
        m = int(clock.minute)
        s = int(clock.second)
        am_pm = clock.strftime('%p')

        time_string = f"{h:02d}:{m:02d}:{s:02d} {am_pm}"
        self.clock_label.configure(text=time_string)
        self.root.after(1000, self.update_clock)
    

class WeatherAtLocation:
    def __init__(self):
        # Configure customtkinter appearance
        ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

        self.root = ctk.CTk()
        self.root.geometry("1028x720+300+50")
        self.root.title("Application")

        self.frame = ctk.CTkFrame(master=self.root, width=300, height=500, corner_radius=15)
        self.frame.place(x = 750, y = 20)

        # Label Context
        self.label = ctk.CTkLabel(master = self.frame, text="Weather", font=('Arial', 18), text_color= '#B3B3B3')
        self.label.pack(pady = 10)
        #Show weather
        self.show_weather()
        #Clock
        self.clock = Clock(self.root)
        #Framne 2
        self.frame2 = ctk.CTkFrame(master = self.root, width= 260, height= 160, corner_radius= 15)
        self.frame2.place(x = 750,y = 460)


        self.label = ctk.CTkLabel(master=self.frame2, text="Vị trí khác", font=('Arial', 18),
                                  text_color='#B3B3B3')
        self.label.pack(pady=10)
        self.textbox = ctk.CTkTextbox(master = self.frame2, width= 255, height= 1, corner_radius= 15, fg_color= "#2A2A2A",
                                        text_color= "#B2B2B2", font = ("Arial", 18), border_width= 2, border_color= "grey",
                                      activate_scrollbars= False )
        self.textbox.bind("<Return>", self.shortcut)
        self.textbox.pack(pady = 20)
        location = self.textbox.get("1.0", ctk.END).strip()
        self.button = ctk.CTkButton(master = self.frame2, width= 120, height= 20, corner_radius= 15,
                                    hover_color= "#4158D0", text = "OK", font = ("Arial", 18), border_width= 2, border_color= "#B2B2B2",
                                    command = self.show_weather_location)
        self.button.pack(pady = 40)
        # Create the forecast display
        self.forecast_frame = ctk.CTkFrame(self.main_frame)
        self.forecast_frame.pack(side="left", padx=20, pady=20)

        self.forecast_labels = []
        for i in range(7):
            forecast_label = ctk.CTkLabel(self.forecast_frame, text="", font=("Arial", 16))
            forecast_label.pack(pady=10)
            self.forecast_labels.append(forecast_label)

        self.update_weather()
    def update_weather(self):
        # Get the current weather data and update the widgets
        now = datetime.now()
        self.time_label.config(text=now.strftime("%a %d, %I:%M %p"))
        self.temperature_label.config(text=f"{29}°C")
        self.weather_label.config(text="Mostly clear")

        # Update the forecast
        for i in range(7):
            forecast_date = now + timedelta(days=i)
            forecast_text = f"{forecast_date.strftime('%a %d')}\n{33}°C / {26}°C"
            self.forecast_labels[i].config(text=forecast_text)

        self.after(60000, self.update_weather)  # Update every minute

       
        # Run
        self.root.mainloop()

    def show_weather(self):
        location = city
        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
            ).json()
            if weather_data['cod'] == 404:
                messagebox.showerror("Error", "No City Found")
            else:
                weather = weather_data['weather'][0]['main']
                temp = round(weather_data['main']['temp'])
                tempC = round(((temp - 32) * 5) / 9)
                tempmin = round(weather_data['main']['temp_min'])
                tempminC = round(((tempmin - 32) * 5) / 9)
                tempmax = round(weather_data['main']['temp_max'])
                tempmaxC = round(((tempmax - 32) * 5) / 9)
                humidity = weather_data['main']['humidity']
                visibility = weather_data['visibility']
                size_image = (200, 200)
                icon_path = ""
                if 'clear' in weather.lower():
                    icon_path = "Icon/clear.png"
                if 'cloud' in weather.lower():
                    icon_path = "Icon/cloud.png"
                if 'rain' in weather.lower():
                    icon_path = "Icon/rain.png"
                if 'snow' in weather.lower():
                    icon_path = "Icon/snow.png"
                if 'storm' in weather.lower():
                    icon_path = "Icon/storm.png"

                image = Image.open(icon_path)
                    # Label chứa icon
                picture = ctk.CTkImage(dark_image=image, light_image= image, size = size_image)
                label_picture = ctk.CTkLabel(master = self.frame, image = picture, text = "")
                label_picture.pack()
                label_text = ctk.CTkLabel(
                        master = self.frame,
                        text=f"Vị Trí: {location}\nThời tiết: {weather}\nNhiệt độ: {tempC}°C\n"
                             f"Thấp nhất: {tempminC}°C, Cao nhất: {tempmaxC}°C\nĐộ ẩm: {humidity}\nTầm nhìn xa: {visibility}",
                        font=('Arial', 18),
                    )
                label_text.pack(pady = 30)
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi mạng, không truy cập được vị trí")

    def show_weather_location(self):
        # Get the location from the textbox
        location = self.textbox.get("1.0", ctk.END).strip()

        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
            ).json()

            if weather_data['cod'] == 404:
                messagebox.showerror("Error", "No City Found")
            else:
                # Clear existing widgets in frame1
                for widget in self.frame.winfo_children():
                    widget.destroy()

                # Extract weather information
                weather = weather_data['weather'][0]['main']
                temp = round(weather_data['main']['temp'])
                tempC = round(((temp - 32) * 5) / 9)
                tempmin = round(weather_data['main']['temp_min'])
                tempminC = round(((tempmin - 32) * 5) / 9)
                tempmax = round(weather_data['main']['temp_max'])
                tempmaxC = round(((tempmax - 32) * 5) / 9)
                humidity = weather_data['main']['humidity']
                visibility = weather_data['visibility']
                size_image = (200, 200)
                icon_path = ""
                # Determine the appropriate icon based on weather conditions
                if 'clear' in weather.lower():
                    icon_path = "Icon/clear.png"
                elif 'cloud' in weather.lower():
                    icon_path = "Icon/cloud.png"
                elif 'rain' in weather.lower():
                    icon_path = "Icon/rain.png"
                elif 'snow' in weather.lower():
                    icon_path = "Icon/snow.png"
                elif 'storm' in weather.lower():
                    icon_path = "Icon/storm.png"

                # Load the icon image
                image = Image.open(icon_path)
                picture = ctk.CTkImage(dark_image=image, light_image=image, size=size_image)

                # Create and display the new weather information
                label_picture = ctk.CTkLabel(master=self.frame, image=picture, text="")
                label_picture.pack()

                label_text = ctk.CTkLabel(
                    master=self.frame,
                    text=f"Vị Trí: {location}\nThời tiết: {weather}\nNhiệt độ: {tempC}°C\n"
                         f"Thấp nhất: {tempminC}°C, Cao nhất: {tempmaxC}°C\nĐộ ẩm: {humidity}\nTầm nhìn xa: {visibility}",
                    font=('Arial', 18),
                )
                label_text.pack(pady=30)
                self.clear_text_box()

        except Exception as e:
            messagebox.showerror("Error", f"Nhập sai tên, vui lòng nhập lại: {e}")

    def shortcut(self, event):
        if event.keysym == "Return":
            self.show_weather_location()
    def clear_text_box(self ):
        self.textbox.delete("0.0", "end")
        

# Run the app
WeatherAtLocation()

