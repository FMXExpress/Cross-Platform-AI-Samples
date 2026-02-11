import base64
import mimetypes
import os

import replicate
from delphifmx import *


class Qwen25VLApp(Form):

    def __init__(self, owner):
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(
            Caption="Qwen2.5-VL - Image Understanding + OCR + Reasoning",
            OnShow=self.__form_show,
            OnClose=self.__form_close,
        )

        self.layout_main = Layout(self)
        self.layout_main.SetProps(
            Parent=self,
            Align="Client",
            Margins=Bounds(RectF(10, 10, 10, 10)),
        )

        # API Key
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

        # Image source controls
        self.layout_image = Layout(self)
        self.layout_image.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=206,
            Margins=Bounds(RectF(0, 5, 0, 10)),
        )

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(
            Parent=self.layout_image,
            Align="Left",
            Width=210,
            Margins=Bounds(RectF(0, 0, 10, 0)),
        )

        self.layout_image_inputs = Layout(self)
        self.layout_image_inputs.SetProps(Parent=self.layout_image, Align="Client")

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(
            Parent=self.layout_image_inputs,
            Align="Top",
            Height=35,
            Text="Choose Local Image",
            OnClick=self.__select_image,
        )

        self.selected_path_label = Label(self)
        self.selected_path_label.SetProps(
            Parent=self.layout_image_inputs,
            Align="Top",
            Height=42,
            Text="No local image selected.",
            VertTextAlign="Leading",
            Margins=Bounds(RectF(0, 6, 0, 8)),
        )

        self.url_label = Label(self)
        self.url_label.SetProps(
            Parent=self.layout_image_inputs,
            Align="Top",
            Height=22,
            Text="Or use image URL:",
            Margins=Bounds(RectF(0, 0, 0, 2)),
        )

        self.url_edit = Edit(self)
        self.url_edit.SetProps(
            Parent=self.layout_image_inputs,
            Align="Top",
            Height=34,
            Text="",
            Margins=Bounds(RectF(0, 0, 0, 6)),
        )

        self.url_hint_label = Label(self)
        self.url_hint_label.SetProps(
            Parent=self.layout_image_inputs,
            Align="Client",
            Text="Tip: local image takes priority over URL if both are set.",
            VertTextAlign="Leading",
        )

        # Prompt
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=130,
            Margins=Bounds(RectF(0, 0, 0, 10)),
        )

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Height=22, Text="Prompt:")

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(
            Parent=self.layout_prompt,
            Align="Client",
            Margins=Bounds(RectF(0, 5, 0, 0)),
            Text="Read all visible text, describe the image, and summarize key details in bullet points.",
        )

        # Controls
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(
            Parent=self.layout_main,
            Align="Top",
            Height=44,
            Margins=Bounds(RectF(0, 0, 0, 10)),
        )

        self.max_tokens_label = Label(self)
        self.max_tokens_label.SetProps(
            Parent=self.layout_controls,
            Align="Left",
            Width=86,
            Text="Max tokens:",
            Margins=Bounds(RectF(0, 11, 6, 0)),
        )

        self.max_tokens_box = ComboBox(self)
        self.max_tokens_box.SetProps(Parent=self.layout_controls, Align="Left", Width=90)
        self.max_tokens_box.Items.Add("256")
        self.max_tokens_box.Items.Add("512")
        self.max_tokens_box.Items.Add("1024")
        self.max_tokens_box.Items.Add("1536")
        self.max_tokens_box.ItemIndex = 1

        self.btn_run = Button(self)
        self.btn_run.SetProps(
            Parent=self.layout_controls,
            Align="Right",
            Width=170,
            Text="Analyze with Qwen2.5-VL",
            OnClick=self.__run_qwen,
        )

        # Output
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client")

        self.output_label = Label(self)
        self.output_label.SetProps(Parent=self.layout_output, Align="Top", Height=24, Text="Model response:")

        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_output, Align="Client", ReadOnly=True)

        # Status bar
        self.status_bar = Label(self)
        self.status_bar.SetProps(
            Parent=self,
            Align="Bottom",
            Height=30,
            Text="Status: Ready",
            Margins=Bounds(RectF(10, 0, 10, 5)),
        )

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
        dialog = OpenDialog(self)
        dialog.Filter = "Images|*.jpg;*.jpeg;*.png;*.webp;*.bmp"
        if dialog.Execute():
            self.selected_image_path = dialog.FileName
            self.img_preview.LoadFromFile(self.selected_image_path)
            self.selected_path_label.Text = self.selected_image_path

    def __image_file_to_data_uri(self, file_path):
        guessed_type = mimetypes.guess_type(file_path)[0]
        mime_type = guessed_type if guessed_type else "image/jpeg"

        with open(file_path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("utf-8")

        return f"data:{mime_type};base64,{encoded}"

    def __run_qwen(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API key is required."
            return

        prompt = self.prompt_memo.Text.strip()
        if not prompt:
            self.status_bar.Text = "Status: Error - prompt is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key

        image_input = None
        if self.selected_image_path:
            image_input = self.__image_file_to_data_uri(self.selected_image_path)
        elif self.url_edit.Text.strip():
            image_input = self.url_edit.Text.strip()

        self.btn_run.Enabled = False
        self.output_memo.Text = ""
        self.status_bar.Text = "Status: Starting prediction..."
        Application.ProcessMessages()

        try:
            model_input = {
                "prompt": prompt,
                "max_tokens": int(self.max_tokens_box.Items[self.max_tokens_box.ItemIndex]),
            }
            if image_input:
                model_input["image"] = image_input

            self.prediction = replicate.predictions.create(
                model="qwen/qwen2.5-vl-72b-instruct",
                input=model_input,
            )
            self.timer.Enabled = True
        except Exception as error:
            self.status_bar.Text = f"Status: Error - {str(error)}"
            self.btn_run.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction:
            return

        try:
            self.prediction.reload()
            current_status = self.prediction.status
            self.status_bar.Text = f"Status: {current_status}..."

            if current_status == "succeeded":
                self.timer.Enabled = False
                output = self.prediction.output
                if isinstance(output, list):
                    output = "".join(str(item) for item in output)
                elif isinstance(output, dict):
                    output = str(output)

                self.output_memo.Text = str(output)
                self.status_bar.Text = "Status: Done."
                self.btn_run.Enabled = True
            elif current_status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.output_memo.Text = str(self.prediction.error) if self.prediction.error else "No error details."
                self.status_bar.Text = f"Status: {current_status.capitalize()}."
                self.btn_run.Enabled = True
        except Exception as error:
            self.timer.Enabled = False
            self.status_bar.Text = f"Status: Polling error - {str(error)}"
            self.btn_run.Enabled = True


def main():
    Application.Initialize()
    Application.Title = "Qwen2.5-VL Demo"
    Application.MainForm = Qwen25VLApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()


if __name__ == "__main__":
    main()
