import os
import replicate
import urllib.request
import hashlib
from delphifmx import *

class InsanelyFastWhisperApp(Form):

    def __init__(self, owner):
        # Setup Style
        self.stylemanager = StyleManager(self)
        if os.path.exists("Air.style"):
            self.stylemanager.SetStyleFromFile("Air.style")

        self.SetProps(Caption="Insanely Fast Whisper - AI Transcription + Replicate", OnShow=self.__form_show, OnClose=self.__form_close)

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

        # File Selection Section
        self.layout_file = Layout(self)
        self.layout_file.SetProps(Parent=self.layout_main, Align="Top", Height=80, Margins=Bounds(RectF(0, 5, 0, 5)))

        self.btn_select_file = Button(self)
        self.btn_select_file.SetProps(Parent=self.layout_file, Align="Top", Text="Select Audio/Video File", Height=35, OnClick=self.__select_file)

        self.file_path_label = Label(self)
        self.file_path_label.SetProps(Parent=self.layout_file, Align="Client", Text="No file selected", VertTextAlign="Center", Margins=Bounds(RectF(0, 5, 0, 0)))

        # Settings Section
        self.layout_settings = Layout(self)
        self.layout_settings.SetProps(Parent=self.layout_main, Align="Top", Height=40, Margins=Bounds(RectF(0, 5, 0, 10)))

        self.task_label = Label(self)
        self.task_label.SetProps(Parent=self.layout_settings, Align="Left", Text="Task:", Width=40, Margins=Bounds(RectF(0, 10, 5, 0)))

        self.combo_task = ComboBox(self)
        self.combo_task.SetProps(Parent=self.layout_settings, Align="Left", Width=100)
        self.combo_task.Items.Add("transcribe")
        self.combo_task.Items.Add("translate")
        self.combo_task.ItemIndex = 0

        self.lang_label = Label(self)
        self.lang_label.SetProps(Parent=self.layout_settings, Align="Left", Text="Language:", Width=70, Margins=Bounds(RectF(15, 10, 5, 0)))

        self.edit_lang = Edit(self)
        self.edit_lang.SetProps(Parent=self.layout_settings, Align="Left", Text="auto", Width=60)

        self.transcribe_button = Button(self)
        self.transcribe_button.SetProps(Parent=self.layout_settings, Align="Right", Text="Start Transcription", Width=150, OnClick=self.__start_transcription)

        # Output Section
        self.layout_output = Layout(self)
        self.layout_output.SetProps(Parent=self.layout_main, Align="Client", Margins=Bounds(RectF(0, 10, 0, 0)))

        self.output_label = Label(self)
        self.output_label.SetProps(Parent=self.layout_output, Align="Top", Text="Transcription:", Height=25)

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
        self.selected_file_path = None

    def __form_show(self, sender):
        self.SetProps(Width=700, Height=600)

    def __form_close(self, sender, action):
        self.timer.Enabled = False
        action = "caFree"

    def __select_file(self, sender):
        od = OpenDialog(self)
        od.Filter = "Media Files|*.mp3;*.wav;*.mp4;*.mkv;*.avi;*.mov;*.aac;*.m4a"
        if od.Execute():
            self.selected_file_path = od.FileName
            self.file_path_label.Text = self.selected_file_path

    def __start_transcription(self, sender):
        api_key = self.api_edit.Text.strip()
        if not api_key:
            self.status_bar.Text = "Status: Error - API Key is required."
            return
        
        if not self.selected_file_path:
            self.status_bar.Text = "Status: Error - Please select a file."
            return

        os.environ["REPLICATE_API_TOKEN"] = api_key
        self.status_bar.Text = "Status: Initializing Whisper..."
        self.transcribe_button.Enabled = False
        self.output_memo.Text = ""
        Application.ProcessMessages()

        try:
            # Model object style
            model = replicate.models.get("turian/insanely-fast-whisper-with-video")
            
            # Transcription parameters
            inputs = {
                "audio": open(self.selected_file_path, "rb"),
                "task": self.combo_task.Text,
                "language": self.edit_lang.Text,
                "timestamp": "chunk"
            }

            self.prediction = replicate.predictions.create(
                model=model,
                input=inputs
            )
            self.timer.Enabled = True
            self.status_bar.Text = "Status: Transcribing blazingly fast..."
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"
            self.transcribe_button.Enabled = True

    def __on_timer_tick(self, sender):
        if not self.prediction: return
        try:
            self.prediction.reload()
            status = self.prediction.status
            self.status_bar.Text = f"Status: {status}..."

            if status == "succeeded":
                self.timer.Enabled = False
                # The model returns a dictionary usually with 'text' or 'chunks'
                output = self.prediction.output
                
                result_text = ""
                if isinstance(output, dict):
                    result_text = output.get("text", str(output))
                else:
                    result_text = str(output)
                
                self.output_memo.Text = result_text
                self.status_bar.Text = "Status: Finished."
                self.transcribe_button.Enabled = True
            elif status in ["failed", "canceled"]:
                self.timer.Enabled = False
                error_msg = self.prediction.error if self.prediction.error else "Failed."
                self.status_bar.Text = f"Status: {status.capitalize()}."
                self.output_memo.Text = f"Error: {error_msg}"
                self.transcribe_button.Enabled = True
        except Exception as e:
            self.status_bar.Text = f"Status: Polling error - {str(e)}"
            self.timer.Enabled = False
            self.transcribe_button.Enabled = True

def main():
    Application.Initialize()
    Application.Title = "Insanely Fast Whisper Demo"
    Application.MainForm = InsanelyFastWhisperApp(Application)
    Application.MainForm.Show()
    Application.Run()
    Application.MainForm.Destroy()

if __name__ == '__main__':
    main()
