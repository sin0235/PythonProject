import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from customtkinter import CTkImage
from datetime import datetime
from pygments.styles.dracula import background
api_key = '30d4741c779ba94c470ca1f63045390a'
# api_key = '5dc4c93a4b357abf361daa99a99cd63b'
# Lấy địa chỉ IP công cộng
public_ip = requests.get("https://api64.ipify.org?format=json").json()["ip"]
# Tra cứu vị trí
response = requests.get(f"http://ip-api.com/json/{public_ip}").json()
#Lấy vị trí cụ thể
country = response.get("country", "Unknown")
city = response.get("city", "Unknown")

size_status_icon = (20, 20)
#Đồng hồ
class Clock:
    def __init__(self, root):
        self.root = root
        self.clock_label = ctk.CTkLabel(self.root, width=50, height=40, font=('digital-7', 32), text_color="skyblue")
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

        #Chọn theme của app
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        #Thiết lập thông số màn hình chính
        self.root = ctk.CTk()
        self.root.geometry("1280x720+150+50")
        self.root.title("Application")
        #Clock
        self.clock = Clock(self.root)

        #Tạo frame đầu tiên chứa thông tin thời tiết tại vị trí
        self.frame = ctk.CTkFrame(master=self.root, width=300, height=500, corner_radius=15, fg_color= "transparent")
        self.frame.place(x = 960, y = 20)

        # Label của frame
        self.label = ctk.CTkLabel(master = self.frame, text="Weather", font=('Arial', 18), text_color= '#B3B3B3')
        self.label.pack(pady = 10)

        #Hiển thị vị trí tại địa chỉ IP
        self.show_weather()

        #Frame 2 chứa lựa chọn truy cập đếp vị trí khác hoặc dự báo thời tiết
        self.create_frame2()
        self.root.mainloop()
    #Hàm tạo ra Frame 2   
    def create_frame2(self):
        self.frame2 = ctk.CTkFrame(master = self.root, width= 300, height= 80, corner_radius= 15, fg_color= "transparent")
        self.frame2.place(x = 950,y = 460)

        self.label = ctk.CTkLabel(master=self.frame2, text="Vị trí khác", font=('Arial', 18),
                                  text_color='#B3B3B3')
        self.label.pack(pady=2)

        self.textbox = ctk.CTkTextbox(master = self.frame2, width= 255, height= 1, corner_radius= 15, fg_color= "#2A2A2A",
                                        text_color= "#B2B2B2", font = ("Arial", 18), border_width= 2, border_color= "grey",
                                      activate_scrollbars= False )
        self.textbox.bind("<Return>", self.shortcut)
        self.textbox.pack(pady = 5)
        self.location = self.textbox.get("1.0", ctk.END).strip()

        self.button = ctk.CTkButton(master = self.frame2, width= 120, height= 20, corner_radius= 15,
                                    hover_color= "#4158D0", text = "OK", font = ("Arial", 18), border_width= 2, border_color= "#B2B2B2",
                                    command = self.show_weather_location)
        self.button.pack(pady = 8)

        # Label nội dung
        self.label = ctk.CTkLabel(master=self.frame2, text="Weather Forecast", font=('Arial', 18), text_color='#B3B3B3')
        self.label.pack(pady=11)
        #Nút dự báo thời tiết
        self.button2_presses = False
        self.button2 = ctk.CTkButton(master = self.frame2, width= 120, height= 20, corner_radius= 15,
                                    hover_color= "#4158D0", text = "FORECAST", font = ("Arial", 18), border_width= 2, 
                                    border_color= "#B2B2B2",
                                    command = self.handle_button2_click)
        self.button2.pack(pady = 14)
    #Hàm xử lí sự kiện khi nhấn nút "OK" để hiển thị thời tiết ở vị trí khác
    def handle_button2_click(self):
        self.button2_presses = not self.button2_presses
        if self.button2_presses:
            self.show_weather_forecast(city)
            self.new_frame2()
    #Hàm hiển thị thời tiết tại vị trí IP
    def show_weather(self):
        location = city
        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
            ).json()
            if weather_data['cod'] == 404:
                messagebox.showerror("Error", "No City Found")
            
            else:
                # Xử lí dữ liệu
                weather = weather_data['weather'][0]['main']
                temp = round(weather_data['main']['temp'])
                tempC = round(((temp - 32) * 5) / 9)
                tempmin = round(weather_data['main']['temp_min'])
                tempminC = round(((tempmin - 32) * 5) / 9)
                tempmax = round(weather_data['main']['temp_max'])
                tempmaxC = round(((tempmax - 32) * 5) / 9)
                humidity = weather_data['main']['humidity']
                visibility = weather_data['visibility']
                self.show_weather_icon(weather, size_image = (150, 150))
                # Tạo các Label với icon
                self.load_icon("Icon/location.png", text = f"{location}")
                self.load_icon("Icon/temperature.png", text = f"{tempC}°C")
                self.load_icon("Icon/temperaturerange.png", text = f"{tempmaxC}°C / {tempminC}°C")
                self.load_icon("Icon/weather.png", text = f"{weather}")
                self.load_icon("Icon/humidity.png", text=f"{humidity}")
                self.load_icon("Icon/visibility.png", text=f"{visibility}")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi mạng, không truy cập được vị trí")

    def load_icon(self, icon_path, size = size_status_icon, text = ""):
        icon = Image.open(icon_path)
        icon_picture = ctk.CTkImage(dark_image=icon, light_image=icon, size=size)
        icon_label = ctk.CTkLabel(master=self.frame, text=f":\t{text}", image=icon_picture, compound= "left", font=('Arial', 18))
        icon_label.pack(pady = 5, anchor = "w")

    #Hàm hiển thị thời tiết tại vị trí chỉ định trong textbox
    def show_weather_location(self):
        # Lấy vị trí từ Textbox
        location = self.textbox.get("1.0", ctk.END).strip()

        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
            ).json()

            if weather_data['cod'] == 404:
                messagebox.showerror("Error", "No City Found in frame 1")
            else:
                # Xóa frame 1
                for widget in self.frame.winfo_children():
                    widget.destroy()

                # Xử lí dữ liệu
                weather = weather_data['weather'][0]['main']
                temp = round(weather_data['main']['temp'])
                tempC = round(((temp - 32) * 5) / 9)
                tempmin = round(weather_data['main']['temp_min'])
                tempminC = round(((tempmin - 32) * 5) / 9)
                tempmax = round(weather_data['main']['temp_max'])
                tempmaxC = round(((tempmax - 32) * 5) / 9)
                humidity = weather_data['main']['humidity']
                visibility = weather_data['visibility']

                #Hiển thị icon thời tiết
                self.show_weather_icon(weather, size_image = (150, 150))

                # Tạo các Label với icon
                self.load_icon("Icon/location.png", text = f"{location}")
                self.load_icon("Icon/temperature.png", text = f"{tempC}°C")
                self.load_icon("Icon/temperaturerange.png", text = f"{tempmaxC}°C / {tempminC}°C")
                self.load_icon("Icon/weather.png", text = f"{weather}")
                self.load_icon("Icon/humidity.png", text=f"{humidity}")
                self.load_icon("Icon/visibility.png", text=f"{visibility}")
                self.clear_text_box()

        except Exception as e:
            messagebox.showerror("Error", f"Nhập sai tên, vui lòng nhập lại: {e}")

    def show_weather_icon(self, weather, size_image):
        icon_path = ""
        # Hiển thị icon dựa trên thông tin trả về
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

        # Load và hiển thị ảnh icon tình hình thời tiết
        image = Image.open(icon_path)
        picture = ctk.CTkImage(dark_image=image, light_image=image, size=size_image)
        label_picture = ctk.CTkLabel(master=self.frame, image=picture, text="")
        label_picture.pack()
    #Hàm xử lí nút "Enter" khi nhập
    def shortcut(self, event):
        if event.keysym == "Return":
            self.show_weather_location()
    #Hàm xóa nội dung trong Textbox
    def clear_text_box(self ):
        self.textbox.delete("0.0", "end")
    #Hàm dự báo thời tiết tại khu vực nhập
    def show_weather_forecast(self, location):
        try:
            # Gửi yêu cầu API để lấy thông tin dự báo thời tiết
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&APPID={api_key}"
            ).json()

            # Kiểm tra nếu thành phố không hợp lệ
            if weather_data['cod'] != '200':
                messagebox.showerror("Error", "City Not Found in frame 2")
                return

            # Xóa frame hiện tại và tạo frame mới
            self.frame.destroy()
            self.frame = ctk.CTkFrame(master=self.root, width=300, height=700, corner_radius=15, fg_color= "transparent")
            self.frame.place(x=920, y=20)

            # Hiển thị vị trí dự báo
            location_label = ctk.CTkLabel(
                master=self.frame,
                text=f"Dự báo thời tiết cho: {location}",
                font=("Arial", 18, "bold"),
                text_color="#FFFFFF",
                anchor="w",
            )
            location_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

            # Xử lý dữ liệu dự báo
            days = {}
            for forecast in weather_data['list']:
                date = forecast['dt_txt'].split(' ')[0]
                temp = forecast['main']['temp']
                weather = forecast['weather'][0]['main']

                if date not in days:
                    days[date] = {"temps": [], "weather": []}

                days[date]["temps"].append(temp)
                days[date]["weather"].append(weather)

            # Hiển thị thông tin dự báo thời tiết theo ngày
            row = 1
            for date, details in days.items():
                min_temp = min(details["temps"])
                max_temp = max(details["temps"])
                weather = max(set(details["weather"]), key=details["weather"].count)

                # Hiển thị ngày
                date_label = ctk.CTkLabel(self.frame, text=date, font=('Arial', 14), text_color="#FFFFFF")
                date_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

                # Hiển thị biểu tượng thời tiết
                size_image = (50, 50)
                icon_path = ""
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

                image = Image.open(icon_path)
                picture = ctk.CTkImage(dark_image=image, light_image=image, size=size_image)
                weather_label = ctk.CTkLabel(self.frame, image=picture, text="")
                weather_label.grid(row=row, column=1, padx=5, pady=5)

                # Hiển thị nhiệt độ tối thiểu và tối đa
                temp_label = ctk.CTkLabel(
                    self.frame,
                    text=f"{min_temp}°C - {max_temp}°C",
                    font=('Arial', 14),
                    text_color="#FFFFFF"
                )
                temp_label.grid(row=row, column=2, padx=10, pady=5, sticky="e")
                row += 1

            # Nút Back để quay lại giao diện thời tiết chính
            back_button = ctk.CTkButton(master=self.frame, width=120, height=20, corner_radius=15, hover_color="#4158D0", text="Back", 
                font=("Arial", 18),border_width=2, border_color="#B2B2B2", command=self.back_function
            )
            back_button.grid(column=1, row=row, padx=5, pady=10, columnspan=2)

        except Exception as e:
            messagebox.showerror("Error", f"Lỗi mạng hoặc dữ liệu không khả dụng: {e}")

    def back_function(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame = ctk.CTkFrame(master=self.root, width=300, height=500, corner_radius=15, fg_color= "transparent")
        self.frame.place(x = 960, y = 20)
        for widget in self.frame2.winfo_children():
            widget.destroy()
        self.create_frame2()
        self.show_weather()
        

    def new_frame2(self):
        for widget in self.frame2.winfo_children():
                widget.destroy()
        self.label = ctk.CTkLabel(master=self.frame2, text="Vị trí khác", font=('Arial', 18),
                                  text_color='#B3B3B3')
        self.label.pack(pady=2)
        self.textbox = ctk.CTkTextbox(master = self.frame2, width= 255, height= 1, corner_radius= 15, fg_color= "#2A2A2A",
                                        text_color= "#B2B2B2", font = ("Arial", 18), border_width= 2, border_color= "grey",
                                      activate_scrollbars= False )
        self.textbox.bind("<Return>", self.shortcut)
        self.textbox.pack(pady = 5)
        self.button = ctk.CTkButton(master = self.frame2, width= 120, height= 20, corner_radius= 15,
                                    hover_color= "#4158D0", text = "OK", font = ("Arial", 18), border_width= 2, border_color= "#B2B2B2",
                                    command=lambda: self.show_weather_forecast(location=self.textbox.get("1.0", ctk.END).strip()))
        self.button.pack(pady = 8)

# Run the app
WeatherAtLocation()

