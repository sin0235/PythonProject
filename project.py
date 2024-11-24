import customtkinter as ctk
from datetime import datetime, timedelta
import json
import os
from tkinter import messagebox, Toplevel, Listbox, END
import calendar
from tkinter import Scrollbar, Text
# Tệp lưu trữ sự kiện
EVENTS_FILE = "events.json"

# Khởi tạo dictionary lưu các sự kiện
events = {}

# Hàm tải sự kiện từ file JSON
def load_events():
    global events
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            try:
                events = json.load(file)
            except json.JSONDecodeError:
                events = {}
    else:
        events = {}

# Hàm lưu sự kiện vào file JSON
def save_events():
    with open(EVENTS_FILE, "w") as file:
        json.dump(events, file, indent=4)

# Hàm chuẩn hóa ngày tháng
def normalize_dates():
    global events
    updated_events = {}
    for date_str, day_events in events.items():
        # Kiểm tra nếu định dạng là hợp lệ
        if not isinstance(date_str, str) or len(date_str) != 10:
            continue  # Bỏ qua nếu định dạng không hợp lệ

        try:
            date = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            try:
                date = datetime.strptime(date_str, "%m/%d/%y")
            except ValueError:
                continue  # Bỏ qua nếu không thể phân tích

        normalized_date_str = date.strftime("%m/%d/%Y")
        updated_events[normalized_date_str] = day_events
    events = updated_events
    save_events()

# Khởi tạo ứng dụng
app = ctk.CTk()
app.geometry("1280x768")
app.title("Calendar App")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Hàm tạo và hiển thị lịch
# Hàm tạo và hiển thị lịch
def generate_calendar(year, month, selected_date=None):
    # Xóa tất cả widget cũ trong calendar_frame
    for widget in calendar_frame.winfo_children():
        widget.destroy()

    # Định nghĩa tiêu đề các ngày trong tuần (tuần bắt đầu từ Thứ Hai)
    days_of_week = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
    for col, day in enumerate(days_of_week):
        day_label = ctk.CTkLabel(calendar_frame, text=day, font=("Arial", 12, "bold"),  # Giảm kích thước chữ
                                 fg_color="#333333", text_color="white", width=60, height=30, corner_radius=4)
        day_label.grid(row=0, column=col, padx=2, pady=2)

    # Lấy ngày đầu tiên của tháng và xác định thứ (0 = Thứ hai, 6 = Chủ nhật)
    first_day = datetime(year, month, 1)
    start_day = (first_day.weekday())  # weekday() trả về 0=Mon, 6=Sun; phù hợp với cách hiển thị lịch

    # Lấy số ngày trong tháng
    days_in_month = calendar.monthrange(year, month)[1]

    # Bắt đầu hiển thị ngày từ cột tương ứng với start_day
    row = 1
    col = start_day
    for day in range(1, days_in_month + 1):
        date_str = f"{month:02}/{day:02}/{year}"
        is_selected = selected_date == date_str
        bg_color = "#444444" if not is_selected else "#FF8C00"
        text_color = "white" if not is_selected else "black"

        # Tạo ô hiển thị ngày
        day_label = ctk.CTkLabel(calendar_frame, text=str(day), font=("Arial", 12),  # Giảm kích thước chữ
                                 fg_color=bg_color, text_color=text_color, width=60, height=30, corner_radius=4)
        day_label.grid(row=row, column=col, padx=2, pady=2)
        day_label.bind("<Button-1>", lambda e, d=date_str: on_day_selected(d))

        # Tăng cột, xuống hàng nếu cần
        col += 1
        if col > 6:
            col = 0
            row += 1

# Hàm cập nhật lịch
def update_calendar(event=None):
    try:
        year = int(entry_year.get())
        month = int(entry_month.get())
        if 1 <= month <= 12:
            generate_calendar(year, month)
        else:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Vui lòng nhập năm và tháng hợp lệ!")

selected_date = None
    
def on_day_selected(date_str):
    global selected_date
    selected_date = date_str
    year = int(entry_year.get())
    month = int(entry_month.get())
    generate_calendar(year, month, selected_date)

