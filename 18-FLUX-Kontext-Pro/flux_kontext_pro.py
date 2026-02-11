import os
import replicate
import urllib.request
import hashlib
from delphifmx import *


class FluxKontextProApp(Form):

    def __init__(self, owner):
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="FLUX Kontext Pro - Image Editing + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

        self.layout_main = Layout(self)
        self.layout_main.SetProps(Parent=self, Align="Client", Margins=Bounds(RectF(10, 10, 10, 10)))

        # API key
        self.layout_api = Layout(self)
        self.layout_api.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 0, 0, 5)))

        self.api_label = Label(self)
        self.api_label.SetProps(Parent=self.layout_api, Align="Left", Text="Replicate API Key:", Width=120, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.api_edit = Edit(self)
        self.api_edit.SetProps(Parent=self.layout_api, Align="Client", Password=True, Text="")
        if os.environ.get("REPLICATE_API_TOKEN"):
            self.api_edit.Text = os.environ.get("REPLICATE_API_TOKEN")

        # Input image section
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_main, Align="Top", Height=180, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.img_input = ImageControl(self)
        self.img_input.SetProps(Parent=self.layout_image, Align="Left", Width=180, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.layout_image_controls = Layout(self)
        self.layout_image_controls.SetProps(Parent=self.layout_image, Align="Client")

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image_controls, Align="Top", Text="Select Source Image (Optional)", Height=35, OnClick=self.__select_image)

        self.image_path_label = Label(self)
        self.image_path_label.SetProps(Parent=self.layout_image_controls, Align="Top", Text="No source image selected", WordWrap=True, Height=55, Margins=Bounds(RectF(0, 8, 0, 0)))

        self.aspect_layout = Layout(self)
        self.aspect_layout.SetProps(Parent=self.layout_image_controls, Align="Top", Height=40, Margins=Bounds(RectF(0, 8, 0, 0)))

        self.aspect_label = Label(self)
        self.aspect_label.SetProps(Parent=self.aspect_layout, Align="Left", Text="Aspect Ratio:", Width=90, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_aspect = ComboBox(self)
        self.combo_aspect.SetProps(Parent=self.aspect_layout, Align="Left", Width=145)
        self.combo_aspect.Items.Add("match_input_image")
        self.combo_aspect.Items.Add("1:1")
        self.combo_aspect.Items.Add("16:9")
        self.combo_aspect.Items.Add("9:16")
        self.combo_aspect.Items.Add("3:2")
        self.combo_aspect.Items.Add("2:3")
        self.combo_aspect.ItemIndex = 0

        # Prompt section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=135, Margins=Bounds(RectF(0, 8, 0, 8)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Edit Prompt:", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(
            Parent=self.layout_prompt,
            Align="Client",
            Text="Transform this image into a cinematic cyberpunk night scene with neon lighting, reflective wet streets, and subtle volumetric fog.",
            Margins=Bounds(RectF(0, 5, 0, 5))
        )

        # Controls
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Generate Edited Image", Width=180, OnClick=self.__generate)

        # Output image
        self.img_output = ImageControl(self)
        self.img_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 8, 0, 0)))

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling timer
        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_image_path = None

    def __form_show(self, sender):
        self.SetProps(Width=860, Height=760)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.webp"
        if od.Execute():
            self.selected_image_path = od.FileName
            self.img_input.LoadFromFile(self.selected_image_path)
            self.image_path_label.Text = self.selected_image_path

    def __generate(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        prompt_text = self.prompt_memo.Text.strip()
        if not prompt_text:
            self.status_bar.Text = "Status: Error - Prompt is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key

        input_payload = {
            "prompt": prompt_text,
            "aspect_ratio": self.combo_aspect.Text,
            "output_format": "jpg",
            "safety_tolerance": 2,
            "prompt_upsampling": True
        }

        if self.selected_image_path:
            input_payload["input_image"] = open(self.selected_image_path, "rb")

        self.status_bar.Text = "Status: Sending request to FLUX Kontext Pro..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="black-forest-labs/flux-kontext-pro",
                input=input_payload
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
            self.status_bar.Text = f"Status: {status}..."

            if status == "succeeded":
                self.timer.Enabled = False
                image_url = self.prediction.output
                if isinstance(image_url, list):
                    image_url = image_url[0]

                self.status_bar.Text = "Status: Downloading edited image..."
                Application.ProcessMessages()

                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./flux_kontext_{file_hash}.jpg"
                urllib.request.urlretrieve(image_url, file_name)

                self.img_output.LoadFromFile(file_name)
                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.generate_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                error_msg = self.prediction.error if self.prediction.error else "Request failed."
                self.status_bar.Text = f"Status: {status.capitalize()}."
                MessageDlg(f"Error: {error_msg}", TMsgDlgType.mtError, [TMsgDlgBtn.mbOK], 0)
                self.generate_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.generate_button.Enabled = True


def main():
    Application.Initialize()
    Application.Title = "FLUX Kontext Pro Demo"
    Application.MainForm = FluxKontextProApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()


if __name__ == '__main__':
    main()
