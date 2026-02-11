import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class FabricTalkingHeadApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="VEED Fabric 1.0 - Talking Head AI + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Media Selection Section
        self.layout_media = Layout(self)
        self.layout_media.SetProps(Parent=self.layout_main, Align="Top", Height=160, Margins=Bounds(RectF(0, 5, 0, 5)))

        # Image Selection
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_media, Align="Left", Width=200, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image, Align="Top", Text="Select Portrait Image", Height=35, OnClick=self.__select_image)

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(Parent=self.layout_image, Align="Client", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Audio Selection
        self.layout_audio = Layout(self)
        self.layout_audio.SetProps(Parent=self.layout_media, Align="Client")

        self.btn_select_audio = Button(self)
        self.btn_select_audio.SetProps(Parent=self.layout_audio, Align="Top", Text="Select Voice Audio", Height=35, OnClick=self.__select_audio)

        self.audio_path_label = Label(self)
        self.audio_path_label.SetProps(Parent=self.layout_audio, Align="Client", Text="No audio file selected", VertTextAlign="Center", WordWrap=True, Margins=Bounds(RectF(5, 5, 0, 0)))

        # Settings Section
        self.layout_settings = Layout(self)
        self.layout_settings.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.res_label = Label(self)
        self.res_label.SetProps(Parent=self.layout_settings, Align="Left", Text="Resolution:", Width=80, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_res = ComboBox(self)
        self.combo_res.SetProps(Parent=self.layout_settings, Align="Left", Width=100)
        self.combo_res.Items.Add("720p")
        self.combo_res.Items.Add("480p")
        self.combo_res.ItemIndex = 0

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_settings, Align="Right", Text="Generate Talking Head", Width=180, OnClick=self.__generate_video)

        # Output / Info
        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)), ReadOnly=True, Text="VEED Fabric 1.0 turns any portrait image into a talking video synchronized to your audio.")

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 2000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_image_path = None
        self.selected_audio_path = None

    def __form_show(self, sender):
        self.SetProps(Width=700, Height=600)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Image Files|*.jpg;*.jpeg;*.png"
        if od.Execute():
            self.selected_image_path = od.FileName
            self.img_preview.LoadFromFile(self.selected_image_path)
            self.status_bar.Text = f"Selected Image: {os.path.basename(self.selected_image_path)}"

    def __select_audio(self, sender):
        od = OpenDialog(self)
        od.Filter = "Audio Files|*.mp3;*.wav;*.m4a;*.aac"
        if od.Execute():
            self.selected_audio_path = od.FileName
            self.audio_path_label.Text = self.selected_audio_path
            self.status_bar.Text = f"Selected Audio: {os.path.basename(self.selected_audio_path)}"

    def __generate_video(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return
        
        if not self.selected_image_path or not self.selected_audio_path:
            self.status_bar.Text = "Status: Error - Both image and audio are required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing VEED Fabric..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            model = replicate.models.get("veed/fabric-1.0")
            
            # Note: Fabric 1.0 takes 'audio' and 'image' as files
            # Output resolution is passed via 'resolution'
            self.prediction = replicate.predictions.create(
                model=model,
                input={
                    "audio": open(self.selected_audio_path, "rb"),
                    "image": open(self.selected_image_path, "rb"),
                    "resolution": self.combo_res.Text
                }
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Generating talking head video..."
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
                file_name = f"./fabric_{file_hash}.mp4"
                
                self.status_bar.Text = "Status: Succeeded! Downloading video..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(video_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.output_memo.Text = f"Talking Head Generation Complete!\nURL: {video_url}\nPath: {os.path.abspath(file_name)}"
                self.generate_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                error_msg = self.prediction.error if self.prediction.error else "Failed."
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.output_memo.Text = f"Error: {error_msg}"
                self.generate_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.generate_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "VEED Fabric Talking Head Demo"
    Application.MainForm = FabricTalkingHeadApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
