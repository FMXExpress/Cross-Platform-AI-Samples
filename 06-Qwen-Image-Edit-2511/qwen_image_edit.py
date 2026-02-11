import os
import replicate
import urllib.request
import hashlib
import base64
from delphifmx import *

class QwenImageEditApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Qwen Image Edit 2511 - Smart Editing + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Image Selection Section (Left/Right for Original/Edited)
        self.layout_images = Layout(self)
        self.layout_images.SetProps(Parent=self.layout_main, Align="Top", Height=250, Margins=Bounds(RectF(0, 5, 0, 5)))

        # Original Image
        self.layout_orig = Layout(self)
        self.layout_orig.SetProps(Parent=self.layout_images, Align="Left", Width=300, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_orig, Align="Top", Text="Select Source Image", Height=35, OnClick=self.__select_image)

        self.img_original = ImageControl(self)
        self.img_original.SetProps(Parent=self.layout_orig, Align="Client", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Result Image
        self.layout_res = Layout(self)
        self.layout_res.SetProps(Parent=self.layout_images, Align="Client")

        self.res_label = Label(self)
        self.res_label.SetProps(Parent=self.layout_res, Align="Top", Text="Edited Result:", Height=35, VertTextAlign="Center")

        self.img_result = ImageControl(self)
        self.img_result.SetProps(Parent=self.layout_res, Align="Client", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Prompt Section
        self.layout_prompt = Layout(self)
        self.layout_prompt.SetProps(Parent=self.layout_main, Align="Top", Height=80, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_prompt, Align="Top", Text="Edit Prompt (e.g., 'add a cat on the chair', 'change text to HELLO'):", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_prompt, Align="Client", Text="change the background to a sunny beach", Margins=Bounds(RectF(0, 5, 0, 5)))

        # Controls Section
        self.layout_controls = Layout(self)
        self.layout_controls.SetProps(Parent=self.layout_main, Align="Top", Height=40)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_controls, Align="Right", Text="Apply Edits", Width=150, OnClick=self.__generate_edit)

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
            self.img_original.LoadFromFile(self.selected_image_path)
            self.status_bar.Text = f"Selected: {os.path.basename(self.selected_image_path)}"

    def __generate_edit(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return
        
        if not self.selected_image_path:
            self.status_bar.Text = "Status: Error - Please select a source image."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Qwen Edit..."
        self.generate_button.Enabled = False
        Application.ProcessMessages()

        try:
            # Match the architecture of the working Interior Design demo
            model = replicate.models.get("qwen/qwen-image-edit-2511")
            
            # Use model object and wrap image in a list as required by this specific model
            self.prediction = replicate.predictions.create(
                model=model,
                input={
                    "image": [open(self.selected_image_path, "rb")],
                    "prompt": self.prompt_memo.Text
                }
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Processing edits..."
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
                image_url = self.prediction.output
                if isinstance(image_url, list): image_url = image_url[0]
                
                file_hash = hashlib.md5(image_url.encode()).hexdigest()
                file_name = f"./qwen_edit_{file_hash}.png"
                
                self.status_bar.Text = "Status: Succeeded! Downloading image..."
                Application.ProcessMessages()
                
                urllib.request.urlretrieve(image_url, file_name)

                self.img_result.LoadFromFile(file_name)
                self.status_bar.Text = f"Status: Done! Saved to {file_name}"
                self.generate_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                # Capture the specific error from Replicate logs/error field
                error_msg = self.prediction.error if self.prediction.error else "No error details provided."
                self.status_bar.Text = f"Status: {status.capitalize()}."
                # Show detailed error in the result label or memo
                self.res_label.Text = f"Detailed Error: {error_msg}"
                print(f"Replicate Error: {error_msg}")
                self.generate_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.generate_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Qwen Image Edit Demo"
    Application.MainForm = QwenImageEditApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
