import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class CrystalUpscalerApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Crystal Video Upscaler - AI Clarity + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Video Selection Section
        self.layout_video = Layout(self)
        self.layout_video.SetProps(Parent=self.layout_main, Align="Top", Height=80, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.btn_select_video = Button(self)
        self.btn_select_video.SetProps(Parent=self.layout_video, Align="Top", Text="Select Source Video", Height=35, OnClick=self.__select_video)

        self.video_path_label = Label(self)
        self.video_path_label.SetProps(Parent=self.layout_video, Align="Client", Text="No video selected", VertTextAlign="Center", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Config Section
        self.layout_config = Layout(self)
        self.layout_config.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.scale_label = Label(self)
        self.scale_label.SetProps(Parent=self.layout_config, Align="Left", Text="Upscale Factor:", Width=100, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_scale = ComboBox(self)
        self.combo_scale.SetProps(Parent=self.layout_config, Align="Left", Width=60)
        self.combo_scale.Items.Add("2")
        self.combo_scale.Items.Add("4")
        self.combo_scale.ItemIndex = 0

        self.mode_label = Label(self)
        self.mode_label.SetProps(Parent=self.layout_config, Align="Left", Text="Mode:", Width=50, Margins=Bounds(RectF(15, 10, 5, 0)))

        self.combo_mode = ComboBox(self)
        self.combo_mode.SetProps(Parent=self.layout_config, Align="Left", Width=120)
        self.combo_mode.Items.Add("portrait")
        self.combo_mode.Items.Add("landscape")
        self.combo_mode.Items.Add("clarity_ai")
        self.combo_mode.ItemIndex = 2

        self.upscale_button = Button(self)
        self.upscale_button.SetProps(Parent=self.layout_config, Align="Right", Text="Start Upscale", Width=150, OnClick=self.__start_upscale)

        # Output / Instructions Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_output, Align="Client", Text="Crystal Video Upscaler is optimized for faces and textures.\n\nSelect a video to begin.", ReadOnly=True)

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 2000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_video_path = None

    def __form_show(self, sender):
        self.SetProps(Width=650, Height=450)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_video(self, sender):
        od = OpenDialog(self)
        od.Filter = "Video Files|*.mp4;*.mov;*.avi;*.mkv"
        if od.Execute():
            self.selected_video_path = od.FileName
            self.video_path_label.Text = self.selected_video_path

    def __start_upscale(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return
        
        if not self.selected_video_path:
            self.status_bar.Text = "Status: Error - Please select a video file."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Replicate prediction..."
        self.upscale_button.Enabled = False
        Application.ProcessMessages()

        try:
            # Note: Video upscaling can take time. We use the file handle.
            self.prediction = replicate.predictions.create(
                model="philz1337x/crystal-video-upscaler",
                input={
                    "video": open(self.selected_video_path, "rb"),
                    "upscale_factor": int(self.combo_scale.Text),
                    "mode": self.combo_mode.Text
                }
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Processing video (this may take a few minutes)..."
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.upscale_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction: return
        try:
            self.prediction.reload()
            status = self.prediction.status
            
            # Log progress if available
            if self.prediction.logs:
                logs = self.prediction.logs.strip().split('\n')
                if logs:
                    self.status_bar.Text = f"Status: {logs[-1]}"

            if status == "succeeded":
                self.timer.Enabled = False
                video_url = self.prediction.output
                
                file_hash = hashlib.md5(video_url.encode()).hexdigest()
                file_name = f"./upscaled_{file_hash}.mp4"
                
                self.status_bar.Text = "Status: Succeeded! Downloading upscaled video..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(video_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.output_memo.Text = f"Upscale Complete!\nURL: {video_url}\nLocal Path: {os.path.abspath(file_name)}"
                self.upscale_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.upscale_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.upscale_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Crystal Video Upscaler Demo"
    Application.MainForm = CrystalUpscalerApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
