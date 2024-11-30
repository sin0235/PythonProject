import customtkinter as ctk
from datetime import datetime, timedelta
import json
import os
from tkinter import messagebox, Toplevel, Listbox, END, Scrollbar, Text
import calendar
import logging
from tkinter import Text, Scrollbar
from datetime import datetime


class CalendarPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logging.basicConfig(
            filename='calendar_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

        self.COLORS = {
            "background": "#F0F4F8",     # Soft light blue-gray background
            "primary": "#2C7BE5",        # Professional blue
            "secondary": "#FFFFFF",      # Pure white
            "text_dark": "#1A365D",      # Deep blue for dark text
            "text_light": "#2D3748",     # Slightly softer dark text
            "highlight": "#E53E3E",      # Vibrant red for highlights
            "accent": "#38A169",         # Bright green for accents
            "border": "#CBD5E0",         # Light gray border color
            "hover": "#EDF2F7"           # Light hover effect color
        }

        self.EVENTS_FILE = "events.json"
        self.DATE_FORMAT = "%m/%d/%Y"

        self.events = {}
        self.selected_date = None

        self.setup_initial_state()

    def setup_logging(self):
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/calendar_app.log"),
                logging.StreamHandler()
            ]
        )
    def setup_initial_state(self):
        try:
            self.load_events()
            self.normalize_dates()

            self.configure(fg_color=self.COLORS["background"])
            self.create_ui()

            now = datetime.now()
            self.entry_year.insert(0, str(now.year))
            self.entry_month.insert(0, str(now.month))
            self.generate_calendar(now.year, now.month)
            self.display_upcoming_events()

            logging.info("Calendar panel initialized successfully")
        except Exception as e:
            logging.error(f"Error in setup_initial_state: {e}")
            messagebox.showerror("Initialization Error", str(e))

    def load_events(self):
        try:
            with open(self.EVENTS_FILE, "r") as file:
                self.events = json.load(file) if os.path.getsize(self.EVENTS_FILE) > 0 else {}
        except FileNotFoundError:
            self.events = {}
        except json.JSONDecodeError:
            logging.error("Corrupted events file")
            self.events = {}

    def save_events(self):
        try:
            with open(self.EVENTS_FILE, "w") as file:
                json.dump(self.events, file, indent=4)
            logging.info("Events saved successfully")
        except IOError as e:
            logging.error(f"Event saving error: {e}")
            messagebox.showerror("Save Error", "Could not save events.")

    def normalize_dates(self):
        updated_events = {}
        for date_str, day_events in list(self.events.items()):
            try:
                parsed_date = None
                for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue

                if parsed_date:
                    normalized_date = parsed_date.strftime(self.DATE_FORMAT)
                    updated_events[normalized_date] = day_events
            except Exception as e:
                logging.error(f"Date normalization error: {e}")

        if updated_events:
            self.events = updated_events
            self.save_events()

    def parse_event_time(self, time_str):
        try:
            time_formats = [
                "%I:%M%p",
                "%H:%M",
                "%I:%M %p",
            ]

            for fmt in time_formats:
                try:
                    return datetime.strptime(time_str, fmt).strftime("%I:%M %p")
                except ValueError:
                    continue

            raise ValueError("Unsupported time format")
        except ValueError:
            logging.warning(f"Invalid time format: {time_str}")
            return time_str

    def create_ui(self):
        self.frame_controls = ctk.CTkFrame(self, fg_color=self.COLORS["secondary"], border_color=self.COLORS["border"],
                                           border_width=1)
        self.frame_controls.pack(pady=10, padx=10, fill="x")

        self.label_year = ctk.CTkLabel(self.frame_controls, text="Year:",
                                       text_color=self.COLORS["text_dark"],
                                       font=("Roboto", 14, "bold"))
        self.label_year.pack(side="left", padx=5)
        self.entry_year = ctk.CTkEntry(self.frame_controls,
                                       width=80,
                                       text_color=self.COLORS["text_dark"],
                                       fg_color=self.COLORS["hover"])
        self.entry_year.pack(side="left", padx=5)

        self.label_month = ctk.CTkLabel(self.frame_controls, text="Month:",
                                        text_color=self.COLORS["text_dark"],
                                        font=("Roboto", 14, "bold"))
        self.label_month.pack(side="left", padx=5)
        self.entry_month = ctk.CTkEntry(self.frame_controls,
                                        width=50,
                                        text_color=self.COLORS["text_dark"],
                                        fg_color=self.COLORS["hover"])
        self.entry_month.pack(side="left", padx=5)

        button_style = {
            "fg_color": self.COLORS["primary"],
            "hover_color": self.COLORS["hover"],
            "text_color": "white",
            "font": ("Roboto", 14, "bold"),
            "border_width": 0
        }

        self.button_update = ctk.CTkButton(self.frame_controls,
                                           text="Update",
                                           command=self.update_calendar,
                                           **button_style)
        self.button_update.pack(side="left", padx=10)

        self.calendar_frame = ctk.CTkFrame(self, fg_color=self.COLORS["background"])
        self.calendar_frame.pack(pady=10, padx=10)

        self.button_add = ctk.CTkButton(self, text="Add Event",
                                        command=self.on_add_event, **button_style)
        self.button_add.pack(pady=10)

        self.events_display_frame = ctk.CTkFrame(self, fg_color=self.COLORS["background"])
        self.events_display_frame.pack(pady=10, padx=10)

    def validate_event_data(self, time, title, content):
        if not time or not title or not content:
            messagebox.showerror("Validation Error", "All fields are required!")
            return False

        if len(title) > 100:
            messagebox.showerror("Validation Error", "Title too long (max 100 characters)")
            return False

        return True
    def validate_input(self, year, month):
        try:
            year = int(year)
            month = int(month)
            if not (1 <= month <= 12 and year > 0):
                raise ValueError("Invalid month or year")
            return year, month
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid year and month!")
            return None, None
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
        self.reset_day_selection()

        self.selected_date = date_str

        for widget in self.calendar_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == date_str.split("/")[1]:
                widget.configure(
                    fg_color=self.COLORS["primary"],
                    text_color="white",
                    font=("Roboto", 12, "bold")
                )
                break

        self.display_selected_date_events()

    def reset_day_selection(self):
        for widget in self.calendar_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                try:
                    day_num = int(widget.cget("text"))
                    widget.configure(
                        fg_color=self.COLORS["secondary"],
                        text_color=self.COLORS["text_dark"],
                        font=("Roboto", 12)
                    )
                except ValueError:
                    pass

    def display_selected_date_events(self):

        if hasattr(self, 'events_popup') and self.events_popup.winfo_exists():
            self.events_popup.destroy()

        self.events_popup = ctk.CTkToplevel(self)
        self.events_popup.title(f"Events on {self.selected_date}")
        self.events_popup.iconbitmap("Icon/chinhSua.ico")
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        self.events_popup.geometry(f"400x500+{x}+{y}")

        self.events_popup.attributes('-topmost', True)

        events_frame = ctk.CTkScrollableFrame(
            self.events_popup,
            fg_color=self.COLORS["background"],
            scrollbar_fg_color=self.COLORS["primary"]
        )
        events_frame.pack(padx=10, pady=10, fill="both", expand=True)

        title_label = ctk.CTkLabel(
            events_frame,
            text=f"Events on {self.selected_date}",
            font=("Roboto", 18, "bold"),
            text_color=self.COLORS["primary"]
        )
        title_label.pack(pady=(0, 10))

        if self.selected_date in self.events and self.events[self.selected_date]:
            for idx, event in enumerate(self.events[self.selected_date], 1):
                event_frame = ctk.CTkFrame(
                    events_frame,
                    fg_color=self.COLORS["secondary"],
                    corner_radius=10
                )
                event_frame.pack(pady=5, fill="x")

                time_label = ctk.CTkLabel(
                    event_frame,
                    text=f"Time: {event['time']}",
                    font=("Roboto", 14),
                    text_color=self.COLORS["text_dark"],
                    anchor="w"
                )
                time_label.pack(anchor="w", padx=10)

                title_label = ctk.CTkLabel(
                    event_frame,
                    text=f"Title: {event['title']}",
                    font=("Roboto", 14, "bold"),
                    text_color=self.COLORS["primary"],
                    anchor="w"
                )
                title_label.pack(anchor="w", padx=10)

                content_label = ctk.CTkLabel(
                    event_frame,
                    text=f"Content: {event['content']}",
                    font=("Roboto", 12),
                    text_color=self.COLORS["text_dark"],
                    anchor="w",
                    wraplength=350
                )
                content_label.pack(anchor="w", padx=10, pady=(0, 10))

                action_frame = ctk.CTkFrame(event_frame, fg_color="transparent")
                action_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))

                edit_btn = ctk.CTkButton(
                    action_frame,
                    text="Edit",
                    width=50,
                    height=25,
                    fg_color=self.COLORS["accent"],
                    hover_color=self.COLORS["primary"],
                    command=lambda e=event: self.open_edit_event_window(self.selected_date, e)
                )
                edit_btn.pack(side="right", padx=5)

                delete_btn = ctk.CTkButton(
                    action_frame,
                    text="Delete",
                    width=50,
                    height=25,
                    fg_color=self.COLORS["highlight"],
                    hover_color="#FF4500",
                    command=lambda e=event: self.delete_specific_event(self.selected_date, e)
                )
                delete_btn.pack(side="right")
    def delete_specific_event(self, date, event):
        if messagebox.askyesno("Confirm", "Bạn có muốn xóa sự kiện này?"):
            self.events[date].remove(event)
            self.save_events()

            if hasattr(self, 'events_popup'):
                self.events_popup.destroy()
            self.display_selected_date_events()
            self.display_upcoming_events()
    def generate_calendar(self, year, month, selected_date=None):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        days_of_week = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
        for col, day in enumerate(days_of_week):
            day_label = ctk.CTkLabel(self.calendar_frame, text=day,
                                     font=("Roboto", 12, "bold"),
                                     fg_color=self.COLORS["hover"],
                                     text_color=self.COLORS["text_dark"],
                                     width=60,
                                     height=30,
                                     corner_radius=4)
            day_label.grid(row=0, column=col, padx=2, pady=2)

        first_day = datetime(year, month, 1)
        start_day = first_day.weekday()
        days_in_month = calendar.monthrange(year, month)[1]

        row = 1
        col = start_day
        for day in range(1, days_in_month + 1):
            date_str = f"{month:02}/{day:02}/{year}"
            is_selected = selected_date == date_str
            bg_color = self.COLORS["secondary"] if not is_selected else self.COLORS["primary"]
            text_color = self.COLORS["text_dark"] if not is_selected else "white"

            day_label = ctk.CTkLabel(self.calendar_frame, text=str(day),
                                     font=("Roboto", 12),
                                     fg_color=bg_color,
                                     text_color=text_color,
                                     width=60,
                                     height=30,
                                     corner_radius=4)
            day_label.grid(row=row, column=col, padx=2, pady=2)
            day_label.bind("<Button-1>", lambda e, d=date_str: self.on_day_selected(d))

            col += 1
            if col > 6:
                col = 0
                row += 1
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

    def open_edit_event_window(self, selected_date, event=None):
        if hasattr(self, 'events_popup'):
            self.events_popup.destroy()

        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Event")
        edit_window.geometry("450x450")

        time_var = ctk.StringVar(value=event['time'])
        title_var = ctk.StringVar(value=event['title'])
        content_var = ctk.StringVar(value=event['content'])

        ctk.CTkLabel(edit_window, text="Time:").pack(pady=(10, 0))
        time_entry = ctk.CTkEntry(edit_window, textvariable=time_var)
        time_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Title:").pack(pady=(10, 0))
        title_entry = ctk.CTkEntry(edit_window, textvariable=title_var)
        title_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Content:").pack(pady=(10, 0))
        content_entry = ctk.CTkEntry(edit_window, textvariable=content_var)
        content_entry.pack(pady=5)

        def save_changes():
            index = self.events[selected_date].index(event)
            self.events[selected_date][index] = {
                'time': time_var.get(),
                'title': title_var.get(),
                'content': content_var.get()
            }
            self.save_events()
            edit_window.destroy()

            self.display_selected_date_events()
            self.display_upcoming_events()

        save_button = ctk.CTkButton(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=20)

    def get_upcoming_events(self):
        now = datetime.now()
        start_date = now.date()
        end_date = (now + timedelta(days=7)).date()

        upcoming_events = []
        for date_str, day_events in self.events.items():
            try:
                event_date = datetime.strptime(date_str, "%m/%d/%Y").date()
                if start_date <= event_date <= end_date:
                    for event in day_events:
                        try:
                            event_time = self.parse_event_time(event['time'])
                            event_datetime = datetime.combine(
                                event_date,
                                datetime.strptime(event_time, "%I:%M %p").time()
                            )

                            upcoming_events.append({
                                "datetime": event_datetime,
                                "date": date_str,
                                "time": event_time,
                                "title": event['title'],
                                "content": event['content']
                            })
                        except ValueError:
                            continue
            except ValueError:
                continue

        return sorted(upcoming_events, key=lambda x: x["datetime"])

    def display_upcoming_events(self):
        for widget in self.events_display_frame.winfo_children():
            widget.destroy()
        events_container = ctk.CTkFrame(
            self.events_display_frame,
            fg_color=self.COLORS["secondary"],
            corner_radius=10,
            border_color=self.COLORS["border"],
            border_width=1
        )
        events_container.pack(expand=True, fill="both", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            events_container,
            text="📅 Upcoming Events",
            font=("Roboto", 18, "bold"),
            text_color=self.COLORS["text_dark"],
            fg_color="transparent"
        )
        title_label.pack(pady=(10, 5))

        text_widget = Text(
            events_container,
            wrap="word",
            bg=self.COLORS["hover"],
            fg=self.COLORS["text_dark"],
            insertbackground=self.COLORS["text_dark"],
            selectbackground=self.COLORS["primary"],
            selectforeground="white",
            relief="flat",
            padx=10,
            pady=10,
            font=("Roboto", 14)
        )

        scrollbar = ctk.CTkScrollbar(
            events_container,
            orientation="vertical",
            command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        text_widget.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        upcoming_events = self.get_upcoming_events()
        text_widget.tag_configure("title", foreground=self.COLORS["primary"], font=("Roboto", 16, "bold"))
        text_widget.tag_configure("date", foreground=self.COLORS["accent"], font=("Roboto", 14, "italic"))
        text_widget.tag_configure("time", foreground="#D69E2E", font=("Roboto", 14))
        text_widget.tag_configure("content", foreground=self.COLORS["text_dark"], font=("Roboto", 14))
        text_widget.tag_configure("separator", foreground="#718096", font=("Roboto", 12))

        if not upcoming_events:
            text_widget.insert("end", "No upcoming events", "title")
        else:
            text_widget.insert("end", f"Upcoming Events ({len(upcoming_events)})\n\n", "title")

            for i, event in enumerate(upcoming_events, 1):
                text_widget.insert("end", f"Event {i}\n", "title")
                text_widget.insert("end", f"Date: {event['date']}\n", "date")
                text_widget.insert("end", f"Time: {event['time']}\n", "time")
                text_widget.insert("end", f"Title: {event['title']}\n", "title")
                text_widget.insert("end", f"Details: {event['content']}\n", "content")

                if i < len(upcoming_events):
                    text_widget.insert("end", "----------------------------\n", "separator")

        text_widget.configure(state="disabled")