# Mở cửa sổ thêm sự kiện
def open_add_event_window(selected_date):
    event_window = Toplevel(app)
    event_window.title("Add Event")
    event_window.geometry("450x450")

    # Gợi ý nhập liệu với màu chữ đen
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

    # Hàm lưu sự kiện
    def save_event():
        time = entry_time.get()
        title = entry_title.get()
        content = entry_content.get()

        if not time or not title or not content:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

    # Chuyển đổi selected_date về định dạng chuẩn
        selected_date_normalized = datetime.strptime(selected_date, "%m/%d/%Y").strftime("%m/%d/%Y")

        if selected_date_normalized not in events:
            events[selected_date_normalized] = []

        events[selected_date_normalized].append({"time": time, "title": title, "content": content})
        save_events()  # Lưu sự kiện vào file
        messagebox.showinfo("Success", "Event added successfully!")
    
        # Cập nhật khung hiển thị các sự kiện trong hôm nay và 24h tiếp theo
        display_upcoming_events()  # Cập nhật lại danh sách sự kiện sắp tới

        # Đóng cửa sổ sau khi lưu
        event_window.destroy()  


    # Nút lưu sự kiện
    button_save = ctk.CTkButton(event_window, text="Save Event", command=save_event)
    button_save.pack(pady=10)

    # Căn chỉnh kích thước cửa sổ cho phù hợp
    event_window.update_idletasks()  # Cập nhật kích thước cửa sổ
    event_window.minsize(event_window.winfo_width(), event_window.winfo_height())  # Đặt kích thước tối thiểu

# Cập nhật hàm thêm sự kiện
def on_add_event():
    global selected_date
    if not selected_date:
        messagebox.showerror("Error", "No date selected! Please select a date.")
        return
    open_add_event_window(selected_date)

# Hàm hiển thị sự kiện trong ngày đang chọn
def view_events():
    global selected_date
    if not selected_date:
        messagebox.showerror("Error", "No date selected! Please select a date.")
        return

    # Kiểm tra nếu có sự kiện trong ngày đã chọn
    if selected_date in events and events[selected_date]:
        event_list = events[selected_date]
        message = f"Events on {selected_date}:\n\n"
        for i, event in enumerate(event_list, 1):
            message += f"{i}. {event['time']} - {event['title']}\n   {event['content']}\n\n"
    else:
        message = f"No events on {selected_date}."

    # Hiển thị danh sách sự kiện
    messagebox.showinfo("Events", message)

# Hàm mở cửa sổ xóa sự kiện
def open_delete_event_window():
    global selected_date
    if not selected_date:
        messagebox.showerror("Error", "No date selected! Please select a date.")
        return

    # Kiểm tra nếu ngày được chọn có sự kiện
    if selected_date not in events or not events[selected_date]:
        messagebox.showinfo("No Events", f"No events found on {selected_date}.")
        return

    # Tạo cửa sổ xóa sự kiện
    delete_window = Toplevel(app)
    delete_window.title("Delete Event")
    delete_window.geometry("500x500")

    # Frame chứa Listbox và Scrollbar
    listbox_frame = ctk.CTkFrame(delete_window)
    listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Thanh trượt dọc
    scrollbar = Scrollbar(listbox_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    # Tạo danh sách sự kiện
    listbox_events = Listbox(
        listbox_frame,
        height=12,
        width=50,
        selectmode="single",
        font=("Arial", 14),
        yscrollcommand=scrollbar.set
    )
    listbox_events.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=listbox_events.yview)

    # Điền dữ liệu vào Listbox
    for i, event in enumerate(events[selected_date], 1):
        listbox_events.insert(END, f"{i}. {event['time']} - {event['title']}")

    # Hàm xử lý xóa sự kiện
    def delete_event():
        try:
            selected_index = listbox_events.curselection()[0]
            events[selected_date].pop(selected_index)
            save_events()
            display_upcoming_events()

            if not events[selected_date]:  # Nếu ngày không còn sự kiện, xóa ngày
                del events[selected_date]

            messagebox.showinfo("Success", "Event deleted successfully!")
            delete_window.destroy()
        except IndexError:
            messagebox.showerror("Error", "Please select an event to delete.")

    # Nút xóa sự kiện
    button_delete = ctk.CTkButton(delete_window, text="Delete Selected Event", command=delete_event)
    button_delete.pack(pady=(5, 10))

