import tkinter as tk
from tkinter import scrolledtext
import subprocess
import re
from googletrans import Translator
import os

path = os.getcwd()

class ChatApp:
    def __init__(self, root, history_file="bin/log/chat_history.txt"):
        self.root = root
        self.history_file = history_file  # فایل ذخیره تاریخچه پیام‌ها
        self.root.title("ongpt")
        self.root.geometry("650x750")  # تغییر اندازه پنجره
        self.root.config(bg="#f0f0f5")  # پس‌زمینه روشن و مدرن

        # رنگ‌ها
        self.primary_color = "#007aff"  # آبی مک
        self.secondary_color = "#ffffff"  # سفید
        self.chat_bg_color = "#ffffff"  # پس‌زمینه چت سفید
        self.button_hover_color = "#5e5bff"  # رنگ دکمه در حالت هاور

        # نام پیش‌فرض برای ابزار
        self.bot_name = "ONGPT"

        # ترجمه‌کننده (Google Translate API)
        self.translator = Translator()

        # طراحی نوار عنوان
        self.title_label = tk.Label(root, text="Chat with ongpt", font=("SF Pro Display", 20, "bold"), bg=self.primary_color, fg=self.secondary_color, relief="flat", pady=12)
        self.title_label.pack(fill=tk.X)

        # منوی کشویی انتخاب زبان
        self.language_label = tk.Label(root, text="Select your language:", font=("SF Pro Display", 12), bg=self.primary_color, fg=self.secondary_color)
        self.language_label.pack(pady=10)
        
        self.language_var = tk.StringVar(value="en")  # پیش‌فرض زبان انگلیسی
        self.language_dropdown = tk.OptionMenu(root, self.language_var, "en", "fa", "tr")  # زبان‌ها
        self.language_dropdown.config(font=("SF Pro Display", 12), bg=self.secondary_color, width=12, anchor="center", relief="flat")
        self.language_dropdown.pack(pady=5)

        # ایجاد بخش نمایش چت
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, font=("SF Pro Display", 14), bg=self.chat_bg_color, fg="#333333", bd=0, relief="flat", insertbackground="black", padx=15, pady=15)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # ارتفاع ریسپانسیو برای chat_area

        # فیلد ورودی پیام (بدون محدودیت)
        self.entry = tk.Text(root, width=60, height=4, font=("SF Pro Display", 14), bg=self.secondary_color, fg="#333333", bd=0, relief="flat", wrap=tk.WORD, insertbackground="black", padx=15, pady=10)
        self.entry.pack(fill=tk.X, padx=20, pady=10)  # عرض ریسپانسیو برای entry

        # دکمه ارسال
        self.send_button = tk.Button(root, text="Send", command=self.send_message, font=("SF Pro Display", 14, "bold"), bg=self.primary_color, fg=self.secondary_color, bd=0, relief="flat", width=12, height=2, activebackground=self.button_hover_color)
        self.send_button.pack(pady=15)

        # اضافه کردن انیمیشن یا افکت‌ها (اختیاری)
        self.root.after(500, self.show_welcome_message)

        # خواندن تاریخچه چت از فایل
        self.load_chat_history()

        # اتصال رویداد Ctrl+C
        self.root.bind('<Control-c>', self.handle_ctrl_c)
        # اتصال رویداد Ctrl+W
        self.root.bind('<Control-w>', self.show_exit_warning)

    def handle_ctrl_c(self, event):
        # تابع برای انجام عملی که در صورت فشردن Ctrl + C انجام می‌دهیم
        selected_text = self.chat_area.get(tk.SEL_FIRST, tk.SEL_LAST)  # متن انتخاب‌شده در چت
        if selected_text:
            self.root.clipboard_clear()  # پاک کردن کلیپ‌بورد قبلی
            self.root.clipboard_append(selected_text)  # اضافه کردن متن انتخابی به کلیپ‌بورد
            self.update_chat("System@One_Exploit~# Text copied to clipboard.")  # پیغام کپی شدن متن

    def show_exit_warning(self, event):
        from tkinter import messagebox
        import time
        # نمایش پیام هشدار برای بستن برنامه
        self.close = messagebox.askyesno("Warning", "Are you sure you want to exit the application?")
        if self.close != False:  # جلوگیری از عملکرد پیش‌فرض Ctrl+W (که معمولاً برای بستن پنجره است)
            messagebox.Message.show()
            time.sleep(3)
            root.quit()



    def show_welcome_message(self):
        # نمایش پیغام خوشامدگویی اولیه
        self.update_chat(f"System@One_Exploit~# Hi! . (You can call me {self.bot_name}!)")

    def send_message(self):
        user_message = self.entry.get("1.0", tk.END).strip()  # دریافت پیام از فیلد Text
        if user_message:
            # شناسایی دستورات خاص
            if self.is_special_command(user_message):
                self.execute_special_command(user_message)
                return  # از ارسال پیام به tgpt جلوگیری می‌شود

            # انتخاب زبان مورد نظر کاربر
            selected_language = self.language_var.get()

            # بررسی اعتبار زبان انتخابی
            if not self.is_valid_language(selected_language):
                self.update_chat("زبان انتخابی معتبر نیست. لطفاً زبان صحیحی انتخاب کنید.")
                return

            # ترجمه پیام به انگلیسی (در صورتی که زبان کاربر غیر از انگلیسی باشد)
            if selected_language != "en":
                translated_message = self.translate_to_english(user_message, selected_language)
                user_message = translated_message  # پیام ترجمه شده را به ابزار می‌دهیم

            # نمایش پیام کاربر در پنجره چت
            self.update_chat("You: " + user_message)

            # ارسال پیام به ترمینال و دریافت پاسخ
            response = self.get_response_from_terminal(user_message)

            # فیلتر کردن کاراکترهای Loading از پاسخ سیستم
            filtered_response = self.filter_loading(response)

            # ترجمه پاسخ به زبان انتخابی کاربر
            if selected_language != "en":
                filtered_response = self.translate_from_english(filtered_response, selected_language)

            # نمایش پاسخ سیستم (بدون کلمه "Loading")
            self.update_chat("System@One_Exploit~# " + filtered_response)

            # ذخیره پیام‌ها و پاسخ‌ها در فایل
            self.save_to_history(user_message, filtered_response)

        # پاک کردن فیلد ورودی
        self.entry.delete("1.0", tk.END)

    def is_special_command(self, message):
        # بررسی دستورات خاص مانند پاک کردن تاریخچه
        if message.lower() == "del history | create -file":
            return True
        return False

    def execute_special_command(self, command):
        # اجرای دستورات خاص مانند پاک کردن تاریخچه چت
        if command.lower() == "del history | create -file":
            self.delete_history_file()
            self.update_chat("System@One_Exploit~# Chat history file has been cleared and recreated.")

            # پس از 3 ثانیه، صفحه چت را رفرش می‌کنیم
            self.root.after(3000, self.refresh_chat)  # 3000 میلی‌ثانیه = 3 ثانیه

    def delete_history_file(self):
        # حذف فایل تاریخچه چت و ایجاد دوباره آن
        if os.path.exists(self.history_file):
            os.remove(self.history_file)  # حذف فایل
        # ایجاد فایل جدید با نام تاریخچه چت
        with open(self.history_file, "w", encoding="utf-8") as file:
            file.write("")  # فایل خالی است، بعداً داده‌ها به آن اضافه می‌شود

    def refresh_chat(self):
        # پس از 3 ثانیه، صفحه چت را رفرش می‌کنیم
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)  # پاک کردن تمام محتوای موجود در صفحه چت
        self.load_chat_history()  # بارگذاری تاریخچه جدید

    def update_chat(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + "\n\n")
        self.chat_area.yview(tk.END)  # اسکرول به پایین برای نمایش پیام جدید
        self.chat_area.config(state=tk.DISABLED)

    def get_response_from_terminal(self, user_message):
        try:
            # اجرای دستور در ترمینال (به جای این خط، دستور مرتبط با tgpt خود را وارد کنید)
            process = subprocess.Popen(["tgpt", user_message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if stderr:
                return "Error: " + stderr.decode()
            return stdout.decode()

        except Exception as e:
            return f"Error: {str(e)}"

    def filter_loading(self, response):
        # استفاده از regex برای حذف خطوط Loading و کاراکترهای اضافی
        filtered_response = re.sub(r"[\s⣾⣽⣻⢿⡿⣟⣯⣷]+Loading", "", response)
        return filtered_response.strip()

    def translate_to_english(self, message, src_language):
        try:
            translated = self.translator.translate(message, src=src_language, dest='en')
            return translated.text
        except Exception as e:
            self.update_chat(f"خطا در ترجمه به انگلیسی: {str(e)}")
            return message  # در صورت خطا، پیام اصلی را برمی‌گردانیم

    def translate_from_english(self, message, target_language):
        try:
            translated = self.translator.translate(message, src='en', dest=target_language)
            return translated.text
        except Exception as e:
            self.update_chat(f"خطا در ترجمه از انگلیسی: {str(e)}")
            return message  # در صورت خطا، پیام اصلی را برمی‌گردانیم

    def load_chat_history(self):
        # خواندن تاریخچه چت از فایل و نمایش آن در پنجره چت
        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                chat_history = file.readlines()

            for line in chat_history:
                self.update_chat(line.strip())  # نمایش هر خط از تاریخچه چت

        except FileNotFoundError:
            pass  # اگر فایل وجود ندارد، مشکلی پیش نمی‌آید

    def save_to_history(self, user_message, system_response):
        # ذخیره پیام کاربر و پاسخ سیستم در فایل تاریخچه
        with open(self.history_file, "a", encoding="utf-8") as file:
            file.write(f"You: {user_message}\n")
            file.write(f"System: {system_response}\n\n")

    def is_valid_language(self, language_code):
        valid_languages = ["en", "fa", "tr"]
        return language_code in valid_languages


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
