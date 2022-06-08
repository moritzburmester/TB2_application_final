from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivymd.uix.picker import MDDatePicker, MDThemePicker
from akivymd.uix.datepicker import AKDatePicker

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year

current_day = datetime.now().strftime('%d')
current_day_full_text = datetime.now().strftime('%A')
current_month_text_short = datetime.now().strftime('%h')
current_month_text_long = datetime.now().strftime('%B')


class QuestionnaireScreen1(Screen):
    pass


class QuestionnaireScreen2(Screen):
    pass


class QuestionnaireScreen3(Screen):
    pass


class QuestionnaireScreen4(Screen):
    pass


class MenuScreen(Screen):

    def show_akdate_picker(self):
        akdate_picker = AKDatePicker(year_range=[2000, currentYear + 1])
        akdate_picker.open()
        print(currentYear, current_month_text_short, current_month_text_long, currentDay)

    def show_theme_picker(self):
        theme_picker = MDThemePicker()
        theme_picker.open()

    def show_date_picker(self):
        date_picker = MDDatePicker(
            year=currentYear,
            month=currentMonth,
            day=currentDay)

        date_picker.open()
