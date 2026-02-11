import os
import replicate
import urllib.request
import hashlib
import base64
from delphifmx import *

class GeminiFlashApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Gemini 3 Flash - Multimodal AI + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Multimodal Input Section (Image Selection)
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_main, Align="Top", Height=200, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(Parent=self.layout_image, Align="Left", Width=200, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image, Align="Top", Text="Select Image (Optional)", Height=35, OnClick=self.__select_image)

        self.image_path_label = Label(self)
        self.image_path_label.SetProps(Parent=self.layout_image, Align="Client", Text="No image selected", VertTextAlign="Leading", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Prompt Section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=100, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Enter your prompt:", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_prompt, Align="Client", Text="Describe this image in detail.", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Control Buttons
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.run_button = Button(self)
        self.run_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Run Gemini Flash", Width=150, OnClick=self.__run_gemini)

        # Output Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_label = Label(self)
        self.output_label.SetProps(Parent=self.layout_output, Align="Top", Text="Response:", Height=25)

        self.output_memo = Memo(self)
        self.output_memo.SetProps(Parent=self.layout_output, Align="Client", ReadOnly=True)

        # Status
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Text="Status: Ready", Height=30, Margins=Bounds(RectF(10, 0, 10, 5)))

        # Polling
        self.timer = Timer(self)
        self.timer.Interval = 1000
        self.timer.Enabled = False
        self.timer.OnTimer = self.__on_timer_tick

        self.prediction = None
        self.selected_image_path = None

    def __form_show(self, sender):
        self.SetProps(Width=700, Height=650)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Images|*.jpg;*.jpeg;*.png;*.webp"
        if od.Execute():
            self.selected_image_path = od.FileName
            self.img_preview.LoadFromFile(self.selected_image_path)
            self.image_path_label.Text = self.selected_image_path

    def __run_gemini(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Gemini..."
        self.run_button.Enabled = False
        self.output_memo.Text = ""
        Application.ProcessMessages()

        try:
            inputs = {
                "prompt": self.prompt_memo.Text
            }

            if self.selected_image_path:
                with open(self.selected_image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                    inputs["image"] = f"data:image/jpeg;base64,{image_data}"

            self.prediction = replicate.predictions.create(
                model="google/gemini-3-flash",
                input=inputs
            )
            self.timer.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.run_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction: return
        try:
            self.prediction.reload()
            status = self.prediction.status
            self.status_bar.Text = f"Status: {status}..."

            if status == "succeeded":
                self.timer.Enabled = False
                # Gemini output can be a list or string depending on version
                output = self.prediction.output
                if isinstance(output, list):
                    output = "".join(output)
                
                self.output_memo.Text = output
                self.status_bar.Text = "Status: Done."
                self.run_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.run_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.run_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Gemini 3 Flash Demo"
    Application.MainForm = GeminiFlashApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