def open_edit_event_window(selected_date):
    global events
    if selected_date not in events or not events[selected_date]:
        messagebox.showerror("Error", f"No events found for {selected_date}.")
        return

    # Mở cửa sổ chọn sự kiện
    edit_window = Toplevel(app)
    edit_window.title(f"Edit Event - {selected_date}")
    edit_window.geometry("500x500")

    # Frame chứa Listbox và Scrollbar
    listbox_frame = ctk.CTkFrame(edit_window)
    listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Thanh trượt dọc
    scrollbar = Scrollbar(listbox_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    # Hiển thị danh sách các sự kiện để chọn
    event_listbox = Listbox(
        listbox_frame,
        font=("Arial", 14),
        height=12,
        width=50,
        selectmode="single",
        yscrollcommand=scrollbar.set
    )
    event_listbox.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=event_listbox.yview)

    # Thêm các sự kiện vào Listbox
    for idx, event in enumerate(events[selected_date], 1):
        event_listbox.insert(END, f"{idx}. {event['time']} - {event['title']}")

    # Hàm chỉnh sửa sự kiện
    def edit_selected_event():
        selected_index = event_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select an event to edit!")
            return

        event_index = selected_index[0]
        event_to_edit = events[selected_date][event_index]

        # Mở cửa sổ chỉnh sửa sự kiện
        edit_event_window = Toplevel(edit_window)
        edit_event_window.title("Edit Event Details")
        edit_event_window.geometry("500x500")

        # Tạo các trường nhập liệu
        label_time = ctk.CTkLabel(edit_event_window, text="Time :", text_color="black", font=("Arial", 14))
        label_time.pack(pady=5)
        entry_time = ctk.CTkEntry(edit_event_window, font=("Arial", 14))
        entry_time.insert(0, event_to_edit['time'])
        entry_time.pack(pady=5)

        label_title = ctk.CTkLabel(edit_event_window, text="Event Title:", text_color="black", font=("Arial", 14))
        label_title.pack(pady=5)
        entry_title = ctk.CTkEntry(edit_event_window, font=("Arial", 14))
        entry_title.insert(0, event_to_edit['title'])
        entry_title.pack(pady=5)

        label_content = ctk.CTkLabel(edit_event_window, text="Event Content:", text_color="black", font=("Arial", 14))
        label_content.pack(pady=5)
        entry_content = ctk.CTkEntry(edit_event_window, font=("Arial", 14))
        entry_content.insert(0, event_to_edit['content'])
        entry_content.pack(pady=5)

        # Hàm lưu sự kiện sau khi chỉnh sửa
        def save_edited_event():
            new_time = entry_time.get()
            new_title = entry_title.get()
            new_content = entry_content.get()
            if not new_time or not new_title or not new_content:
                messagebox.showerror("Error", "Please fill in all fields!")
                return

            # Cập nhật sự kiện
            events[selected_date][event_index] = {
                "time": new_time,
                "title": new_title,
                "content": new_content
            }
            save_events()
            display_upcoming_events()
            messagebox.showinfo("Success", "Event updated successfully!")
            edit_event_window.destroy()
            edit_window.destroy()

        # Nút lưu sự kiện sau khi chỉnh sửa
        button_save = ctk.CTkButton(edit_event_window, text="Save Changes", command=save_edited_event, font=("Arial", 14))
        button_save.pack(pady=10)

    # Nút để chỉnh sửa sự kiện đã chọn
    button_edit = ctk.CTkButton(edit_window, text="Edit Selected Event", command=edit_selected_event, font=("Arial", 14))
    button_edit.pack(pady=(5, 10))

# Hàm lấy các sự kiện trong ngày hôm nay và 24 giờ tiếp theo
def get_upcoming_events():
    now = datetime.now()
    today_str = now.strftime("%m/%d/%Y")
    next_day = now + timedelta(days=1)
    next_day_str = next_day.strftime("%m/%d/%Y")

    upcoming_events = []
    for date_str, day_events in events.items():
        if today_str <= date_str <= next_day_str:  # Lọc các sự kiện trong 24 giờ tới
            for event in day_events:
                try:
                    # Gộp ngày và thời gian của sự kiện thành một đối tượng datetime
                    event_datetime = datetime.strptime(f"{date_str} {event['time']}", "%m/%d/%Y %I:%M%p")
                except ValueError:
                    try:
                        # Nếu thời gian không có AM/PM, thử chuyển đổi từ 24-hour format sang 12-hour format
                        event_time_24 = datetime.strptime(event['time'], "%H:%M")
                        event_time_12 = event_time_24.strftime("%I:%M%p")
                        event_datetime = datetime.strptime(f"{date_str} {event_time_12}", "%m/%d/%Y %I:%M%p")
                    except ValueError:
                        # Nếu vẫn không thành công, bỏ qua sự kiện này
                        continue

                # Thêm sự kiện vào danh sách
                upcoming_events.append({
                    "datetime": event_datetime,  # Thêm datetime để sắp xếp
                    "date": date_str,
                    "time": event["time"],
                    "title": event["title"],
                    "content": event["content"]
                })

    # Sắp xếp danh sách sự kiện dựa trên `datetime`
    upcoming_events.sort(key=lambda x: x["datetime"])
    return upcoming_events

