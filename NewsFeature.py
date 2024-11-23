import requests
import feedparser
import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk
import webbrowser
from io import BytesIO
from bs4 import BeautifulSoup
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


class NewsApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.gradient_colors = {
            "Giải trí": ("#FF6B6B", "#4ECDC4"),
            "Thể thao": ("#FFA726", "#FF5722"),
            "Công nghệ": ("#4A90E2", "#50E3C2"),
            "Kinh tế": ("#9C27B0", "#673AB7"),
            "Chính trị": ("#304FFE", "#1A237E")
        }

        self.app = ctk.CTk()
        self.app.title("Tin tức mới nè bà con")
        self.app.geometry("1100x800")

        self.topics = {
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
        }

        self.setup_ui()
        self.load_initial_topic()

    def setup_ui(self):
        header = ctk.CTkFrame(self.app, corner_radius=10)
        header.pack(fill="x", pady=10, padx=10)
        title = ctk.CTkLabel(header, text="Tin Tức nóng hổi", font=("Segoe UI", 24, "bold"))
        title.pack(pady=10)

        self.category_frame = ctk.CTkFrame(self.app, corner_radius=10)
        self.category_frame.pack(fill="x", pady=10, padx=10)

        button_wrapper = ctk.CTkFrame(self.category_frame, fg_color="transparent")
        button_wrapper.pack(expand=True)

        for topic in self.topics.keys():
            button = ctk.CTkButton(
                button_wrapper,
                text=topic,
                command=lambda t=topic: self.load_topic(t),
                fg_color=self.gradient_colors.get(topic, ("#4A90E2", "#50E3C2"))[0],
                hover_color=self.gradient_colors.get(topic, ("#4A90E2", "#50E3C2"))[1]
            )
            button.pack(side="left", padx=5)

        self.news_frame = ctk.CTkScrollableFrame(self.app, corner_radius=10)
        self.news_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_initial_topic(self):
        self.load_topic(list(self.topics.keys())[0])

    def load_topic(self, topic_name):
        for widget in self.news_frame.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.news_frame,
            text=f"Đang tải tin tức {topic_name}...",
            font=("Segoe UI", 18, "bold")
        )
        loading_label.pack(pady=20)

        def fetch_articles():
            all_articles = []
            sources = self.topics.get(topic_name, [])

            with ThreadPoolExecutor(max_workers=len(sources)) as executor:
                futures = [executor.submit(self.fetch_rss, source['url']) for source in sources]

                for future in as_completed(futures):
                    articles = future.result()
                    all_articles.extend(articles)

            self.app.after(0, lambda: self.display_articles(all_articles))

        threading.Thread(target=fetch_articles, daemon=True).start()

    def fetch_rss(self, url):
        try:
            feed = feedparser.parse(url)
            return [self.extract_article_details(entry) for entry in feed.entries[:10]]
        except Exception as e:
            logging.error(f"RSS Fetch Error for {url}: {e}")
            return []

    def extract_article_details(self, article):
        try:
            image_url = self.get_featured_image(article.get('link', ''))

            return {
                'title': article.get('title', 'Không có tiêu đề'),
                'description': self.truncate_description(article.get('summary', 'Không có mô tả')),
                'link': article.get('link', '#'),
                'published': article.get('published', 'Không rõ ngày'),
                'image_url': image_url
            }
        except Exception as e:
            logging.error(f"Không thể truy cập để lấy tiêu đề: {e}")
            return None

    def get_featured_image(self, article_url):
        try:
            response = requests.get(article_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')

            image_sources = [
                soup.find('meta', property='og:image'),
                soup.find('link', rel='image_src'),
                soup.find('meta', attrs={'name': 'twitter:image'})
            ]

            for source in image_sources:
                if source and source.get('content'):
                    return source['content']

            first_image = soup.find('img')
            return first_image['src'] if first_image and first_image.get('src') else None

        except Exception as e:
            logging.warning(f"Image fetch error for {article_url}: {e}")
            return None

    def load_image(self, image_url):
        try:
            if not image_url:
                return None

            response = requests.get(image_url, timeout=5)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((150, 100), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_data)
        except Exception as e:
            logging.error(f"Image load error: {e}")
            return None

    def truncate_description(self, description, max_length=250):
        description = BeautifulSoup(description, 'html.parser').get_text()
        description = description.strip()

        if not description:
            return "Không có mô tả chi tiết"

        if len(description) > max_length:
            truncated = description[:max_length]
            last_space = truncated.rfind(' ')

            if last_space != -1:
                description = truncated[:last_space] + '...'
            else:
                description = truncated + '...'

        return description

    def display_articles(self, articles):
        for widget in self.news_frame.winfo_children():
            widget.destroy()

        if not articles:
            no_articles_label = ctk.CTkLabel(
                self.news_frame,
                text="Không tìm thấy bài viết nào.",
                font=("Segoe UI", 16)
            )
            no_articles_label.pack(pady=20)
            return

        sorted_articles = sorted(
            [a for a in articles if a],
            key=lambda x: x.get('published', ''),
            reverse=True
        )

        for article in sorted_articles:
            try:
                custom_font_family = "Segoe UI"

                card = ctk.CTkFrame(
                    self.news_frame,
                    corner_radius=10,
                    fg_color="#252525"
                )
                card.pack(fill="x", pady=5, padx=5)
                card.columnconfigure(1, weight=1)

                image_photo = self.load_image(article['image_url'])
                if image_photo:
                    img_label = tk.Label(card, image=image_photo)
                    img_label.image = image_photo
                    img_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")

                title_label = ctk.CTkLabel(
                    card,
                    text=article['title'],
                    font=(custom_font_family, 18, "bold"),
                    wraplength=600,
                    justify="left",
                    anchor="w",
                    text_color="#FFFFFF",
                    cursor="hand2"
                )
                title_label.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))


                title_label.bind("<Button-1>", lambda e, link=article['link']: webbrowser.open(link))

                desc_label = ctk.CTkLabel(
                    card,
                    text=article['description'],
                    font=(custom_font_family, 14, "normal"),
                    wraplength=600,
                    justify="left",
                    anchor="w"
                )
                desc_label.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 5))

            except Exception as e:
                logging.error(f"Article display error: {e}")

    def run(self):
        self.app.mainloop()


def main():
    logging.basicConfig(level=logging.ERROR)
    app = NewsApp()
    app.run()


if __name__ == "__main__":
    main()
