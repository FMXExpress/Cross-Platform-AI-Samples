import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class AceStepApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="ACE-Step - Music Generation AI + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Config Layout
        self.layout_config = Layout(self)
        self.layout_config.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.dur_label = Label(self)
        self.dur_label.SetProps(Parent=self.layout_config, Align="Left", Text="Seconds:", Width=60, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.edit_duration = Edit(self)
        self.edit_duration.SetProps(Parent=self.layout_config, Align="Left", Text="10", Width=50)

        self.steps_label = Label(self)
        self.steps_label.SetProps(Parent=self.layout_config, Align="Left", Text="Steps:", Width=45, Margins=Bounds(RectF(15, 10, 5, 0)))

        self.edit_steps = Edit(self)
        self.edit_steps.SetProps(Parent=self.layout_config, Align="Left", Text="27", Width=50)

        # Prompt Section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=100, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Music Description:", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_prompt, Align="Client", Text="Upbeat synthwave track with heavy bass and futuristic lead melody", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Control Buttons
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Generate Music", Width=150, OnClick=self.__generate_music)

        # Output Info
        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)), ReadOnly=True, Text="ACE-Step is a blazingly fast music generation foundation model. It can generate high-quality music in seconds.")

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

    def __generate_music(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing ACE-Step..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            model = replicate.models.get("lucataco/ace-step")
            
            self.prediction = replicate.predictions.create(
                model=model,
                input={
                    "prompt": self.prompt_memo.Text,
                    "duration": int(self.edit_duration.Text),
                    "num_inference_steps": int(self.edit_steps.Text)
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
                file_name = f"./ace_step_{file_hash}.mp3"
                
                self.status_bar.Text = "Status: Succeeded! Downloading audio..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(audio_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.output_memo.Text = f"Music Generation Complete!\nURL: {audio_url}\nLocal Path: {os.path.abspath(file_name)}"
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
    Application.Title = "ACE-Step Music Gen Demo"
    Application.MainForm = AceStepApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
