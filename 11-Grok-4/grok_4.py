import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class Grok4AssistantApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Grok 4 - Advanced Reasoning AI + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # Chat Section (Input)
        self.layout_chat = Layout(self)
        self.layout_chat.SetProps(Parent=self.layout_main, Align="Top", Height=120, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.chat_label = Label(self)
        self.chat_label.SetProps(Parent=self.layout_chat, Align="Top", Text="Enter your complex logic or analysis prompt (Grok 4):", Height=25)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_chat, Align="Client", Text="Explain the impact of decentralized computing on the future of AI scaling. Be concise and insightful.", Margins=Bounds(RectF(0, 5, 0, 5)))

        self.send_button = Button(self)
        self.send_button.SetProps(Parent=self.layout_main, Align="Top", Text="Consult Grok 4", Height=40, OnClick=self.__run_grok)

        # Output Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_label = Label(self)
        self.output_label.SetProps(Parent=self.layout_output, Align="Top", Text="Grok Response:", Height=25)

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

    def __form_show(self, sender):
        self.SetProps(Width=750, Height=650)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __run_grok(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Grok 4..."
        self.send_button.Enabled = False
        self.output_memo.Text = ""
        Application.ProcessMessages()

        try:
            self.prediction = replicate.predictions.create(
                model="xai/grok-4",
                input={
                    "prompt": self.prompt_memo.Text,
                    "max_tokens": 4096
                }
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
                
                self.output_memo.Text = str(output)
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
    Application.Title = "Grok 4 Demo"
    Application.MainForm = Grok4AssistantApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
