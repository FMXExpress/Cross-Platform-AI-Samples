import hashlib
import os
import urllib.request

import replicate
from delphifmx import *


class Flux2ProApp(Form):

    def __init__(self, owner):
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(
            Caption="FLUX.2 Pro - Replicate Explore Top Pick",
            OnShow=self.__form_show,
            OnClose=self.__form_close,
        )

        self.layout_main = Layout(self)
        self.layout_main.SetProps(
            Parent=self,
            Align="Client",
            Margins=Bounds(RectF(10, 10, 10, 10)),
        )

        # API key
        self.layout_api = Layout(self)
        self.layout_api.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=40,
            Margins=Bounds(RectF(0, 0, 0, 5)),
        )

        self.api_label = Label(self)
        self.api_label.SetProps(
            Parent=self.layout_api,
            Align="Left",
            Text="Replicate API Key:",
            Width=120,
            Margins=Bounds(RectF(0, 10, 5, 0)),
        )

        self.api_edit = Edit(self)
        self.api_edit.SetProps(Parent=self.layout_api, Align="Client", Password=True, Text="")
        if os.environ.get("REPLICATE_API_TOKEN"):
            self.api_edit.Text = os.environ.get("REPLICATE_API_TOKEN")

        # Prompt
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=145,
            Margins=Bounds(RectF(0, 6, 0, 8)),
        )

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(
            Parent=self.layout_prompt,
            Align="Top",
            Text="Prompt:",
            Height=24,
        )

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(
            Parent=self.layout_prompt,
            Align="Client",
            Margins=Bounds(RectF(0, 5, 0, 0)),
            Text="A cinematic astronaut portrait, soft rim lighting, 85mm lens look, ultra-detailed, magazine cover composition",
        )

        # Controls
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=44,
            Margins=Bounds(RectF(0, 0, 0, 8)),
        )

        self.aspect_label = Label(self)
        self.aspect_label.SetProps(
            Parent=self.layout_controls,
            Align="Left",
            Text="Aspect Ratio:",
            Width=86,
            Margins=Bounds(RectF(0, 11, 6, 0)),
        )

        self.combo_aspect = ComboBox(self)
        self.combo_aspect.SetProps(Parent=self.layout_controls, Align="Left", Width=110)
        self.combo_aspect.Items.Add("1:1")
        self.combo_aspect.Items.Add("16:9")
        self.combo_aspect.Items.Add("9:16")
        self.combo_aspect.Items.Add("3:2")
        self.combo_aspect.Items.Add("2:3")
        self.combo_aspect.ItemIndex = 0

        self.generate_button = Button(self)
        self.generate_button.SetProps(
            Parent=self.layout_controls,
            Align="Right",
            Text="Generate Image",
            Width=150,
            OnClick=self.__generate_image,
        )

        # Output
        self.img_result = ImageControl(self)
        self.img_result.SetProps(
            Parent=self.layout_main,
            Align="Client",
            Margins=Bounds(RectF(0, 8, 0, 0)),
        )

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(
            Parent=self,
            Align="Bottom",
            Text="Status: Ready",
            Height=30,
            Margins=Bounds(RectF(10, 0, 10, 5)),
        )

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None

    def __form_show(self, sender):
        self.SetProps(Width=820, Height=760)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __generate_image(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        prompt_text = self.prompt_memo.Text.strip()
        if not prompt_text:
            self.status_bar.Text = "Status: Error - Prompt is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key

        self.status_bar.Text = "Status: Initializing prediction..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="black-forest-labs/flux-2-pro",
                input={
                    "prompt": prompt_text,
                    "aspect_ratio": self.combo_aspect.Text,
                    "output_format": "jpg",
                },
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
                if isinstance(image_url, list):
                    image_url = image_url[0]

                self.status_bar.Text = "Status: Downloading result..."
                Application.ProcessMessages()

                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./output_flux2_{file_hash}.jpg"
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
    Application.Title = "FLUX.2 Pro - Replicate"
    Application.MainForm = Flux2ProApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()


if __name__ == "__main__":
    main()
