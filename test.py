import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from customtkinter import CTkImage
location = "Berlin"
api_key = '5dc4c93a4b357abf361daa99a99cd63b'
weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}").json()
print(weather_data)