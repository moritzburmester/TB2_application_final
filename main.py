import json
import calendar
from datetime import datetime
from time import strptime
from kivymd.uix.list import TwoLineListItem
import numpy as np
import requests
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, SlideTransition
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
import matplotlib.pyplot as plt
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from backend_kivy.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.text import LabelBase

# modules
from menu.menu import MenuScreen
from authentication.myfirebase import MyFirebase, LogInScreen, SignUpScreen


class DiaryScreen(Screen):
    pass


class AvatarScreen(Screen):
    pass


# main application class

class MainApp(MDApp):

    def __init__(self, **kwargs):

        self.dialog = None
        self.current_month_text_short = None
        self.box = None
        self.email = None
        self.username = None
        self.local_id = None
        self.id_token = None
        self.title = "TB2"

        # Setting theme properties

        self.theme_cls = ThemeManager()

        self.my_firebase = MyFirebase()

        super().__init__(**kwargs)

    def build(self):

        # change app icon
        self.icon = 'assets/mental-icon-2.jpg'

        # Set window size to average phone screen height and width
        Window.size = (320, 600)

        # initialize screen manager
        self.sm = ScreenManager()

        # adding screens
        self.sm.add_widget(LogInScreen(name='login'))
        self.sm.add_widget(SignUpScreen(name='signup'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(DiaryScreen(name='diary'))
        self.sm.add_widget(AvatarScreen(name='avatar'))

        return self.sm

    def on_start(self):

        # get weather report and update labels in menu screen
        self.show_weather()

        # set color of cards in menu/timeline screen
        for i in range(1, 12):
            card = "carousel" + str(i)
            self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_light

        # set color of emoji cards in menu screen
        for i in range(1, 7):
            card = "emoji" + str(i)
            self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_light

        # set color of cards in avatar screen
        for i in range(1, 10):
            card = "card" + str(i)
            self.root.get_screen("avatar").ids[card].md_bg_color = self.theme_cls.primary_light

        # set time to current time
        currentYear = datetime.now().year
        current_day = datetime.now().strftime('%d')
        current_day_full_text = datetime.now().strftime('%A')
        self.current_month_text_short = datetime.now().strftime('%h')
        current_month_text_long = datetime.now().strftime('%B')

        self.root.get_screen('menu').ids.today1.text = " " + current_day
        self.root.get_screen(
            'menu').ids.today2.text = f"{current_day_full_text}\n{self.current_month_text_short} {currentYear}"
        self.root.get_screen('menu').ids.moodchart_month.text = current_month_text_long + "  " + str(currentYear)

        try:
            # try to read persistent sign in credentials

            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()

            # use refresh_token to get a new idToken

            self.id_token, self.local_id = self.my_firebase.exchange_refresh_token(refresh_token.replace("\n", ""))

            # get database data

            result = requests.get("https://techbasics2assignment-default-rtdb.europe-west1.firebasedatabase.app/" +
                                  self.local_id + ".json?auth=" + self.local_id)

            data = json.loads(result.content.decode())

            # display username in menu screen

            with open("credentials/username.txt", 'r') as f:
                username = f.read()
                self.root.get_screen('menu').ids.welcome_label.text = f"Hey {username}, how do you feel today?"
                self.username = username
                self.root.get_screen("menu").ids.username.text = "          " + username

            # get email from user

            with open("credentials/email.txt", 'r') as f:
                email = f.read()
                self.email = email

            self.sm.transition = NoTransition()
            self.change_screen('menu')
            self.sm.transition = SlideTransition()

        except Exception as e:
            print(e)

        try:
            # try to plot mood chart if there is data in database
            self.add_plot()
        except Exception as e:
            print(e)

        try:
            # try to add list items to timeline MDList if diary entries exist
            length, titles, days, content = self.my_firebase.get_diary(self.current_month_text_short)
            month_number = strptime(f'{self.current_month_text_short}', '%b').tm_mon

            listitems = {}
            for i in range(length):
                listitems[i] = TwoLineListItem(text=f'{days[i]}.{month_number}.{currentYear}', secondary_text=titles[i],
                                               secondary_theme_text_color='Primary',
                                               theme_text_color='Secondary',
                                               on_release=lambda x, i=i: self.my_firebase.update_diary(i, days, titles,
                                                                                                       content,
                                                                                                       month_number)
                                               )

                self.root.get_screen('menu').ids.diary_list.add_widget(listitems[i])

        except Exception as e:
            print(e)

    def change_card_color_carousel(self, card_number):

        """Function that changes card color of carousel card when card is clicked."""
        for i in range(1, 12):
            card = "carousel" + str(i)
            self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_light
        card = "carousel" + str(card_number)
        self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_dark

    def spinner_toggle(self):

        """Function that toggles spinner to active/inactive"""

        if not self.root.get_screen('signup').ids.spinner.active:
            self.root.get_screen('signup').ids.spinner.active = True
        else:
            self.root.get_screen('signup').ids.spinner.active = False

    def change_screen(self, screen):

        """Function that changes to specified screen """

        self.sm.current = screen

    def update_plot(self):

        """Function that clears plot widget, clears plot data and then creates a new plot with updated data."""

        box = self.root.get_screen('menu').ids.box
        box.clear_widgets()
        plt.cla()
        self.add_plot()

    def add_plot(self):

        """Function that creates a plot that shows the mood progression of the user."""



        # dataset
        df = self.my_firebase.update_plot()

        # convert x values to int
        df['x'] = df['x'].astype(int)
        # sort dataset
        df = df.sort_values(['x'])
        # convert to list
        y = df.y.to_list()
        x = df.x.to_list()

        ax = plt.gca()

        # disable y-axis labels
        ax.axes.yaxis.set_ticklabels([])

        # add color to background
        ax.axhspan(1, 2, facecolor='red', alpha=0.5)
        ax.axhspan(2, 3, facecolor='red', alpha=0.3)
        ax.axhspan(3, 4, facecolor='yellow', alpha=0.3)
        ax.axhspan(4, 5, facecolor='green', alpha=0.3)
        ax.axhspan(5, 6, facecolor='green', alpha=0.5)

        # Plot Graph
        plt.plot(x, y, color='black', linestyle='solid')

        # set x axis values
        now = datetime.now()
        days = calendar.monthrange(now.year, now.month)[1]
        plt.xlim(1, days)

        # add grid
        plt.grid()

        # set ticks for y axis
        plt.yticks(np.arange(1, 7))
        # set ticks for x axis
        x_ticks = np.arange(1, days+1, 4).tolist()
        x_ticks.remove(29)
        x_ticks.append(days)
        plt.xticks(x_ticks)

        # add plot to BoxLayout in menu.kv
        self.box = self.root.get_screen('menu').ids.box
        self.box.padding = (10, 0, 0, 0)
        self.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def change_card_color(self, card_number):

        """Function that changes card color of horizontal sliding cards in menu screen"""

        for i in range(1, 7):
            card = "emoji" + str(i)
            self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_light
        card = "emoji" + str(card_number)
        self.root.get_screen("menu").ids[card].md_bg_color = self.theme_cls.primary_dark

    def change_avatar_card_color(self, card_number):

        """Function that changes card color of cards in avatar screen"""

        for i in range(1, 10):
            card = "card" + str(i)
            self.root.get_screen("avatar").ids[card].md_bg_color = self.theme_cls.primary_light
        card = "card" + str(card_number)
        self.root.get_screen("avatar").ids[card].md_bg_color = self.theme_cls.primary_dark

    def change_avatar(self):

        """Function that changes the avatar when user clicks submit in avatar screen"""

        for i in range(1, 10):
            card = "card" + str(i)
            image = "image" + str(i)
            if self.root.get_screen("avatar").ids[card].md_bg_color == self.theme_cls.primary_dark:
                self.root.get_screen('menu').ids['avatar1'].source = self.root.get_screen("avatar").ids[image].source
                self.root.get_screen('menu').ids['avatar2'].source = self.root.get_screen("avatar").ids[image].source
                self.my_firebase.update_avatar(self.root.get_screen("avatar").ids[image].source)
        self.change_screen('menu')

    def clear_input(self):
        """Function that clears title and content field of diary when user presses reset button"""
        self.root.get_screen('menu').ids.title.text = ""
        self.root.get_screen('menu').ids.content.text = ""

    def format_date_month(self, date):
        month_number = date.split('.')[1]
        datetime_object = datetime.strptime(month_number, "%m")
        month_name = datetime_object.strftime("%b")
        print(month_name)
        return month_name

    def format_date_day(self, date):
        day = date.split('.')[0]
        print(day)
        return day

    def confirm_delete_dialog(self):

        if not self.dialog:
            self.dialog = MDDialog(
                title="Delete Entry?",
                text="This will delete the diary entry.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.confirm_delete
                    ),
                ],
            )
        self.dialog.open()

    def confirm_delete(self, obj):
        date = self.root.get_screen('diary').ids.date.text
        self.my_firebase.delete_diary(self.format_date_day(date), self.format_date_month(date))
        self.my_firebase.refresh_diary(self.format_date_month(date))
        self.dialog.dismiss()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def show_weather(self):

        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        apikey = "facc8b8a55bf0bffec4fdce03dc17d12"
        city = "Hamburg"
        url = base_url + "q=" + city + "&appid=" + apikey
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            main = data['main']

            # getting temperature
            temperature = main['temp'] - 273.15
            # weather report
            report = data['weather']

            self.root.get_screen('menu').ids.temperature.text = str(round(temperature, 0)) + "°C"
            self.root.get_screen('menu').ids.weather.source = 'https://openweathermap.org/img/w/' + data['weather'][0][
                'icon'] + '.png'


# driver code

if __name__ == "__main__":
    LabelBase.register(name='Roboto',
                       fn_regular='assets/Poppins/Poppins-Light.ttf',
                       fn_bold='assets/Roboto/Roboto-Medium.ttf')
    MainApp().run()
