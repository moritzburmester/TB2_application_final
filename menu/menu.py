from datetime import datetime

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.picker import MDDatePicker, MDThemePicker
from akivymd.uix.datepicker import AKDatePicker

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year

current_day = datetime.now().strftime('%d')
current_day_full_text = datetime.now().strftime('%A')
current_month_text_short = datetime.now().strftime('%h')
current_month_text_long = datetime.now().strftime('%B')


class MenuScreen(Screen):

    def show_theme_picker(self):
        theme_picker = MDThemePicker()
        theme_picker.open()


