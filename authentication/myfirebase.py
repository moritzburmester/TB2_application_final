# kivy imports
from datetime import datetime

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

# other modules
import requests
import json


# classes
class LogInScreen(Screen):
    pass


class SignUpScreen(Screen):
    pass


class Content1(BoxLayout):
    pass


class Content2(BoxLayout):
    pass


class MyFirebase:

    # dialog fields
    dialog1 = None
    dialog2 = None

    # api key
    key = "AIzaSyCc3kh6tOV80CMtwpaSEO80d0JUK_9FqdM"

    # snackbar messages
    failure = "Invalid Data. Please try again."
    signup_success = "Sign Up Successful!"
    signin_success = "Log In Successful!"

    def sign_up(self, email, username, password1, password2):

        """
        Function that takes user input from signup screen and authenticates the user through firebase authentication.

        :param email: The e-mail that the user types in the corresponding textfield.
        :param username: The username that the user types in the corresponding textfield.
        :param password1: The password that the user types in the corresponding textfield.
        :param password2: The password confirmation that the user types in the corresponding textfield.
        """

        app = App.get_running_app()

        # send email, username, password to firebase
        signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + self.key
        signup_payload = {"displayName": username, "email": email, "password": password1, "returnSecureToken": True}

        if password1 == password2:

            signup_req = requests.post(signup_url, data=signup_payload)
            signup_data = json.loads(signup_req.content.decode())

            if signup_req:

                localId = signup_data['localId']
                idToken = signup_data['idToken']

                # save username,email to a variable in MainAppClass
                app.email = email
                app.username = username
                # save localId to a variable in MainAppClass
                app.local_id = localId
                # Save IdToken to variable in MainAppClass
                app.id_token = idToken
                # create new key in database from localId
                my_data = {"username": username, "avatar": "assets/animal_icons/cat.png"}
                post_request = requests.patch(
                    "https://techbasics2assignment-default-rtdb.europe-west1.firebasedatabase.app/" + localId +
                    ".json?auth=" + idToken, data=json.dumps(my_data))

                # change screen to login if successful
                app.change_screen('login')
                self.snackbar_show(self.signup_success)

                # write username to local file
                with open("credentials/username.txt", "w") as f:
                    f.write(username)

                # write email to local file
                with open("credentials/email.txt", "w") as f:
                    f.write(email)

                # Clear userinput
                app.root.get_screen('signup').ids.username.text = ""
                app.root.get_screen('signup').ids.email.text = ""
                app.root.get_screen('signup').ids.password1.text = ""
                app.root.get_screen('signup').ids.password2.text = ""

            else:

                # invalid email or password not safe enough
                self.snackbar_show(self.failure)

        else:

            # passwords don't match
            self.snackbar_show(self.failure)


    def sign_in(self, email, password):

        """
        Function that takes user input from login screen and validates user information from database.

        :param email: Email input from the corresponding textfield.
        :param password: Password input from the corresponding textfield.
        """

        app = App.get_running_app()

        signin_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + self.key
        signin_payload = {"email": email, "password": password, "returnSecureToken": True}
        signin_req = requests.post(signin_url, data=signin_payload)
        signin_data = json.loads(signin_req.content.decode())

        if signin_req.ok:
            # save refreshToken to a file
            refresh_token = signin_data['refreshToken']
            localId = signin_data['localId']
            idToken = signin_data['idToken']

            with open("credentials/refresh_token.txt", "w") as f:
                f.write(refresh_token)

            app.change_screen('menu')
            self.snackbar_show(self.signin_success)

            # save email to mainappclass variable
            with open("credentials/email.txt", "w") as f:
                f.write(email)
            with open("credentials/email.txt", "r") as f:
                app.email = f.read()

            # change label and avatar in menu screen to username and user avatar
            get_request = requests.get(
                "https://techbasics2assignment-default-rtdb.europe-west1.firebasedatabase.app/" + localId +
                ".json?auth=" + idToken)

            if get_request.ok:
                username = get_request.json()["username"]
                avatar = get_request.json()["avatar"]

            with open("credentials/username.txt", "w") as f:
                f.write(username)

            with open("credentials/avatar.txt", "w") as f:
                f.write(avatar)

            with open("credentials/username.txt", "r") as f:
                username = f.read()

            with open("credentials/avatar.txt", "r") as f:
                avatar = f.read()

            # updating the app
            current_month_text_short = datetime.now().strftime('%h')
            app.my_firestore.refresh_diary(current_month_text_short)
            app.update_plot()
            app.root.get_screen("menu").ids.avatar1.source = avatar
            app.root.get_screen("menu").ids.avatar2.source = avatar
            app.root.get_screen("menu").ids.welcome_label.text = "Welcome, " + username + "!\nHow do you feel today?"
            app.root.get_screen("menu").ids.username.text = "          " + username

            # clear userinput
            app.root.get_screen('login').ids.email.text = ""
            app.root.get_screen('login').ids.password.text = ""

        else:

            # invalid password/email
            self.snackbar_show(self.failure)


    def exchange_refresh_token(self, refresh_token):

        """
        A Function that allows user to instantly access menu screen if they have already logged in from their device.

        :param refresh_token: The refresh token generated by the firebase authentication, that is saved locally.
        :return A new idToken and a localId for the user.
        """

        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.key
        refresh_payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        refresh_req = requests.post(refresh_url, data=refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']

        return id_token, local_id

    def log_out(self):

        """
        Function that clears the refresh_token and changes screen to 'login'. User is logged out.
        """

        app = App.get_running_app()

        with open("credentials/refresh_token.txt", "w") as f:
            f.write("")
        with open("credentials/email.txt", "w") as f:
            f.write("")
        with open("credentials/avatar.txt", "w") as f:
            f.write("")
        with open("credentials/username.txt", "w") as f:
            f.write("")

        mdlist = app.root.get_screen('menu').ids.diary_list
        mdlist.clear_widgets()

        app.change_screen('login')

    def update_avatar(self, avatar):

        """
        Function that updates user avatar in firebase database.

        :param avatar: The specified avatar that the user chooses as file path.
        """

        app = App.get_running_app()
        my_data = {"avatar": avatar}
        localId = app.local_id
        idToken = app.id_token

        with open("credentials/avatar.txt", "w") as f:
            f.write(avatar)

        patch_request = requests.patch(
            "https://techbasics2assignment-default-rtdb.europe-west1.firebasedatabase.app/" + localId +
            ".json?auth=" + idToken, data=json.dumps(my_data))

    def reset_password_dialog(self):

        """
        Function that creates a Pop-up dialog when user clicks on forgot_password button
        """

        app = App.get_running_app()

        if not self.dialog1:
            self.dialog1 = MDDialog(
                title="Type in Email Address:",
                type="custom",
                content_cls=Content1(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.close_dialog1
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.reset_password
                    ),
                ],
            )
        self.dialog1.open()

    def reset_password(self, obj):

        """
        A function that sends an email to the user with a code when they want to reset their password.

        :param obj: Not used.
        """

        email = self.dialog1.content_cls.ids.resemail.text
        self.dialog1.content_cls.ids.resemail.text = ""

        password_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=" + self.key
        password_payload = {"requestType": "PASSWORD_RESET", "email": email}
        password_req = requests.post(password_url, data=password_payload)
        password_data = json.loads(password_req.content.decode())

        if password_req.ok:

            self.confirm_password_reset_dialog()

        else:

            self.snackbar_show("Invalid email.")

    def confirm_password_reset_dialog(self):

        """
        A function that displays the confirm password reset dialog.
        """

        app = App.get_running_app()

        if not self.dialog2:
            self.dialog2 = MDDialog(
                title="Type in action code:",
                type="custom",
                content_cls=Content2(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.close_dialog2
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.confirm_password_reset
                    ),
                ],
            )
        self.dialog2.open()

    def confirm_password_reset(self, obj):

        """
        A function that validates the code that the user received per email. If correct, it resets their password.

        :param obj: Not used.
        """

        newpassword = self.dialog2.content_cls.ids.newpassword.text
        code = self.dialog2.content_cls.ids.actioncode.text
        self.dialog2.content_cls.ids.actioncode.text = ""
        self.dialog2.content_cls.ids.newpassword.text = ""

        password_url = "https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key=" + self.key
        password_payload = {"oobCode": code, "newPassword": newpassword}
        password_req = requests.post(password_url, data=password_payload)
        password_data = json.loads(password_req.content.decode())

        if password_req.ok:
            self.snackbar_show("Password reset successful!")
            self.dialog2.dismiss()
            self.dialog1.dismiss()
        else:
            self.snackbar_show("Invalid code.")

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

    def close_dialog1(self, obj):

        """
        A function that closes the password reset dialog.

        :param obj: Not used.
        """
        self.dialog1.dismiss()

    def close_dialog2(self, obj):

        """
        A function that closes the confirm password reset dialog.

        :param obj: Not used.
        """
        self.dialog2.dismiss()
