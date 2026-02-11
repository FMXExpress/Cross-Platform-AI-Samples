import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class QwenTTSApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Qwen3-TTS - Multilingual Speech + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Configuration Layout
        self.layout_config = Layout(self)
        self.layout_config.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.mode_label = Label(self)
        self.mode_label.SetProps(Parent=self.layout_config, Align="Left", Text="TTS Mode:", Width=70, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_mode = ComboBox(self)
        self.combo_mode.SetProps(Parent=self.layout_config, Align="Left", Width=100)
        self.combo_mode.Items.Add("Voice")
        self.combo_mode.Items.Add("Clone")
        self.combo_mode.Items.Add("Design")
        self.combo_mode.ItemIndex = 0
        self.combo_mode.OnChange = self.__on_mode_change

        self.voice_label = Label(self)
        self.voice_label.SetProps(Parent=self.layout_config, Align="Left", Text="Preset Voice:", Width=85, Margins=Bounds(RectF(10, 10, 5, 0)))

        self.combo_voice = ComboBox(self)
        self.combo_voice.SetProps(Parent=self.layout_config, Align="Left", Width=120)
        voices = ["English Female", "English Male", "Chinese Female", "Chinese Male", "Japanese Female", "Korean Female"]
        for v in voices:
            self.combo_voice.Items.Add(v)
        self.combo_voice.ItemIndex = 0

        # Reference Audio Section (For Clone mode)
        self.layout_clone = Layout(self)
        self.layout_clone.SetProps(Parent=self.layout_main, Align="Top", Height=40, Visible=False, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.ref_label = Label(self)
        self.ref_label.SetProps(Parent=self.layout_clone, Align="Left", Text="Ref Audio (URL):", Width=100, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.ref_edit = Edit(self)
        self.ref_edit.SetProps(Parent=self.layout_clone, Align="Client", Text="https://replicate.delivery/pbxt/JvX7nZ3KjL5n8o2f4e0d/ref.mp3")

        # Prompt Section
        self.layout_text = Layout(self)
        self.layout_text.SetProps(Parent=self.layout_main, Align="Top", Height=120, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.text_label = Label(self)
        self.text_label.SetProps(Parent=self.layout_text, Align="Top", Text="Enter text to synthesize:", Height=25)

        self.text_memo = Memo(self)
        self.text_memo.SetProps(Parent=self.layout_text, Align="Client", Text="Hello! I am Qwen3-TTS, a state-of-the-art speech generation model running on Replicate.", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Control Buttons
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Generate Audio", Width=150, OnClick=self.__generate_audio)

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
        self.SetProps(Width=650, Height=550)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __on_mode_change(self, sender):
        self.layout_clone.Visible = (self.combo_mode.Text == "Clone")
        self.combo_voice.Enabled = (self.combo_mode.Text == "Voice")

    def __generate_audio(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Sending request..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            params = {
                "text": self.text_memo.Text,
                "mode": self.combo_mode.Text.lower()
            }
            
            if params["mode"] == "voice":
                params["voice"] = self.combo_voice.Text
            elif params["mode"] == "clone":
                params["reference_audio"] = self.ref_edit.Text

            self.prediction = replicate.predictions.create(
                model="qwen/qwen3-tts",
                input=params
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
                file_name = f"./output_{file_hash}.mp3"
                urllib.request.urlretrieve(audio_url, file_name)

                self.status_bar.Text = f"Status: Succeeded! Audio saved to {file_name}"
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
    Application.Title = "Qwen3-TTS Demo"
    Application.MainForm = QwenTTSApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
