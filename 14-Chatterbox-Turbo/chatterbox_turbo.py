import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class ChatterboxTurboApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Chatterbox Turbo - Resemble AI + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

        # Main layout
        self.layout_main = Layout(self)
        self.layout_main.SetProps(Parent=self, Align="Client", Margins=Bounds(RectF(10, 10, 10, 10)))

        # API Key Section
        self.layout_api = Layout(self)
        self.layout_api.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 0, 0, 5)))

        self.api_label = Label(self)
        self.api_label.SetProps(Parent=self.layout_api, Align="Left", Text="Replicate API Key:", Width=120, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.api_edit = Edit(self)
        self.api_edit.SetProps(Parent=self.layout_api, Align="Client", Password=True, Text="")
        if os.environ.get("REPLICATE_API_TOKEN"):
            self.api_edit.Text = os.environ.get("REPLICATE_API_TOKEN")

        # Voice Selection
        self.layout_voice = Layout(self)
        self.layout_voice.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.voice_label = Label(self)
        self.voice_label.SetProps(Parent=self.layout_voice, Align="Left", Text="Voice:", Width=50, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_voice = ComboBox(self)
        self.combo_voice.SetProps(Parent=self.layout_voice, Align="Left", Width=150)
        # Using common preset IDs for Resemble
        voices = ["f-us-1", "m-us-1", "f-us-2", "m-us-2", "f-gb-1", "m-gb-1"]
        for v in voices:
            self.combo_voice.Items.Add(v)
        self.combo_voice.ItemIndex = 0

        # Prompt Section
        self.layout_text = Layout(self)
        self.layout_text.SetProps(Parent=self.layout_main, Align="Top", Height=120, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.text_label = Label(self)
        self.text_label.SetProps(Parent=self.layout_text, Align="Top", Text="Text to speak (supports [laugh], [cough], [chuckle]):", Height=25)

        self.text_memo = Memo(self)
        self.text_memo.SetProps(Parent=self.layout_text, Align="Client", Text="Hello there! [laugh] I am Chatterbox Turbo. I can speak very quickly without losing quality. [chuckle]", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Control Buttons
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Speak Text", Width=150, OnClick=self.__generate_audio)

        # Output Info
        self.info_memo = Memo(self)
        self.info_memo.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)), ReadOnly=True, Text="Chatterbox-Turbo is a blazingly fast 350M parameter TTS model from Resemble AI. It features native paralinguistic tag support.")

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None

    def __form_show(self, sender):
        self.SetProps(Width=600, Height=500)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __generate_audio(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Sending request to Resemble..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            model = replicate.models.get("resemble-ai/chatterbox-turbo")
            
            self.prediction = replicate.predictions.create(
                model=model,
                input={
                    "text": self.text_memo.Text,
                    "voice": self.combo_voice.Text
                }
            )
            self.timer.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.generate_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction: return
        try:
            self.prediction.reload()
            status = self.prediction.status
            self.status_bar.Text = f"Status: {status}..."

            if status == "succeeded":
                self.timer.Enabled = False
                audio_url = self.prediction.output
                if isinstance(audio_url, list): audio_url = audio_url[0]
                
                file_hash = hashlib.md5(audio_url.encode()).hexdigest()
                file_name = f"./chatterbox_{file_hash}.wav"
                
                self.status_bar.Text = "Status: Succeeded! Downloading audio..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(audio_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.generate_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.generate_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.generate_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Chatterbox Turbo Demo"
    Application.MainForm = ChatterboxTurboApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
