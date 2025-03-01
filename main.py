import re
import json
import html
import os
import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView


def parse_chat_file():
    input_file = "chat.html"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_txt = os.path.join(output_dir, "chat_export.txt")
    output_json = os.path.join(output_dir, "chat_export.json")
    error_file = os.path.join(output_dir, "errors.log")

    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()

    json_matches = re.finditer(r"\{.*?\}", text, re.DOTALL)

    found_messages = []
    error_logs = []

    for match in json_matches:
        try:
            json_text = match.group(0)
            data = json.loads(json_text)
            if "parts" in data and isinstance(data["parts"], list):
                messages = [html.unescape(part) for part in data["parts"] if isinstance(part, str)]
                found_messages.extend(messages)

        except json.JSONDecodeError as e:
            error_logs.append(f"Ошибка парсинга JSON: {e}")

    if found_messages:
        processed_lines = []
        for msg in found_messages:
            line = re.sub(r"[^\w\s.,!?()\"':;%–—\-\n]", "", msg)
            line = line.strip()
            if line:
                line = line[0].upper() + line[1:]
            processed_lines.append(line)

        clean_text = "\n".join(processed_lines)

        char_count = len(clean_text)
        word_count = len(re.findall(r"\b\w+\b", clean_text))
        print(f"Символов: {char_count}")
        print(f"Слов: {word_count}")

        with open(output_txt, "w", encoding="utf-8") as txt_file:
            txt_file.write(clean_text)

        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump({"messages": processed_lines}, json_file, ensure_ascii=False, indent=4)

        print(f"\n✅ Данные сохранены в '{output_txt}' и '{output_json}'")
    else:
        print("❌ Сообщения не найдены в 'parts'. Возможно, формат другой.")

    if error_logs:
        with open(error_file, "w", encoding="utf-8") as err_file:
            err_file.write("\n".join(error_logs))
        print(f"⚠️ Некоторые JSON-объекты не удалось разобрать. Ошибки записаны в '{error_file}'")


class ChatViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Data Export Viewer")
        self.setGeometry(200, 200, 900, 600)

        self.browser = QWebEngineView()
        html_path = os.path.abspath("chat.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        self.close_button = QPushButton("Закрыть окно")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


def main():
    parse_chat_file()
    app = QApplication(sys.argv)
    viewer = ChatViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
