import csv
import json
from datetime import datetime

import numpy as np
import requests
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, SlideTransition
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
import matplotlib.pyplot as plt
import pandas as pd
from backend_kivy.backend_kivyagg import FigureCanvasKivyAgg


# modules
from menu.menu import MenuScreen, QuestionnaireScreen1, QuestionnaireScreen2, QuestionnaireScreen3, QuestionnaireScreen4
from authentication.myfirebase import MyFirebase, LogInScreen, SignUpScreen


class DiaryScreen(Screen):
    pass


class ArchiveScreen(Screen):
    pass


# main application class

class MainApp(MDApp):

    def __init__(self, **kwargs):
        self.title = "Janaru"

        # Setting theme properties
        self.theme_cls = ThemeManager()

        self.my_firebase = MyFirebase()

        super().__init__(**kwargs)

    def build(self):
        # Set window size to average phone screen height and width
        Window.size = (320, 600)

        # initialize screen manager
        self.sm = ScreenManager()

        # adding screens

        self.sm.add_widget(LogInScreen(name='login'))
        self.sm.add_widget(SignUpScreen(name='signup'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(QuestionnaireScreen1(name='questionnaire1'))
        self.sm.add_widget(QuestionnaireScreen2(name='questionnaire2'))
        self.sm.add_widget(QuestionnaireScreen3(name='questionnaire3'))
        self.sm.add_widget(QuestionnaireScreen4(name='questionnaire4'))


        return self.sm

    def on_start(self):

        # plot csv file

        headers = ['x', 'y']
        df = pd.read_csv("data.csv", usecols=headers)

        self.add_plot(df)

        # set time to current time

        currentYear = datetime.now().year
        current_day = datetime.now().strftime('%d')
        current_day_full_text = datetime.now().strftime('%A')
        current_month_text_short = datetime.now().strftime('%h')
        current_month_text_long = datetime.now().strftime('%B')

        self.root.get_screen('menu').ids.today1.text = current_day
        self.root.get_screen(
            'menu').ids.today2.text = f"{current_day_full_text}\n{current_month_text_short} {currentYear}"
        self.root.get_screen('menu').ids.today3.text = current_day
        self.root.get_screen(
            'menu').ids.today4.text = f"{current_day_full_text}\n{current_month_text_short} {currentYear}"
        self.root.get_screen('menu').ids.today5.text = str(currentYear)
        self.root.get_screen('menu').ids.today6.text = current_month_text_long

        try:
            # try to read persistent sign in credentials

            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()

            # use refresh_token to get a new idToken

            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token.replace("\n", ""))

            # get database data

            result = requests.get("https://techbasics2assignment-default-rtdb.europe-west1.firebasedatabase.app/" +
                                  local_id + ".json?auth=" + id_token)

            data = json.loads(result.content.decode())

            # display username in menu screen

            with open("username.txt", 'r') as f:
                username = f.read()
                self.root.get_screen('menu').ids.welcome_label.text = f"Hey {username}, how do you feel today?"

            self.sm.transition = NoTransition()
            self.change_screen('menu')
            self.sm.transition = SlideTransition()

        except Exception as e:
            print(e)

    def spinner_toggle(self):

        """Function that toggles spinner to active/inactive"""

        if not self.root.get_screen('signup').ids.spinner.active:
            self.root.get_screen('signup').ids.spinner.active = True
        else:
            self.root.get_screen('signup').ids.spinner.active = False

    def change_screen(self, screen):

        """Function that changes to specified screen """

        self.sm.current = screen

    def submit_form(self):

        """ Function that takes the user input from the questionnaire
        and appends it to a csv file."""
        list = []
        for i in range(1, 5):
            for j in range(1, 8):
                icon = "list" + str(i) + "icon" + str(j)
                if self.root.get_screen("questionnaire"+str(i)).ids[icon].icon == "circle":
                    list.append(j)

        # reverse score for question 4
        list[3] = 8 - list[3]
        # calculate average
        mean = sum(list)/len(list)

        y = mean
        x = datetime.now().strftime('%d').lstrip("0").replace(" 0", " ")

        data = [x, y]

        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

        headers = ['x', 'y']
        df = pd.read_csv("data.csv", usecols=headers)

        self.add_plot(df)

        self.change_screen('menu')

    def add_plot(self, df):
        plt.plot(df.x, df.y)
        plt.xticks(np.arange(1, 30, 4))
        box = self.root.get_screen('menu').ids.box
        box.padding = (0,65,0,0)
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def change_icon(self, screen, field):

        for i in range(1, 8):
            icon = "list" + str(screen) + "icon" + str(i)
            print(icon)
            self.root.get_screen("questionnaire"+str(screen)).ids[icon].icon = "circle-outline"

        icon = "list" + str(screen) + "icon" + str(field)
        self.root.get_screen("questionnaire" + str(screen)).ids[icon].icon = "circle"


# driver code

if __name__ == "__main__":
    MainApp().run()
