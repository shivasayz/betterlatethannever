import sys
import os
import calendar
import warnings
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QPushButton, QSpacerItem
)
from PyQt5.QtCore import QDate, QDateTime, Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QPainterPath


class MonthBar(QFrame):
    def __init__(self, name, fill_ratio, is_filled, theme):
        super().__init__()
        self.name = name
        self.fill_ratio = fill_ratio
        self.is_filled = is_filled
        self.theme = theme
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(20)
        self.setMinimumHeight(100)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        fill_height = int(height * self.fill_ratio)
        radius = 10

        border_color = QColor("#ffffff" if self.theme == "dark" else "#000000")
        fill_color = QColor("#ff4b4b" if self.theme == "dark" else "#d32f2f")
        text_color = border_color

        # Draw outer border
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(Qt.transparent)
        painter.drawRoundedRect(0, 0, width, height, radius, radius)

        # Draw filled section
        if self.is_filled and fill_height > 0:
            path = QPainterPath()
            top = height - fill_height
            path.moveTo(0, height)
            path.lineTo(0, top + radius)
            path.quadTo(0, top, radius, top)
            path.lineTo(width - radius, top)
            path.quadTo(width, top, width, top + radius)
            path.lineTo(width, height)
            path.closeSubpath()

            painter.setBrush(fill_color)
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

        # Draw label
        painter.setPen(text_color)
        font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.name)


class TimeTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.setWindowTitle("Better Late Than Never")
        self.setGeometry(100, 100, 850, 580)  # Slightly taller to fit clock
        self.setStyleSheet(self.get_stylesheet())
        self.initUI()

    def get_stylesheet(self):
        if self.theme == "dark":
            return """
                QWidget {
                    background-color: #1E1E1E;
                    color: white;
                    border-radius: 15px;
                }
                QPushButton {
                    background-color: #333;
                    color: white;
                    padding: 6px 12px;
                    border: 1px solid #666;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #f0f0f0;
                    color: black;
                    border-radius: 15px;
                }
                QPushButton {
                    background-color: #ddd;
                    color: black;
                    padding: 6px 12px;
                    border: 1px solid #aaa;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #ccc;
                }
            """

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.setStyleSheet(self.get_stylesheet())
        for bar in self.bars:
            bar.set_theme(self.theme)

        self.quote.setStyleSheet(
            "color: rgba(255,255,255,180);" if self.theme == "dark"
            else "color: rgba(0,0,0,180);"
        )

        self.datetime_label.setStyleSheet(
            "color: white;" if self.theme == "dark" else "color: black;"
        )

    def get_month_fill_ratios(self):
        today = QDate.currentDate()
        current_month = today.month()
        total_days = calendar.monthrange(today.year(), current_month)[1]
        completed_days = today.day()

        ratios = []
        flags = []
        for i in range(12):
            if i + 1 < current_month:
                ratios.append(1.0)
                flags.append(True)
            elif i + 1 == current_month:
                ratios.append(completed_days / total_days)
                flags.append(True)
            else:
                ratios.append(0.0)
                flags.append(False)
        return ratios, flags

    def initUI(self):
        self.bars = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Header with title and theme toggle
        header_layout = QHBoxLayout()
        title = QLabel("Better Late Than Never", self)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        toggle_btn = QPushButton("🌗 Toggle Theme")
        toggle_btn.clicked.connect(self.toggle_theme)

        header_layout.addWidget(title)
        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding))
        header_layout.addWidget(toggle_btn)
        layout.addLayout(header_layout)

        # Quote
        self.quote = QLabel(self.get_quote(), self)
        self.quote.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.quote.setStyleSheet("color: rgba(255, 255, 255, 220); padding: 10px;")
        self.quote.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.quote)

        # Month bars
        ratios, flags = self.get_month_fill_ratios()
        month_layout = QHBoxLayout()
        month_layout.setSpacing(12)
        month_names = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]
        for i, name in enumerate(month_names):
            bar = MonthBar(name, ratios[i], flags[i], self.theme)
            self.bars.append(bar)
            month_layout.addWidget(bar, stretch=1)
        layout.addLayout(month_layout)

        # Live Date & Time Label ⏰
        self.datetime_label = QLabel("", self)
        self.datetime_label.setFont(QFont("Segoe UI", 11))
        self.datetime_label.setAlignment(Qt.AlignCenter)
        self.datetime_label.setStyleSheet("color: white;")
        layout.addWidget(self.datetime_label)

        # Timer to update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString("dddd, MMMM d, yyyy - hh:mm:ss AP"))

    def get_quote(self):
        from random import choice
        return choice([
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "Fall seven times, stand up eight. – Japanese Proverb",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
    "The man who moves a mountain begins by carrying away small stones. – Confucius",
    "Difficulties strengthen the mind, as labor does the body. – Seneca",
    "Through perseverance many people win success out of what seemed destined to be certain failure. – Benjamin Disraeli",
    "Energy and persistence conquer all things. – Benjamin Franklin",
    "Never confuse a single defeat with a final defeat. – F. Scott Fitzgerald",
    "You may have to fight a battle more than once to win it. – Margaret Thatcher",
    "Persistence guarantees that results are inevitable. – Paramahansa Yogananda",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "You are never too old to set another goal or to dream a new dream. – C.S. Lewis",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. – Ralph Waldo Emerson",
    "Doubt kills more dreams than failure ever will. – Suzy Kassem",
    "Act as if what you do makes a difference. It does. – William James",
    "Whether you think you can or you think you can’t, you’re right. – Henry Ford",
    "Your time is limited, so don’t waste it living someone else’s life. – Steve Jobs",
    "Don't be pushed around by the fears in your mind. Be led by the dreams in your heart. – Roy T. Bennett",
    "You are enough just as you are. – Meghan Markle",
    "Self-confidence is the first requisite to great undertakings. – Samuel Johnson",
    "Success usually comes to those who are too busy to be looking for it. – Henry David Thoreau",
    "The way to get started is to quit talking and begin doing. – Walt Disney",
    "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
    "Success is walking from failure to failure with no loss of enthusiasm. – Winston Churchill",
    "I never dreamed about success. I worked for it. – Estée Lauder",
    "Dream big and dare to fail. – Norman Vaughan",
    "The only place where success comes before work is in the dictionary. – Vidal Sassoon",
    "If you want to achieve greatness, stop asking for permission. – Unknown",
    "Success doesn’t come to you. You go to it. – Marva Collins",
    "Opportunities don't happen. You create them. – Chris Grosser",
    "Be not afraid of growing slowly; be afraid only of standing still. – Chinese Proverb",
    "The best way to predict the future is to create it. – Peter Drucker",
    "Change your thoughts and you change your world. – Norman Vincent Peale",
    "Do one thing every day that scares you. – Eleanor Roosevelt",
    "If you want something you’ve never had, you must be willing to do something you’ve never done. – Thomas Jefferson",
    "We cannot become what we want by remaining what we are. – Max DePree",
    "Life begins at the end of your comfort zone. – Neale Donald Walsch",
    "Small daily improvements over time lead to stunning results. – Robin Sharma",
    "Don’t limit your challenges. Challenge your limits. – Jerry Dunn",
    "Growth is painful. Change is painful. But nothing is as painful as staying stuck. – Mandy Hale",
    "The secret of getting ahead is getting started. – Mark Twain",
    "You don’t have to be great to start, but you have to start to be great. – Zig Ziglar",
    "Well done is better than well said. – Benjamin Franklin",
    "Don’t wait for opportunity. Create it. – Unknown",
    "A goal without a plan is just a wish. – Antoine de Saint-Exupéry",
    "Discipline is the bridge between goals and accomplishment. – Jim Rohn",
    "The future depends on what you do today. – Mahatma Gandhi",
    "Success is the sum of small efforts repeated day in and day out. – Robert Collier",
    "Do not wait; the time will never be ‘just right.’ – Napoleon Hill",
    "Action is the foundational key to all success. – Pablo Picasso",
    "Happiness is not something ready-made. It comes from your own actions. – Dalai Lama",
    "Your attitude, not your aptitude, will determine your altitude. – Zig Ziglar",
    "If you change the way you look at things, the things you look at change. – Wayne Dyer",
    "Success is 10% what happens to you and 90% how you react to it. – Charles R. Swindoll",
    "Nothing will work unless you do. – Maya Angelou",
    "You can't cross the sea merely by standing and staring at the water. – Rabindranath Tagore",
    "Live as if you were to die tomorrow. Learn as if you were to live forever. – Mahatma Gandhi",
    "Do not let what you cannot do interfere with what you can do. – John Wooden",
    "Life is 10% what happens to us and 90% how we respond to it. – Dennis P. Kimbro",
    "Be so good they can’t ignore you. – Steve Martin",
    "Keep going. – Unknown",
    "Make it happen. – Unknown",
    "Stay hungry. Stay foolish. – Steve Jobs",
    "Create. Don’t wait. – Unknown",
    "One day or day one. You decide. – Unknown",
    "Prove them wrong. – Unknown",
    "Dream. Plan. Do. – Unknown",
    "Start now. – Unknown",
    "Push yourself. No one else will. – Unknown",
    "No pressure, no diamonds. – Thomas Carlyle",
    "Everything you’ve ever wanted is on the other side of fear. – George Addair",
    "Courage doesn’t always roar. – Mary Anne Radmacher",
    "Fear is a reaction. Courage is a decision. – Winston Churchill",
    "Do not be afraid to give up the good to go for the great. – John D. Rockefeller",
    "It’s not the load that breaks you down, it’s the way you carry it. – Lou Holtz",
    "Take risks: if you win, you will be happy; if you lose, you will be wise. – Unknown",
    "You miss 100% of the shots you don’t take. – Wayne Gretzky",
    "Leap and the net will appear. – John Burroughs",
    "Don’t fear failure. Fear being in the exact same place next year. – Unknown",
    "Only those who dare to fail greatly can ever achieve greatly. – Robert F. Kennedy",
    "Every morning we are born again. What we do today is what matters most. – Buddha",
    "Light tomorrow with today. – Elizabeth Barrett Browning",
    "You only live once, but if you do it right, once is enough. – Mae West",
    "The best revenge is massive success. – Frank Sinatra",
    "Every strike brings me closer to the next home run. – Babe Ruth",
    "Don’t count the days, make the days count. – Muhammad Ali",
    "Live each day as if your life had just begun. – Johann Wolfgang von Goethe",
    "If opportunity doesn’t knock, build a door. – Milton Berle",
    "I can and I will. Watch me. – Carrie Green",
    "Turn your wounds into wisdom. – Oprah Winfrey",
    "The harder you work for something, the greater you’ll feel when you achieve it. – Unknown",
    "Push yourself, because no one else is going to do it for you. – Unknown",
    "Success doesn’t just find you. You have to go out and get it. – Unknown",
    "Great things never come from comfort zones. – Unknown",
    "Wake up with determination. Go to bed with satisfaction. – Unknown",
    "Do something today that your future self will thank you for. – Sean Patrick Flanery",
    "Little things make big days. – Isabel Marant",
    "It always seems impossible until it’s done. – Nelson Mandela",
    "Your only limit is your mind. – Unknown",
    "The best time to start was yesterday. The next best is now.",
    "Each month is a blank page. Make it a masterpiece.",
    "Don't count the months—make the months count.",
    "Completed months are experience. The rest are opportunity.",
    "Consistency builds greatness, one month at a time."
])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTracker()
    window.show()
    sys.exit(app.exec_())
