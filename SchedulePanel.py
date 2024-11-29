import customtkinter as ctk
from datetime import datetime, timedelta
import json
import os
from tkinter import messagebox, Toplevel, Listbox, END, Scrollbar, Text
import calendar


class CalendarPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.COLORS = {
            "background": "#FFFFFF",
            "primary": "#00BCD4",
            "secondary": "#E0F7FA",
            "text_light": "#212121",
            "text_dark": "#37474F",
            "highlight": "#FF4081",
            "accent": "#FFEB3B"
        }

        self.EVENTS_FILE = "events.json"

        self.events = {}

        self.load_events()
        self.normalize_dates()

        self.selected_date = None

        self.configure(fg_color=self.COLORS["background"])
        self.create_ui()

        now = datetime.now()
        self.entry_year.insert(0, str(now.year))
        self.entry_month.insert(0, str(now.month))
        self.generate_calendar(now.year, now.month)
        self.display_upcoming_events()

    def load_events(self):
        if os.path.exists(self.EVENTS_FILE):
            with open(self.EVENTS_FILE, "r") as file:
                try:
                    self.events = json.load(file)
                except json.JSONDecodeError:
                    self.events = {}
        else:
            self.events = {}

    def save_events(self):
        with open(self.EVENTS_FILE, "w") as file:
            json.dump(self.events, file, indent=4)

    def normalize_dates(self):
        updated_events = {}
        for date_str, day_events in self.events.items():
            if not isinstance(date_str, str) or len(date_str) != 10:
                continue

            try:
                date = datetime.strptime(date_str, "%m/%d/%Y")
            except ValueError:
                try:
                    date = datetime.strptime(date_str, "%m/%d/%y")
                except ValueError:
                    continue

            normalized_date_str = date.strftime("%m/%d/%Y")
            updated_events[normalized_date_str] = day_events
        self.events = updated_events
        self.save_events()

    def create_ui(self):
        self.frame_controls = ctk.CTkFrame(self, fg_color=self.COLORS["secondary"])
        self.frame_controls.pack(pady=10, padx=10, fill="x")

        self.label_year = ctk.CTkLabel(self.frame_controls, text="Year:",
                                       text_color=self.COLORS["text_light"],
                                       font=("Roboto", 14, "bold"))
        self.label_year.pack(side="left", padx=5)
        self.entry_year = ctk.CTkEntry(self.frame_controls,
                                       width=80,
                                       text_color="#FFFFFF",
                                       fg_color=self.COLORS["text_light"])
        self.entry_year.pack(side="left", padx=5)

        self.label_month = ctk.CTkLabel(self.frame_controls, text="Month:",
                                        text_color=self.COLORS["text_light"],
                                        font=("Roboto", 14, "bold"))
        self.label_month.pack(side="left", padx=5)
        self.entry_month = ctk.CTkEntry(self.frame_controls,
                                        width=50,
                                        text_color="#FFFFFF",
                                        fg_color=self.COLORS["text_light"])
        self.entry_month.pack(side="left", padx=5)

        self.button_update = ctk.CTkButton(self.frame_controls,
                                           text="Update",
                                           command=self.update_calendar,
                                           fg_color=self.COLORS["primary"],
                                           hover_color=self.COLORS["secondary"],
                                           text_color=self.COLORS["text_light"])
        self.button_update.pack(side="left", padx=10)

        self.calendar_frame = ctk.CTkFrame(self, fg_color=self.COLORS["background"])
        self.calendar_frame.pack(pady=10, padx=10)

        self.frame_event = ctk.CTkFrame(self, fg_color=self.COLORS["background"])
        self.frame_event.pack(pady=10, padx=10)

        self.frame_left = ctk.CTkFrame(self.frame_event, fg_color=self.COLORS["background"])
        self.frame_left.pack(side="left", padx=20)

        self.frame_right = ctk.CTkFrame(self.frame_event, fg_color=self.COLORS["background"])
        self.frame_right.pack(side="left", padx=20)

        button_style = {
            "fg_color": self.COLORS["primary"],
            "hover_color": self.COLORS["secondary"],
            "text_color": self.COLORS["text_light"],
            "font": ("Roboto", 14, "bold")
        }

        self.button_add = ctk.CTkButton(self.frame_left, text="Add Event",
                                        command=self.on_add_event, **button_style)
        self.button_add.pack(pady=5)

        self.button_view = ctk.CTkButton(self.frame_left, text="View Event",
                                         command=self.view_events, **button_style)
        self.button_view.pack(pady=5)

        delete_button_style = button_style.copy()
        delete_button_style["fg_color"] = self.COLORS["highlight"]
        delete_button_style["hover_color"] = "#C0392B"
        self.button_edit_event = ctk.CTkButton(self.frame_right, text="Edit Event",
                                               command=lambda: self.open_edit_event_window(self.selected_date),
                                               **button_style)
        self.button_edit_event.pack(pady=5)

        self.button_delete_event = ctk.CTkButton(self.frame_right, text="Delete Event",
                                                 command=self.open_delete_event_window,
                                                 **delete_button_style)
        self.button_delete_event.pack(pady=5)

        self.events_display_frame = ctk.CTkFrame(self, fg_color=self.COLORS["background"])
        self.events_display_frame.pack(pady=10, padx=10)

    def generate_calendar(self, year, month, selected_date=None):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        days_of_week = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
        for col, day in enumerate(days_of_week):
            day_label = ctk.CTkLabel(self.calendar_frame,
                                     text=day,
                                     font=("Roboto", 12, "bold"),
                                     fg_color=self.COLORS["secondary"],
                                     text_color=self.COLORS["text_light"],
                                     width=60,
                                     height=30,
                                     corner_radius=6)
            day_label.grid(row=0, column=col, padx=2, pady=2)

        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()
        days_in_month = calendar.monthrange(year, month)[1]

        row = 1
        col = start_day
        for day in range(1, days_in_month + 1):
            date_str = f"{month:02}/{day:02}/{year}"
            is_selected = selected_date == date_str
            bg_color = self.COLORS["secondary"] if not is_selected else self.COLORS["highlight"]
            text_color = self.COLORS["text_light"] if not is_selected else "white"

            day_label = ctk.CTkLabel(self.calendar_frame,
                                     text=str(day),
                                     font=("Roboto", 12, "bold"),
                                     fg_color=bg_color,
                                     text_color=text_color,
                                     width=60,
                                     height=30,
                                     corner_radius=6)
            day_label.grid(row=row, column=col, padx=2, pady=2)
            day_label.bind("<Button-1>", lambda e, d=date_str: self.on_day_selected(d))

            col += 1
            if col > 6:
                col = 0
                row += 1

    def generate_calendar(self, year, month, selected_date=None):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        days_of_week = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
        for col, day in enumerate(days_of_week):
            day_label = ctk.CTkLabel(self.calendar_frame, text=day, font=("Roboto", 12, "bold"),
                                     fg_color="#333333", text_color="white", width=60, height=30, corner_radius=4)
            day_label.grid(row=0, column=col, padx=2, pady=2)

        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()

        days_in_month = calendar.monthrange(year, month)[1]

        row = 1
        col = start_day
        for day in range(1, days_in_month + 1):
            date_str = f"{month:02}/{day:02}/{year}"
            is_selected = selected_date == date_str
            bg_color = "#444444" if not is_selected else "#FF8C00"
            text_color = "white" if not is_selected else "black"

            day_label = ctk.CTkLabel(self.calendar_frame, text=str(day), font=("Roboto", 12),
                                     fg_color=bg_color, text_color=text_color, width=60, height=30, corner_radius=4)
            day_label.grid(row=row, column=col, padx=2, pady=2)
            day_label.bind("<Button-1>", lambda e, d=date_str: self.on_day_selected(d))

            col += 1
            if col > 6:
                col = 0
                row += 1

    def update_calendar(self, event=None):
        try:
            year = int(self.entry_year.get())
            month = int(self.entry_month.get())
            if 1 <= month <= 12:
                self.generate_calendar(year, month)
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Vui lòng nhập năm và tháng hợp lệ!")

    def on_day_selected(self, date_str):
        self.selected_date = date_str
        year = int(self.entry_year.get())
        month = int(self.entry_month.get())
        self.generate_calendar(year, month, self.selected_date)

    def on_add_event(self):
        if not self.selected_date:
            messagebox.showerror("Error", "No date selected! Please select a date.")
            return
        self.open_add_event_window(self.selected_date)

    def open_add_event_window(self, selected_date):
        event_window = Toplevel(self)
        event_window.title("Add Event")
        event_window.geometry("450x450")

        label_time = ctk.CTkLabel(event_window, text="Time :", text_color="black")
        label_time.pack(pady=5)
        entry_time = ctk.CTkEntry(event_window)
        entry_time.pack(pady=5)

        label_title = ctk.CTkLabel(event_window, text="Event Title:", text_color="black")
        label_title.pack(pady=5)
        entry_title = ctk.CTkEntry(event_window)
        entry_title.pack(pady=5)

        label_content = ctk.CTkLabel(event_window, text="Event Content:", text_color="black")
        label_content.pack(pady=5)
        entry_content = ctk.CTkEntry(event_window)
        entry_content.pack(pady=5)

        def save_event():
            time = entry_time.get()
            title = entry_title.get()
            content = entry_content.get()

            if not time or not title or not content:
                messagebox.showerror("Error", "Please fill in all fields!")
                return

            selected_date_normalized = datetime.strptime(selected_date, "%m/%d/%Y").strftime("%m/%d/%Y")

            if selected_date_normalized not in self.events:
                self.events[selected_date_normalized] = []

            self.events[selected_date_normalized].append({"time": time, "title": title, "content": content})
            self.save_events()
            messagebox.showinfo("Success", "Event added successfully!")

            self.display_upcoming_events()
            event_window.destroy()

        button_save = ctk.CTkButton(event_window, text="Save Event", command=save_event)
        button_save.pack(pady=10)

        event_window.update_idletasks()
        event_window.minsize(event_window.winfo_width(), event_window.winfo_height())

    def view_events(self):
        if not self.selected_date:
            messagebox.showerror("Error", "No date selected! Please select a date.")
            return

        if self.selected_date in self.events and self.events[self.selected_date]:
            event_list = self.events[self.selected_date]
            message = f"Events on {self.selected_date}:\n\n"
            for i, event in enumerate(event_list, 1):
                message += f"{i}. {event['time']} - {event['title']}\n   {event['content']}\n\n"
        else:
            message = f"No events on {self.selected_date}."

        messagebox.showinfo("Events", message)

    def open_delete_event_window(self):
        if not self.selected_date:
            messagebox.showerror("Error", "No date selected! Please select a date.")
            return

        if self.selected_date not in self.events or not self.events[self.selected_date]:
            messagebox.showinfo("No Events", f"No events found on {self.selected_date}.")
            return

        delete_window = Toplevel(self)
        delete_window.title("Delete Event")
        delete_window.geometry("500x500")

        listbox_frame = ctk.CTkFrame(delete_window)
        listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        listbox_events = Listbox(
            listbox_frame,
            height=12,
            width=50,
            selectmode="single",
            font=("Roboto", 14),
            yscrollcommand=scrollbar.set
        )
        listbox_events.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=listbox_events.yview)

        for i, event in enumerate(self.events[self.selected_date], 1):
            listbox_events.insert(END, f"{i}. {event['time']} - {event['title']}")

        def delete_event():
            try:
                selected_index = listbox_events.curselection()[0]
                self.events[self.selected_date].pop(selected_index)
                self.save_events()
                self.display_upcoming_events()

                if not self.events[self.selected_date]:
                    del self.events[self.selected_date]

                messagebox.showinfo("Success", "Event deleted successfully!")
                delete_window.destroy()
            except IndexError:
                messagebox.showerror("Error", "Please select an event to delete.")

        button_delete = ctk.CTkButton(delete_window, text="Delete Selected Event", command=delete_event)
        button_delete.pack(pady=(5, 10))

    def open_edit_event_window(self, selected_date):
        if selected_date not in self.events or not self.events[selected_date]:
            messagebox.showerror("Error", f"No events found for {selected_date}.")
            return

        edit_window = Toplevel(self)
        edit_window.title(f"Edit Event - {selected_date}")
        edit_window.geometry("500x500")

        listbox_frame = ctk.CTkFrame(edit_window)
        listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        event_listbox = Listbox(
            listbox_frame,
            font=("Roboto", 14),
            height=12,
            width=50,
            selectmode="single",
            yscrollcommand=scrollbar.set
        )
        event_listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=event_listbox.yview)

        for idx, event in enumerate(self.events[selected_date], 1):
            event_listbox.insert(END, f"{idx}. {event['time']} - {event['title']}")

        def edit_selected_event():
            selected_index = event_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Error", "Please select an event to edit!")
                return

            event_index = selected_index[0]
            event_to_edit = self.events[selected_date][event_index]

            edit_event_window = Toplevel(edit_window)
            edit_event_window.title("Edit Event Details")
            edit_event_window.geometry("500x500")

            label_time = ctk.CTkLabel(edit_event_window, text="Time :", text_color="black", font=("Roboto", 14))
            label_time.pack(pady=5)
            entry_time = ctk.CTkEntry(edit_event_window, font=("Roboto", 14))
            entry_time.insert(0, event_to_edit['time'])
            entry_time.pack(pady=5)

            label_title = ctk.CTkLabel(edit_event_window, text="Event Title:", text_color="black", font=("Roboto", 14))
            label_title.pack(pady=5)
            entry_title = ctk.CTkEntry(edit_event_window, font=("Roboto", 14))
            entry_title.insert(0, event_to_edit['title'])
            entry_title.pack(pady=5)

            label_content = ctk.CTkLabel(edit_event_window, text="Event Content:", text_color="black",
                                         font=("Roboto", 14))
            label_content.pack(pady=5)
            entry_content = ctk.CTkEntry(edit_event_window, font=("Roboto", 14))
            entry_content.insert(0, event_to_edit['content'])
            entry_content.pack(pady=5)

            def save_edited_event():
                new_time = entry_time.get()
                new_title = entry_title.get()
                new_content = entry_content.get()

                if not new_time or not new_title or not new_content:
                    messagebox.showerror("Error", "Please fill in all fields!")
                    return

                self.events[selected_date][event_index] = {
                    "time": new_time,
                    "title": new_title,
                    "content": new_content
                }
                self.save_events()
                self.display_upcoming_events()
                messagebox.showinfo("Success", "Event updated successfully!")
                edit_event_window.destroy()
                edit_window.destroy()

            button_save = ctk.CTkButton(edit_event_window, text="Save Changes",
                                        command=save_edited_event, font=("Roboto", 14))
            button_save.pack(pady=10)
        button_edit = ctk.CTkButton(edit_window, text="Edit Selected Event",
                                    command=edit_selected_event, font=("Roboto", 14))
        button_edit.pack(pady=(5, 10))

    def get_upcoming_events(self):
        now = datetime.now()
        today_str = now.strftime("%m/%d/%Y")
        next_day = now + timedelta(days=1)
        next_day_str = next_day.strftime("%m/%d/%Y")

        upcoming_events = []
        for date_str, day_events in self.events.items():
            if today_str <= date_str <= next_day_str:
                for event in day_events:
                    try:
                        event_datetime = datetime.strptime(f"{date_str} {event['time']}", "%m/%d/%Y %I:%M%p")
                    except ValueError:
                        try:
                            event_time_24 = datetime.strptime(event['time'], "%H:%M")
                            event_time_12 = event_time_24.strftime("%I:%M%p")
                            event_datetime = datetime.strptime(f"{date_str} {event_time_12}", "%m/%d/%Y %I:%M%p")
                        except ValueError:
                            continue

                    upcoming_events.append({
                        "datetime": event_datetime,
                        "date": date_str,
                        "time": event["time"],
                        "title": event["title"],
                        "content": event["content"]
                    })

        upcoming_events.sort(key=lambda x: x["datetime"])
        return upcoming_events

    def display_upcoming_events(self):
        for widget in self.events_display_frame.winfo_children():
            widget.destroy()

        self.events_display_frame.configure(
            width=int(self.winfo_width() * 0.7),
            height=int(self.winfo_height() * 0.7)
        )

        scrollbar = Scrollbar(self.events_display_frame, orient="vertical")
        text_widget = Text(
            self.events_display_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg="#222222",
            fg="white",
            font=("Roboto", 14),
            relief="flat",
            height=20,
            width=70,
        )
        scrollbar.config(command=text_widget.yview)

        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", fill="both", expand=True)

        upcoming_events = self.get_upcoming_events()

        if not upcoming_events:
            message = "No upcoming events (Today & Tomorrow)."
        else:
            message = "Upcoming Events (Today & Tomorrow):\n\n"
            for event in upcoming_events:
                message += f"{event['date']} - {event['time']} - {event['title']}\n   {event['content']}\n\n"

        text_widget.insert("1.0", message)

        text_widget.tag_configure("center", justify="center")
        text_widget.tag_add("center", "1.0", "end")
        text_widget.config(state="disabled")