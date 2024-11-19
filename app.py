from tkinter import *
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
api_key = '5dc4c93a4b357abf361daa99a99cd63b'
class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("400x400")
        self.root.title("Weather App")
        icon = tk.PhotoImage(file='WeatherIcon/icon.png')
        self.root.iconphoto(True, icon)
        self.root.config(background="#FFE3D8")
        # Label
        self.label = tk.Label(self.root, text="Your location:", font=('Arial', 18), fg = '#845162')
        self.label.pack(padx=20, pady=20)
        self.label.config(background="#FFE3D8")
        # Textbox
        self.textbox = tk.Text(self.root, font=('Arial', 16), height=1)
        self.textbox.bind("<KeyPress>", self.shortcut)
        self.textbox.pack(padx=20, pady=20)
        self.textbox.config()
        # Button
        self.button = tk.Button(self.root, text="Submit", font=('Arial', 18), command=self.show_weather)
        self.button.pack(padx=20, pady=20)
        self.button.config(background = "#E3B6B1")
        # Run
        self.root.mainloop()
    def show_new_weather(self, weather, temperature, location, tempmin, tempmax, humidity, visibility):
        self.weather_window = tk.Toplevel()
        self.weather_window.geometry("400x400")
        self.weather_window.title("Weather Information")
        self.weather_window.config(background="#FFE3D8")
        # Set icon for new window
        new_window_icon = tk.PhotoImage(file='WeatherIcon/icon.png')
        self.weather_window.iconphoto(True, new_window_icon)

        # Check for clouds and load image if applicable
        if 'cloud' in weather.lower():
            image = Image.open('WeatherIcon/cloudy.png')
            image = image.resize((100, 100), Image.BICUBIC)
            photo_image = ImageTk.PhotoImage(image)
            # Display the image
            label_image = tk.Label(self.weather_window, image=photo_image)
            label_image.image = photo_image  # Keep a reference to prevent garbage collection
            label_image.pack(padx=20, pady=20)
        if 'rain' in weather.lower():
            image = Image.open('WeatherIcon/rain.png')
            image = image.resize((100, 100), Image.BICUBIC)
            photo_image = ImageTk.PhotoImage(image)
            # Display the image
            label_image = tk.Label(self.weather_window, image=photo_image)
            label_image.image = photo_image  # Keep a reference to prevent garbage collection
            label_image.pack(padx=20, pady=20)
        if 'snow' in weather.lower():
            image = Image.open('WeatherIcon/snow.png')
            image = image.resize((100, 100), Image.BICUBIC)
            photo_image = ImageTk.PhotoImage(image)
            # Display the image
            label_image = tk.Label(self.weather_window, image=photo_image)
            label_image.image = photo_image  # Keep a reference to prevent garbage collection
            label_image.pack(padx=20, pady=20)   
        if 'storm' in weather.lower():
            image = Image.open('WeatherIcon/storm.png')
            image = image.resize((100, 100), Image.BICUBIC)
            photo_image = ImageTk.PhotoImage(image)
            # Display the image
            label_image = tk.Label(self.weather_window, image=photo_image)
            label_image.image = photo_image  # Keep a reference to prevent garbage collection
            label_image.pack(padx=20, pady=20)
        if 'clear' in weather.lower():
            image = Image.open('WeatherIcon/clearsky.png')
            image = image.resize((100, 100), Image.BICUBIC)
            photo_image = ImageTk.PhotoImage(image)
            # Display the image
            label_image = tk.Label(self.weather_window, image=photo_image)
            label_image.image = photo_image  # Keep a reference to prevent garbage collection
            label_image.pack(padx=20, pady=20)
        # Display weather and temperature
        label_text = tk.Label(self.weather_window, text=f"Location: {location}\n Weather: {weather}\nTemp: {temperature}°C. Min: {tempmin}°C. Max: {tempmax}°C \nHuminity: {humidity} \nVisibility: {visibility}" , font=('Arial', 16))
        label_text.pack(pady=20)
        label_text.config(background="#FFE3D8")

    def show_weather(self):
        location = self.textbox.get("1.0", tk.END).strip()
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
        ).json()
        
        if weather_data['cod'] == 404:
            messagebox.showerror("Error", "No City Found")
        else:
            weather = weather_data['weather'][0]['main']
            temp = round(weather_data['main']['temp'])
            tempC = round(((temp - 32)*5)/9)
            tempmin = round(weather_data['main']['temp_min'])
            tempminC = round(((tempmin - 32)*5)/9)
            tempmax = round(weather_data['main']['temp_max'])
            tempmaxC = round(((tempmax - 32)*5)/9)
            humidity = weather_data['main']['humidity']
            visibility = weather_data['visibility']
            self.show_new_weather(weather, tempC, location, tempminC, tempmaxC, humidity, visibility)

    
    def shortcut(self, event):
        if event.state == 0 and event.keysym == "Return":
            self.show_weather()

        


# Run the app
WeatherApp()
