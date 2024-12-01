import re
import threading
import webbrowser
from urllib.parse import urljoin
import feedparser
import customtkinter as ctk
import concurrent.futures
from bs4 import BeautifulSoup
import os
import hashlib
import logging
import requests
from PIL import Image, ImageTk
from io import BytesIO
from collections import OrderedDict
from typing import Optional
from queue import Queue



import os
import hashlib
import threading
import logging
from queue import Queue
from collections import OrderedDict
from PIL import Image, ImageTk
from io import BytesIO
import requests
from typing import Optional
import time


class ImageCacheManager:
    def __init__(self, cache_dir='./image_cache', max_size=100):
        self.cache_dir = cache_dir
        self.max_size = max_size
        os.makedirs(cache_dir, exist_ok=True)
        self._memory_cache = OrderedDict()
        self._work_queue = Queue()
        self._start_worker()
        self._start_cleanup_task()

    def _start_worker(self):
        def worker():
            while True:
                url, callback = self._work_queue.get()
                if url is None:
                    break
                image = self._download_and_process_image(url)
                callback(image)
                self._work_queue.task_done()

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _start_cleanup_task(self):
        def cleanup():
            while True:
                time.sleep(300)
                self._clean_cache()

        threading.Thread(target=cleanup, daemon=True).start()

    def _clean_cache(self):
        try:
            cache_files = [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir)]
            cache_files.sort(key=os.path.getmtime)
            while len(cache_files) > self.max_size:
                oldest = cache_files.pop(0)
                os.remove(oldest)
                logging.info(f"Removed old cache file: {oldest}")
        except Exception as e:
            logging.error(f"Error during cache cleanup: {e}")

    def load_image_async(self, image_url: str, callback):
        self._work_queue.put((image_url, callback))

    def _download_and_process_image(self, image_url: str):
        try:
            response = requests.get(image_url, timeout=5)
            img_data = Image.open(BytesIO(response.content))
            img_data.thumbnail((150, 100), Image.Resampling.LANCZOS)
            return img_data
        except Exception as e:
            logging.error(f"Error downloading image: {e}")
            return None

    def load_image(self, image_url: str) -> Optional[ImageTk.PhotoImage]:
        if threading.current_thread() != threading.main_thread():
            logging.warning("Attempted to load image from non-main thread.")
            return None

        cached_image = self.get_cached_image(image_url)
        if cached_image:
            return cached_image

        try:
            if not image_url:
                return None

            response = requests.get(image_url, timeout=5)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((150, 100), Image.Resampling.LANCZOS)

            photo_image = ImageTk.PhotoImage(img_data)
            self.cache_image(image_url, img_data)
            return photo_image
        except Exception as e:
            logging.error(f"Image load error: {e}")
            return None

    def get_cached_image(self, url: str) -> Optional[ImageTk.PhotoImage]:
        if not url:
            return None

        key = hashlib.md5(url.encode()).hexdigest()
        if threading.current_thread() != threading.main_thread():
            logging.warning("Attempted to access cached image from non-main thread.")
            return None
        if key in self._memory_cache:
            self._memory_cache.move_to_end(key)
            return self._memory_cache[key]

        cache_path = os.path.join(self.cache_dir, f"{key}.webp")
        if os.path.exists(cache_path):
            try:
                image = Image.open(cache_path)
                photo_image = ImageTk.PhotoImage(image)

                self._memory_cache[key] = photo_image
                self._ensure_cache_size()
                return photo_image
            except Exception as e:
                logging.warning(f"Cache retrieval error: {e}")

        return None

    def cache_image(self, url: str, image: Image.Image):
        key = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{key}.webp")

        if key not in self._memory_cache:
            self._memory_cache[key] = ImageTk.PhotoImage(image)
            self._ensure_cache_size()

        if not os.path.exists(cache_path):
            try:
                image.save(cache_path, format='WEBP')
            except Exception as e:
                logging.error(f"Error saving image to cache: {e}")

    def _ensure_cache_size(self):
        while len(self._memory_cache) > self.max_size:
            self._memory_cache.popitem(last=False)




