import hashlib
import os
import urllib.request

import replicate
from delphifmx import *


class RembgBackgroundRemovalApp(Form):

    def __init__(self, owner):
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(
            Caption="Rembg Background Removal - Replicate Explore Pick",
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

        # File picker
        self.layout_input = Layout(self)
        self.layout_input.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=88,
            Margins=Bounds(RectF(0, 6, 0, 8)),
        )

        self.select_button = Button(self)
        self.select_button.SetProps(
            Parent=self.layout_input,
            Align="Top",
            Text="Select Input Image",
            Height=36,
            OnClick=self.__select_input_image,
        )

        self.input_label = Label(self)
        self.input_label.SetProps(
            Parent=self.layout_input,
            Align="Client",
            Text="No file selected",
            VertTextAlign="Center",
            Margins=Bounds(RectF(0, 8, 0, 0)),
        )

        # Control row
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=44,
            Margins=Bounds(RectF(0, 0, 0, 8)),
        )

        self.generate_button = Button(self)
        self.generate_button.SetProps(
            Parent=self.layout_controls,
            Align="Right",
            Text="Remove Background",
            Width=170,
            OnClick=self.__remove_background,
        )

        # Preview split
        self.layout_preview = Layout(self)
        self.layout_preview.SetProps(
            Parent=self.layout_main,
            Align="Client",
            Margins=Bounds(RectF(0, 8, 0, 0)),
        )

        self.input_image = ImageControl(self)
        self.input_image.SetProps(
            Parent=self.layout_preview,
            Align="Left",
            Width=380,
            Margins=Bounds(RectF(0, 0, 6, 0)),
        )

        self.output_image = ImageControl(self)
        self.output_image.SetProps(
            Parent=self.layout_preview,
            Align="Client",
            Margins=Bounds(RectF(6, 0, 0, 0)),
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

        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_file_path = None

    def __form_show(self, sender):
        self.SetProps(Width=920, Height=700)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_input_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Image Files|*.png;*.jpg;*.jpeg;*.webp"
        if od.Execute():
            self.selected_file_path = od.FileName
            self.input_label.Text = self.selected_file_path
            self.input_image.LoadFromFile(self.selected_file_path)
            self.output_image.Bitmap.SetSize(0, 0)

    def __remove_background(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        if not self.selected_file_path:
            self.status_bar.Text = "Status: Error - Please select an input image."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key

        self.status_bar.Text = "Status: Sending image to rembg..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="cjwbw/rembg",
                input={"image": open(self.selected_file_path, "rb")},
            )
            self.timer.Enabled = True
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
                self.status_bar.Text = "Status: Removing background..."
            elif status == "succeeded":
                self.timer.Enabled = False
                output = self.prediction.output

                image_url = None
                if isinstance(output, list) and output:
                    image_url = output[0]
                elif isinstance(output, dict):
                    image_url = output.get("image") or output.get("output")
                elif isinstance(output, str):
                    image_url = output

                if not image_url:
                    self.status_bar.Text = "Status: Error - No image URL in output."
                    self.generate_button.Enabled = True
                    return

                self.status_bar.Text = "Status: Downloading PNG with transparent background..."
                Application.ProcessMessages()

                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./output_rembg_{file_hash}.png"
                urllib.request.urlretrieve(image_url, file_name)

                self.output_image.LoadFromFile(file_name)
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
    Application.Title = "Rembg Background Removal - Replicate"
    Application.MainForm = RembgBackgroundRemovalApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()


if __name__ == "__main__":
    main()
