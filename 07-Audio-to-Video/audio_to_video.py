import os
import replicate
import urllib.request
import hashlib
import base64
from delphifmx import *

class AudioToVideoApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Audio-to-Video - Lightricks LTX-2 + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Audio Selection Section (Required)
        self.layout_audio = Layout(self)
        self.layout_audio.SetProps(Parent=self.layout_main, Align="Top", Height=60, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.btn_select_audio = Button(self)
        self.btn_select_audio.SetProps(Parent=self.layout_audio, Align="Left", Text="Select Audio File", Width=150, OnClick=self.__select_audio)

        self.audio_path_label = Label(self)
        self.audio_path_label.SetProps(Parent=self.layout_audio, Align="Client", Text="No audio file selected", VertTextAlign="Center", Margins=Bounds(RectF(10, 0, 0, 0)))

        # Optional Image Section
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_main, Align="Top", Height=140, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(Parent=self.layout_image, Align="Left", Width=140, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image, Align="Top", Text="Select Ref Image (Optional)", Height=35, OnClick=self.__select_image)

        self.image_path_label = Label(self)
        self.image_path_label.SetProps(Parent=self.layout_image, Align="Client", Text="No image selected", VertTextAlign="Leading", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Settings Section
        self.layout_settings = Layout(self)
        self.layout_settings.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.dur_label = Label(self)
        self.dur_label.SetProps(Parent=self.layout_settings, Align="Left", Text="Duration:", Width=65, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_dur = ComboBox(self)
        self.combo_dur.SetProps(Parent=self.layout_settings, Align="Left", Width=60)
        self.combo_dur.Items.Add("6")
        self.combo_dur.Items.Add("8")
        self.combo_dur.Items.Add("10")
        self.combo_dur.ItemIndex = 1

        self.res_label = Label(self)
        self.res_label.SetProps(Parent=self.layout_settings, Align="Left", Text="Res:", Width=40, Margins=Bounds(RectF(10, 10, 5, 0)))

        self.combo_res = ComboBox(self)
        self.combo_res.SetProps(Parent=self.layout_settings, Align="Left", Width=80)
        self.combo_res.Items.Add("720p")
        self.combo_res.Items.Add("1080p")
        self.combo_res.Items.Add("1440p")
        self.combo_res.ItemIndex = 1

        # Prompt Section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=80, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Visual Prompt (Style/Setting):", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_prompt, Align="Client", Text="cinematic close up, high quality, realistic lighting", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Generate Button
        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_main, Align="Top", Text="Generate Audio-Driven Video", Height=40, OnClick=self.__generate_video)

        # Output / Status
        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)), ReadOnly=True, Text="Select an audio file to begin. The audio will drive the performance and pacing.")

        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 2000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_audio_path = None
        self.selected_image_path = None

    def __form_show(self, sender):
        self.SetProps(Width=700, Height=680)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_audio(self, sender):
        od = OpenDialog(self)
        od.Filter = "Audio Files|*.mp3;*.wav;*.aac;*.m4a"
        if od.Execute():
            self.selected_audio_path = od.FileName
            self.audio_path_label.Text = self.selected_audio_path

    def __select_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.webp"
        if od.Execute():
            self.selected_image_path = od.FileName
            self.img_preview.LoadFromFile(self.selected_image_path)
            self.image_path_label.Text = self.selected_image_path

    def __generate_video(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return
        
        if not self.selected_audio_path:
            self.status_bar.Text = "Status: Error - Audio file is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Lightricks A2V..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            inputs = {
                "audio": open(self.selected_audio_path, "rb"),
                "prompt": self.prompt_memo.Text,
                "duration": int(self.combo_dur.Text),
                "resolution": self.combo_res.Text
            }
            if self.selected_image_path:
                inputs["image"] = open(self.selected_image_path, "rb")

            self.prediction = replicate.predictions.create(
                model="lightricks/audio-to-video",
                input=inputs
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Processing (audio/video joint generation)..."
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
                video_url = self.prediction.output
                if isinstance(video_url, list): video_url = video_url[0]
                
                file_hash = hashlib.md5(video_url.encode()).hexdigest()
                file_name = f"./a2v_lightricks_{file_hash}.mp4"
                
                self.status_bar.Text = "Status: Succeeded! Downloading video..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(video_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.output_memo.Text = f"Audio-to-Video Complete!\nURL: {video_url}\nPath: {os.path.abspath(file_name)}"
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
    Application.Title = "Lightricks Audio-to-Video Demo"
    Application.MainForm = AudioToVideoApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
