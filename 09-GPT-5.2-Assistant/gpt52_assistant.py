import os
import replicate
import urllib.request
import hashlib
import base64
from delphifmx import *

class GPT52AssistantApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="GPT-5.2 Assistant - Coding & Vision + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Config Layout (Model Variant selection)
        self.layout_config = Layout(self)
        self.layout_config.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.variant_label = Label(self)
        self.variant_label.SetProps(Parent=self.layout_config, Align="Left", Text="Model Variant:", Width=90, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_variant = ComboBox(self)
        self.combo_variant.SetProps(Parent=self.layout_config, Align="Left", Width=150)
        self.combo_variant.Items.Add("gpt-5.2-chat-latest")
        self.combo_variant.Items.Add("gpt-5.2")
        self.combo_variant.Items.Add("gpt-5.2-pro")
        self.combo_variant.ItemIndex = 0

        # Multimodal Section (Optional Image for Vision tasks)
        self.layout_image = Layout(self)
        self.layout_image.SetProps(Parent=self.layout_main, Align="Top", Height=140, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.img_preview = ImageControl(self)
        self.img_preview.SetProps(Parent=self.layout_image, Align="Left", Width=140, Margins=Bounds(RectF(0, 0, 10, 0)))

        self.btn_select_image = Button(self)
        self.btn_select_image.SetProps(Parent=self.layout_image, Align="Top", Text="Attach Image (Optional)", Height=35, OnClick=self.__select_image)

        self.image_info = Label(self)
        self.image_info.SetProps(Parent=self.layout_image, Align="Client", Text="GPT-5.2 excels at vision analysis and GUI understanding.", VertTextAlign="Leading", WordWrap=True, Margins=Bounds(RectF(0, 5, 0, 0)))

        # Chat Section (Input + Button)
        self.layout_chat = Layout(self)
        self.layout_chat.SetProps(Parent=self.layout_main, Align="Top", Height=120, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.chat_label = Label(self)
        self.chat_label.SetProps(Parent=self.layout_chat, Align="Top", Text="Enter your coding question or vision prompt:", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_chat, Align="Client", Text="Explain the architectural pattern in this image or write a Python script for a GUI.", Margins=Bounds(RectF(0, 5, 0, 5)))

        self.send_button = Button(self)
        self.send_button.SetProps(Parent=self.layout_main, Align="Top", Text="Send to GPT-5.2", Height=40, OnClick=self.__run_assistant)

        # Output Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_label = Label(self)
        self.output_label.SetProps(Parent=self.layout_output, Align="Top", Text="Assistant Response:", Height=25)

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
        self.SetProps(Width=750, Height=750)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_image(self, sender):
        od = OpenDialog(self)
        od.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.webp"
        if od.Execute():
            self.selected_image_path = od.FileName
            self.img_preview.LoadFromFile(self.selected_image_path)
            self.status_bar.Text = f"Image selected: {os.path.basename(self.selected_image_path)}"

    def __run_assistant(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = f"Status: Initializing GPT-5.2 ({self.combo_variant.Text})..."
        self.send_button.Enabled = False
        self.output_memo.Text = ""
        Application.ProcessMessages()

        try:
            inputs = {
                "prompt": self.prompt_memo.Text,
                "system_prompt": "You are a helpful and precise 10x developer assistant. Provide direct, technical, and accurate answers.",
                "max_tokens": 4096
            }
            
            if self.selected_image_path:
                with open(self.selected_image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                    # Assuming standard Replicate OpenAI multimodal input format
                    inputs["image"] = f"data:image/jpeg;base64,{image_data}"

            self.prediction = replicate.predictions.create(
                model=f"openai/{self.combo_variant.Text}",
                input=inputs
            )
            self.timer.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.send_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction: return
        try:
            self.prediction.reload()
            status = self.prediction.status
            self.status_bar.Text = f"Status: {status}..."

            if status == "succeeded":
                self.timer.Enabled = False
                output = self.prediction.output
                if isinstance(output, list):
                    output = "".join(output)
                
                self.output_memo.Text = output
                self.status_bar.Text = "Status: Response received."
                self.send_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.send_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.send_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "GPT-5.2 Assistant Demo"
    Application.MainForm = GPT52AssistantApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
