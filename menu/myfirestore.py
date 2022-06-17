# kivy imports
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.snackbar import Snackbar

# firestore
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

# other modules
from datetime import datetime
from time import strptime
import pandas as pd


# classes
class MenuScreen(Screen):

    def show_theme_picker(self):
        """
        This function displays the theme picker widget in the navigation drawer in the home screen of the app.
        """
        theme_picker = MDThemePicker()
        theme_picker.open()


class MyFirestore:

    # initialize firestore
    cred = credentials.Certificate("credentials/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # snackbar messages
    empty_diary = "Title or Content can't be empty"
    no_entry = "No entries for this month!"

    def update_mood(self, value):

        """
        Function that takes the mood value that's specified by the user in the home screen.
        The Function then updates the value at the corresponding date in the firestore database.

        :param value: A value between 1-6, depending on the choice of the user
        """

        app = App.get_running_app()

        # update mood value
        value = 7 - value
        email = app.email
        current_day = datetime.now().strftime('%d')
        current_month_text_short = datetime.now().strftime('%h')
        data = {current_month_text_short: {current_day: value}}

        self.db.collection('mood').document(email).set(data, merge=True)

    def update_plot(self):

        """
        A function that updates the plot in the mood-chart progression screen when called.

        :return: A dataframe that contains all the mood values for the current month with x as the days and y for the
                 mood values.
        """

        app = App.get_running_app()
        email = app.email
        current_month_text_short = datetime.now().strftime('%h')

        # get values
        result = self.db.collection('mood').document(email).get()
        if result.exists:
            mood_dict = result.to_dict()[current_month_text_short]

            # format dictionary
            x = list(mood_dict.keys())
            y = list(mood_dict.values())
            d = {'x': x, 'y': y}
            df = pd.DataFrame(d)

            return df

    def send_diary(self, title, content):

        """
        A function that sends the diary title and content to the firestore database.

        :param title: The title specified by the user in the diary screen.
        :param content: The content written by the user in the diary screen.
        """
        if title.text == "" or content.text == "":
            self.snackbar_show(self.empty_diary)
        else:
            app = App.get_running_app()
            email = app.email
            current_day = datetime.now().strftime('%d')
            current_month_text_short = datetime.now().strftime('%h')
            data = {current_month_text_short: {current_day: [{'Title': title.text}, {'Content': content.text}]}}

            self.db.collection('diary').document(email).set(data, merge=True)

    def get_diary(self, month):

        """
        A Function that fetches the diary data from the firestore database.

        :param month: The specified month by the user in the archive screen from when the data should be collected.
        :return: The amount of diary entries (length), the titles, content and corresponding days of the entries.
        """
        app = App.get_running_app()
        email = app.email
        result = self.db.collection('diary').document(email).get()

        if result.exists:

            if month in result.to_dict():

                diary_dict = result.to_dict()[month]
                length = len(list(diary_dict.keys()))
                days = [x for x in diary_dict]
                titles = [x['Title'] for x in [x[0] for x in [diary_dict[x] for x in days]]]
                content = [x['Content'] for x in [x[1] for x in [diary_dict[x] for x in days]]]

                return length, titles, days, content

            else:

                return False

    def refresh_diary(self, month):

        """
        A function that refreshes the diary. E.g., when a new entry has been made, the month specified by the user
        was changed or the entry was deleted.

        :param month: The specified month where the diary entries should be refreshed.
        """
        app = App.get_running_app()

        if not self.get_diary(month):

            self.snackbar_show(self.no_entry)
            app.root.get_screen('menu').ids.diary_list.clear_widgets()

        else:

            length, titles, days, content = self.get_diary(month)
            mdlist = app.root.get_screen('menu').ids.diary_list
            mdlist.clear_widgets()
            month_number = strptime(f'{month}', '%b').tm_mon
            currentYear = datetime.now().year

            listitems = {}
            for i in range(length):
                listitems[i] = TwoLineListItem(text=f'{days[i]}.{month_number}.{currentYear}', secondary_text=titles[i],
                                               secondary_theme_text_color='Primary',
                                               theme_text_color='Secondary',
                                               on_release=lambda x, i=i: self.update_diary(i, days, titles, content,
                                                                                           month_number)
                                               )

                app.root.get_screen('menu').ids.diary_list.add_widget(listitems[i])

    def update_diary(self, item, days, titles, content, month):

        """
        This function updates the text-fields in the diary screen.

        :param item: The index of the diary entry from the scroll list.
        :param days: The day of the month of the entry.
        :param titles: Title of the entry.
        :param content: Content of the entry.
        :param month: Month of the entry.
        """

        app = App.get_running_app()
        currentYear = datetime.now().year
        app.change_screen('diary')

        app.root.get_screen('diary').ids.date.text = f'{days[item]}.{month}.{currentYear}'
        app.root.get_screen('diary').ids.title.text = titles[item]
        app.root.get_screen('diary').ids.content.text = content[item]

    def delete_diary(self, day, month):

        """
        This function deletes the diary entry from the database when the user presses delete in the diary screen.

        :param day: The day of the month of the diary entry.
        :param month: The month of the diary entry.
        """

        app = App.get_running_app()
        app.change_screen('menu')
        email = app.email

        self.db.collection('diary').document(email).update({month + '.' + day: firestore.DELETE_FIELD})

    def snackbar_show(self, string):

        """
        Function that displays a Snackbar depending on the type of message that is passed.

        :param string: A specified string, e.g. "Invalid data!"
        """

        snackbar = Snackbar(
            text=string,
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        snackbar.size_hint_x = (
                                       Window.width - (snackbar.snackbar_x * 2)
                               ) / Window.width
        snackbar.open()
