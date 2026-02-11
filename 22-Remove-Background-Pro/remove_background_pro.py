import hashlib
import os
import urllib.request

import replicate
from delphifmx import *


class RemoveBackgroundProApp(Form):

    def __init__(self, owner):
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(
            Caption="Remove Background Pro - Replicate Explore Sample #22",
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
            Margins=Bounds(RectF(0, 0, 0, 6)),
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

        # Input + output previews
        self.layout_images = Layout(self)
        self.layout_images.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=330,
            Margins=Bounds(RectF(0, 4, 0, 8)),
        )

        self.layout_input = Layout(self)
        self.layout_input.SetProps(
            Parent=self.layout_images,
            Align="Left",
            Width=390,
            Margins=Bounds(RectF(0, 0, 8, 0)),
        )

        self.btn_select = Button(self)
        self.btn_select.SetProps(
            Parent=self.layout_input,
            Align="Top",
            Text="Select Source Image",
            Height=35,
            OnClick=self.__select_image,
        )

        self.img_input = ImageControl(self)
        self.img_input.SetProps(
            Parent=self.layout_input,
            Align="Client",
            Margins=Bounds(RectF(0, 6, 0, 0)),
        )

        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_images, Align="Client")

        self.output_label = Label(self)
        self.output_label.SetProps(
            Parent=self.layout_output,
            Align="Top",
            Text="Background Removed Result:",
            Height=35,
            VertTextAlign="Center",
        )

        self.img_output = ImageControl(self)
        self.img_output.SetProps(
            Parent=self.layout_output,
            Align="Client",
            Margins=Bounds(RectF(0, 6, 0, 0)),
        )

        # Controls
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
        self.timer.Interval = 1200
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_image_path = None

    def __form_show(self, sender):
        self.SetProps(Width=860, Height=690)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_image(self, sender):
        open_dialog = OpenDialog(self)
        open_dialog.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.webp"
        if open_dialog.Execute():
            self.selected_image_path = open_dialog.FileName
            self.img_input.LoadFromFile(self.selected_image_path)
            self.status_bar.Text = f"Status: Selected {os.path.basename(self.selected_image_path)}"

    def __remove_background(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        if not self.selected_image_path:
            self.status_bar.Text = "Status: Error - Please select an image first."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key

        self.status_bar.Text = "Status: Initializing prediction..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="fofr/remove-background",
                input={"image": open(self.selected_image_path, "rb")},
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

                self.status_bar.Text = "Status: Downloading cutout..."
                Application.ProcessMessages()

                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./output_remove_bg_{file_hash}.png"
                urllib.request.urlretrieve(image_url, file_name)

                self.img_output.LoadFromFile(file_name)
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
    Application.Title = "Remove Background Pro - Replicate"
    Application.MainForm = RemoveBackgroundProApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()


if __name__ == "__main__":
    main()
