import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class NanoBananaApp(Form):

    def __init__(self, owner):
        # Setting up the style and form properties
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Nano Banana Pro - Google DeepMind + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

        # Main layout container
        self.layout_main = Layout(self)
        self.layout_main.SetProps(Parent=self, Align="Client", Margins=Bounds(RectF(10, 10, 10, 10)))

        # API Key Section
        self.layout_api = Layout(self)
        self.layout_api.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 0, 0, 5)))

        self.api_label = Label(self)
        self.api_label.SetProps(Parent=self.layout_api, Align="Left", Text="Replicate API Key:", Width=120, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.api_edit = Edit(self)
        self.api_edit.SetProps(Parent=self.layout_api, Align="Client", Password=True, Text="")
        # Try to pull from environment as a default if it exists, otherwise empty
        if os.environ.get("REPLICATE_API_TOKEN"):
            self.api_edit.Text = os.environ.get("REPLICATE_API_TOKEN")

        # Top layout for prompt and controls
        self.layout_top = Layout(self)
        self.layout_top.SetProps(Parent=self.layout_main, Align="Top", Height=120, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_top, Align="Top", Text="Enter your prompt (Nano Banana Pro is great at text!):", Height=25)

        # Memo for the prompt
        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_top, Align="Client", Text="A vintage travel poster for Mars that says 'VISIT THE RED PLANET' in bold Art Deco typography, 8k resolution", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Controls layout (Button + Aspect Ratio)
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_top, Align="Bottom", Height=40)

        self.aspect_label = Label(self)
        self.aspect_label.SetProps(Parent=self.layout_controls, Align="Left", Text="Aspect Ratio:", Width=80, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_aspect = ComboBox(self)
        self.combo_aspect.SetProps(Parent=self.layout_controls, Align="Left", Width=100)
        self.combo_aspect.Items.Add("1:1")
        self.combo_aspect.Items.Add("16:9")
        self.combo_aspect.Items.Add("9:16")
        self.combo_aspect.Items.Add("3:2")
        self.combo_aspect.Items.Add("2:3")
        self.combo_aspect.ItemIndex = 0

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Generate Image", Width=150, OnClick=self.__generate_image)

        # Image display area
        self.img_result = ImageControl(self)
        self.img_result.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        # Status bar
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Timer for polling Replicate status
        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None

    def __form_show(self, sender):
        self.SetProps(Width=800, Height=750)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __generate_image(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        # Set the token for the replicate client
        os.environ["REPLICATE_API_TOKEN"] = api_key
        
        prompt_text = self.prompt_memo.Text
        aspect_ratio = self.combo_aspect.Text
        
        self.status_bar.Text = "Status: Initializing prediction..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="google/nano-banana-pro",
                input={
                    "prompt": prompt_text,
                    "aspect_ratio": aspect_ratio,
                    "output_format": "jpg",
                    "output_quality": 85
                }
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Request sent to Replicate..."
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.generate_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction:
            return

        try:
            self.prediction.reload()
            status = self.prediction.status
            
            if status == "starting":
                self.status_bar.Text = "Status: Starting model..."
            elif status == "processing":
                self.status_bar.Text = "Status: Generating image..."
            elif status == "succeeded":
                self.timer.Enabled = False
                image_url = self.prediction.output
                # Replicate Pro Ultra usually returns a single URL string for the image
                if isinstance(image_url, list):
                    image_url = image_url[0]
                
                self.status_bar.Text = "Status: Downloading result..."
                Application.ProcessMessages()

                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./output_{file_hash}.jpg"
                urllib.request.urlretrieve(image_url, file_name)

                self.img_result.LoadFromFile(file_name)
                self.status_bar.Text = f"Status: Succeeded! Saved as {file_name}"
                self.generate_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.status_bar.Text = f"Status: Prediction {status}."
                self.generate_button.Enabled = True
                
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.generate_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Nano Banana - AI Image Generator"
    Application.MainForm = NanoBananaApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
