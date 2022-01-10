# Frontend Libraries
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
# Backend Libraries
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
from pytube import Playlist
import random
import os
import smtplib
from googleapiclient.discovery import build


class WindowManager(ScreenManager):
    pass


class Virtual_Voice_AssistantApp(App):
    def build(self):
        return kv

    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def wishMe(self):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            self.speak("Good Morning Sir")
            self.speak("How may i help you?")

        elif hour >= 12 and hour < 18:
            self.speak("Good Afternoon Sir")
            self.speak("How may i help you?")

        else:
            self.speak("Good Evening Sir")
            self.speak("How may i help you?")

    def takecommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Listening...')
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-in')
            print(f'User Said: {query}')
            return query
        except:
            print('Sorry cannot recognize please say that again')
            self.speak('Sorry please say that again')
            return self.takecommand()

    # Database for sendEmail function
    emailDict = {'abhinav': '17122000abhinav@gmail.com'}

    def sendEmail(self, to, content):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        email = os.environ.get('email_id')
        password = os.environ.get('email_pass')
        server.login(email, password)
        server.sendmail(email, to, content)
        server.close()

    def playOnYT(self, query):
        api_key = os.environ.get('YOUTUBE_API')
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(part='snippet', type='video', q=query)
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        webbrowser.open(f'https://www.youtube.com/watch?v={video_id}')
        youtube.close()

    def actions(self, query):
        query = str(query).lower()
        if 'wikipedia' in query:
            self.speak('Searching on Wikipedia..')
            query = query.replace('search', '')
            query = query.replace('on wikipedia', '')
            try:
                result = wikipedia.summary(query, sentences=3)
                self.speak('According to wikipedia')
                print(result)
                # set speed to 150 wpm
                self.engine.say(result, 150)
                self.engine.runAndWait()
                return result
            except:
                result = "Wikipedia Page Not Found!"
                self.speak(result)
                return result

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
            return "Successful!"

        elif 'youtube' in query:
            query = query.replace('on youtube', '')
            query = query.replace('search', '')
            self.playOnYT(query)
            return "Successful!"

        elif 'open google' in query:
            webbrowser.open("google.com")
            return "Successful!"

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")
            return "Successful!"

        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            # set speed to 150 wpm
            result = (f"\nSir the time is {strTime}")
            print(result)
            self.engine.say(f"Sir the time is {strTime}", 150)
            self.engine.runAndWait()
            return result

        elif 'play music' in query:
            self.speak('do you have a specific song in mind?')
            query = str(self.takecommand()).lower()

            if 'no' in query or 'any' in query or 'random' in query:
                p = Playlist(
                    'https://www.youtube.com/watch?v=gvyUuxdRdR4&list=RDCLAK5uy_n9Fbdw7e6ap-98_A-8JYBmPv64v-Uaq1g&start_radio=1')
                url_list = []
                for url in p.video_urls:
                    url_list.append(url)

                url = random.choice(url_list)
                webbrowser.open(url)
                return "Successful!"
            else:
                query = query.replace('play', '')
                self.playOnYT(query)
                return "Successful!"

        elif 'send email' in query:
            try:
                while True:
                    self.speak("Please specify reciever's name")
                    print("Please specify reciever's name")
                    user = str(self.takecommand()).lower()
                    if user in self.emailDict.keys():
                        to = self.emailDict[user]
                        break
                    else:
                        not_found = "Sorry user not found"
                        self.speak(not_found)
                        print(not_found)
                        return not_found
                while True:
                    self.speak('what should i write?')
                    print('what should i write?')
                    content = self.takecommand()
                    self.speak('Please confirm to send email')
                    confirmation = self.takecommand()
                    if 'yes' or 'ok' in confirmation:
                        self.sendEmail(to, content)
                        break
                    elif 'stop' in confirmation:
                        break
                result = 'Email has been sent succesfully!'
                self.speak(result)
                print(result)
                return
            except Exception as e:
                print(e)
                self.speak('Sorry Sir. Unable to send email!')

        elif query == 'sleep':
            self.speak('GoodBye Sir')
            quit()

    def start(self):
        print("STANDBY..")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language='en-in')
            query = str(query).lower()
            print(query)
            if 'jarvis' in query:
                query = str(self.takecommand()).lower()
                self.actions(query)
        except:
            pass


class MainWindow(Screen):
    pass


class ListeningWindow(Screen):
    def exit(self):
        quit()


class OutputWindow(Screen):
    def runCmnd(self):
        input_text = self.ids.my_textinput
        label = self.ids.output_label
        instance = Virtual_Voice_AssistantApp()
        instance.speak("Executing!")
        query = input_text.text
        result = instance.actions(query)
        if result:
            label.text = result


kv = Builder.load_file("my.kv")

if __name__ == "__main__":
    Virtual_Voice_AssistantApp().run()