class NewsPanel(ctk.CTkFrame):
    def __init__(self, parent, topics, gradient_colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.topics = topics
        self.gradient_colors = gradient_colors
        self.app = parent
        self.image_cache = ImageCacheManager()
        self.setup_ui_for_News()


    def cache_images_for_articles(self, articles, executor):
        image_futures = {
            executor.submit(self.image_cache.load_image, article.get('image_url')): article
            for article in articles if article.get('image_url')
        }
        for future in concurrent.futures.as_completed(image_futures):
            try:
                _ = future.result()
            except Exception as e:
                logging.warning(f"Error caching image: {e}")


    def setup_ui_for_News(self):
        self.category_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#F0F4F8"
        )
        self.category_frame.pack(fill="x", pady=(15, 10), padx=15)

        button_wrapper = ctk.CTkFrame(
            self.category_frame,
            fg_color="transparent"
        )
        button_wrapper.pack(expand=True, pady=10)

        for topic in self.topics.keys():
            button = ctk.CTkButton(
                button_wrapper,
                text=topic,
                command=lambda t=topic: self.load_topic(t),
                corner_radius=15,
                fg_color="white",
                text_color=self.gradient_colors.get(topic, ("#4A90E2", "#50E3C2"))[0],
                hover_color="#E0E0E0",
                border_width=2,
                border_color=self.gradient_colors.get(topic, ("#4A90E2", "#50E3C2"))[0],
            font= ("Inter", 16, 'bold'),
            )
            button.pack(side="left", padx=5)

        self.news_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=20,
            fg_color="white"
        )
        self.news_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))

    def load_topic(self, topic_name):
        for widget in self.news_frame.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.news_frame,
            text=f"Đang tải tin tức {topic_name}...",
            font=("Inter", 18, "bold")
        )
        loading_label.pack(pady=20)

        def fetch_articles():
            all_articles = []
            sources = self.topics.get(topic_name, [])
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                article_futures = [executor.submit(self.fetch_rss, source['url']) for source in sources]
                for future in concurrent.futures.as_completed(article_futures):
                    all_articles.extend(future.result())

                image_futures = {
                    executor.submit(self.image_cache.load_image, article.get('image_url')): article
                    for article in all_articles if article.get('image_url')
                }
                for future in concurrent.futures.as_completed(image_futures):
                    article = image_futures[future]
                    try:
                        article['image'] = future.result()
                    except Exception:
                        article['image'] = None

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
            response = requests.get(article_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            image_selectors = [
                lambda: soup.find('meta', property='og:image', content=True),
                lambda: soup.find('meta', attrs={'name': 'twitter:image'}, content=True),
                lambda: soup.find('link', rel='image_src', href=True),
                lambda: soup.find('img', class_=re.compile('featured|main|hero', re.I)),
                lambda: soup.find('img', src=re.compile(r'\.(jpg|jpeg|png|gif)$'))
            ]

            for selector in image_selectors:
                result = selector()
                if result:
                    img_url = result.get('content') or result.get('href') or result.get('src')
                    return self.normalize_url(img_url, article_url)

            return None

        except Exception as e:
            logging.warning(f"Image fetch error for {article_url}: {e}")
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
                font=("Inter", 16, "italic"),
                text_color="gray"
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
                card = ctk.CTkFrame(
                    self.news_frame,
                    corner_radius=15,
                    fg_color="white",
                    border_width=1,
                    border_color="#E0E0E0"
                )
                card.pack(fill="x", pady=8, padx=5)
                card.columnconfigure(1, weight=1)

                image_photo = article.get('image') or self.image_cache.load_image(article['image_url'])
                if image_photo:
                    img_label = ctk.CTkLabel(
                        card,
                        image=image_photo,
                        text=""
                    )
                    img_label.image = image_photo
                    img_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")
                else:
                    placeholder_label = ctk.CTkLabel(
                        card,
                        text="📰",
                        font=("Inter", 40),
                        text_color="gray"
                    )
                    placeholder_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")
                title_label = ctk.CTkLabel(
                    card,
                    text=article['title'],
                    font=("Inter", 16, "bold"),
                    wraplength=600,
                    justify="left",
                    anchor="w",
                    text_color="#333333",
                    cursor="hand2"
                )
                title_label.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))

                title_label.bind("<Button-1>", lambda e, link=article['link']: webbrowser.open(link))
                title_label.bind("<Enter>", lambda e, label=title_label: label.configure(text_color="#2196F3"))
                title_label.bind("<Leave>", lambda e, label=title_label: label.configure(text_color="#333333"))

                desc_label = ctk.CTkLabel(
                    card,
                    text=article['description'],
                    font=("Inter", 14, "normal"),
                    wraplength=600,
                    justify="left",
                    anchor="w",
                    text_color="gray"
                )
                desc_label.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 10))

            except Exception as e:
                logging.error(f"Article display error: {e}")

    def normalize_url(self, url, base_url):
        if url and not url.startswith(('http://', 'https://')):
            return urljoin(base_url, url)
        return url