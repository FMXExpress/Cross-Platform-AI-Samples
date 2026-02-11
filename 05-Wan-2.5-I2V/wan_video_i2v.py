import os
import replicate
import urllib.request
import hashlib
import base64
from delphifmx import *

class WanVideoI2VApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Alibaba Wan 2.5 - Image to Video + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Image Selection Section
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_main, Align="Top", Height=160, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(Parent=self.layout_image, Align="Left", Width=160, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image, Align="Top", Text="Select Source Image", Height=35, OnClick=self.__select_image)

        self.image_path_label = Label(self)
        self.image_path_label.SetProps(Parent=self.layout_image, Align="Client", Text="No image selected", VertTextAlign="Leading", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Prompt Section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=80, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Motion Prompt:", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_prompt, Align="Client", Text="Cinematic camera move, subtle motion, high quality", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Controls Section
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.size_label = Label(self)
        self.size_label.SetProps(Parent=self.layout_controls, Align="Left", Text="Resolution:", Width=80, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_size = ComboBox(self)
        self.combo_size.SetProps(Parent=self.layout_controls, Align="Left", Width=100)
        self.combo_size.Items.Add("480p")
        self.combo_size.Items.Add("720p")
        self.combo_size.Items.Add("1080p")
        self.combo_size.ItemIndex = 1

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Generate Video", Width=150, OnClick=self.__generate_video)

        # Output Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_output, Align="Client", Text="Alibaba Wan 2.5 generates high-quality video from a static image.", ReadOnly=True)

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

    def __form_show(self, sender):
        self.SetProps(Width=700, Height=600)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

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
        
        if not self.selected_image_path:
            self.status_bar.Text = "Status: Error - Please select an image."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Wan 2.5..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="wan-video/wan-2.5-i2v",
                input={
                    "image": open(self.selected_image_path, "rb"),
                    "prompt": self.prompt_memo.Text,
                    "resolution": self.combo_size.Text
                }
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Generating video..."
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
                file_name = f"./wan_video_{file_hash}.mp4"
                
                self.status_bar.Text = "Status: Succeeded! Downloading video..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(video_url, file_name)

                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.output_memo.Text = f"Video Generation Complete!\nURL: {video_url}\nPath: {os.path.abspath(file_name)}"
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
    Application.Title = "Alibaba Wan 2.5 Demo"
    Application.MainForm = WanVideoI2VApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