# Hàm hiển thị sự kiện trong hôm nay và trong 24 giờ tiếp theo
def display_upcoming_events():
    # Xóa nội dung cũ trong khung hiển thị
    for widget in events_display_frame.winfo_children():
        widget.destroy()

    # Điều chỉnh kích thước khung hiển thị xuống 70%
    events_display_frame.configure(width=int(app.winfo_width() * 0.7), height=int(app.winfo_height() * 0.7))

    # Tạo Text widget với Scrollbar
    scrollbar = Scrollbar(events_display_frame, orient="vertical")
    text_widget = Text(
        events_display_frame,
        wrap="word",  # Tự động xuống dòng
        yscrollcommand=scrollbar.set,  # Kết nối thanh trượt
        bg="#222222",  # Màu nền tương tự khung
        fg="white",    # Màu chữ trắng
        font=("Arial", 14),  # Font chữ lớn hơn
        relief="flat",  # Loại bỏ viền 3D
        height=20,      # Đặt chiều cao hợp lý
        width=70,       # Đặt chiều rộng hợp lý
    )
    scrollbar.config(command=text_widget.yview)

    # Đặt thanh trượt và Text widget vào khung
    scrollbar.pack(side="right", fill="y")
    text_widget.pack(side="left", fill="both", expand=True)

    # Lấy các sự kiện trong hôm nay và 24 giờ tới
    upcoming_events = get_upcoming_events()

    if not upcoming_events:
        message = "No upcoming events (Today & Tomorrow)."
    else:
        message = "Upcoming Events (Today & Tomorrow):\n\n"
        for event in upcoming_events:
            message += f"{event['date']} - {event['time']} - {event['title']}\n   {event['content']}\n\n"

    # Chèn nội dung vào Text widget
    text_widget.insert("1.0", message)

    # Căn giữa văn bản
    text_widget.tag_configure("center", justify="center")
    text_widget.tag_add("center", "1.0", "end")

    # Vô hiệu hóa chỉnh sửa nội dung
    text_widget.config(state="disabled")

# Giao diện chính
frame_controls = ctk.CTkFrame(app,fg_color="#222222")
frame_controls.pack(pady=10, padx=10)

label_year = ctk.CTkLabel(frame_controls, text="Year:")
label_year.pack(side="left", padx=5)
entry_year = ctk.CTkEntry(frame_controls, width=80)
entry_year.pack(side="left", padx=5)

label_month = ctk.CTkLabel(frame_controls, text="Month:")
label_month.pack(side="left", padx=5)
entry_month = ctk.CTkEntry(frame_controls, width=50)
entry_month.pack(side="left", padx=5)

button_update = ctk.CTkButton(frame_controls, text="Update", command=update_calendar)
button_update.pack(side="left", padx=10)

# Cho phép người dùng nhấn Enter để cập nhật lịch
entry_year.bind("<Return>", update_calendar)
entry_month.bind("<Return>", update_calendar)

calendar_frame = ctk.CTkFrame(app, fg_color="#222222")
calendar_frame.pack(pady=10, padx=10)

# Cập nhật lại bố cục của các nút trong frame_event
frame_event = ctk.CTkFrame(app,fg_color="#222222")
frame_event.pack(pady=10, padx=10)

# Sử dụng frame con để chia bố cục thành hai phần: trái và phải
frame_left = ctk.CTkFrame(frame_event)
frame_left.pack(side="left", padx=20)

frame_right = ctk.CTkFrame(frame_event)
frame_right.pack(side="left", padx=20)

# Nút Add Event và View Event (Nằm bên trái)
button_add = ctk.CTkButton(frame_left, text="Add Event", command=on_add_event)
button_add.pack(pady=5)

button_view = ctk.CTkButton(frame_left, text="View Event", command=view_events)
button_view.pack(pady=5)

# Nút Edit Event và Delete Event (Nằm bên phải)
button_edit_event = ctk.CTkButton(frame_right, text="Edit Event", command=lambda: open_edit_event_window(selected_date))
button_edit_event.pack(pady=5)

button_delete_event = ctk.CTkButton(frame_right, text="Delete Event", command= open_delete_event_window)
button_delete_event.pack(pady=5)

# Khung hiển thị các sự kiện trong 24 giờ tới
events_display_frame = ctk.CTkFrame(app,fg_color="#222222")
events_display_frame.pack(pady=10, padx=10)

load_events()
normalize_dates()
now = datetime.now()
entry_year.insert(0, str(now.year))
entry_month.insert(0, str(now.month))
generate_calendar(now.year, now.month)
display_upcoming_events()
app.mainloop()