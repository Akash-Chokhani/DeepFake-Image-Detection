import wx
import threading

import process


class MyFrame(wx.Frame):
    def __init__(self):
        super(MyFrame, self).__init__(
            parent=None, title="DeepFake", size=(500, 400))
        self.InitUI()
        self.Centre()

    def InitUI(self):
        self.panel = wx.Panel(self)

        self.imagePanel = wx.Panel(self.panel, size=(440, 300), pos=(20, 10))
        self.imagePanel.SetBackgroundColour(
            wx.Colour(200, 200, 200))

        self.imageCtrl = wx.StaticBitmap(
            self.imagePanel, size=self.imagePanel.GetSize())
        self.imageCtrl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterImage)
        self.imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveImage)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnChange)

        self.uploadText = wx.StaticText(
            self.imagePanel, label="Click Here\nto\nUpload Image", style=wx.ALIGN_CENTER)

        self.predictButton = wx.Button(
            self.panel, label="Predict", pos=(360, 322))
        self.predictButton.Bind(wx.EVT_BUTTON, self.OnPredict)
        self.predictButton.Disable()

        self.imageLabel = wx.StaticText(
            self.panel, label="", pos=(340, 315))
        self.imageLabel.Hide()

        self.ModelLabel = wx.StaticText(
            self.panel, label="Model:", pos=(50, 326))
        self.ModelChoice = wx.Choice(self.panel, pos=(100, 322), size=(
            80, -1), choices=list(process.model_list.keys()))
        self.ModelChoice.Bind(wx.EVT_CHOICE, self.OnSelection)
        self.ModelChoice.SetSelection(0)

        self.UIStyle()

    def UIStyle(self):
        # Set larger font size for upload text
        self.uploadText.Wrap(width=-1)
        uploadTextFont = self.uploadText.GetFont()
        uploadTextFont.PointSize += 8
        self.uploadText.SetFont(uploadTextFont)
        self.uploadText.Center()

        # Set larger font size for image label
        font = self.imageLabel.GetFont()
        font.PointSize += 8
        self.imageLabel.SetFont(font)

    def OnEnterImage(self, event):
        # Change cursor to a hand cursor
        self.imageCtrl.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def OnLeaveImage(self, event):
        # Revert cursor to default
        self.imageCtrl.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

    def OnChange(self, event):
        # Open file dialog to select an image
        with wx.FileDialog(self, "Choose an image", wildcard="Image files (*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            self.imagePath = fileDialog.GetPath()
            self.LoadImage()

            # Enable predict button on changing image
            self.imageLabel.Hide()
            self.predictButton.Show()
            self.predictButton.Enable()

    def LoadImage(self):
        # Load the image
        img = wx.Image(self.imagePath, wx.BITMAP_TYPE_ANY)

        # Get the size of the image and the panel
        imgWidth, imgHeight = img.GetSize()
        panelWidth, panelHeight = self.imagePanel.GetSize()

        # Calculate the aspect ratio of the image and the panel
        imgRatio = imgWidth / imgHeight
        panelRatio = panelWidth / panelHeight

        # Determine the new size of the image to maintain aspect ratio
        if imgRatio > panelRatio:
            newWidth = panelWidth
            newHeight = panelWidth / imgRatio
        else:
            newHeight = panelHeight
            newWidth = panelHeight * imgRatio

        # Convert newWidth and newHeight to integers
        newWidth = int(newWidth)
        newHeight = int(newHeight)

        # Scale the image
        img = img.Scale(newWidth, newHeight, wx.IMAGE_QUALITY_HIGH)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))

        # Update the image control with the scaled image
        self.imageCtrl.SetSize(newWidth, newHeight)
        self.imageCtrl.Center()
        self.imagePanel.SetBackgroundColour(self.panel.GetBackgroundColour())

        self.uploadText.Hide()
        self.Refresh()

    def OnSelection(self, event):
        # Enable predict button on changing model
        self.imageLabel.Hide()
        self.predictButton.Show()

    def OnPredict(self, event):
        # Change the button label to indicate loading
        self.predictButton.SetLabel("Predicting...")
        self.predictButton.Disable()

        # Start the prediction in a new thread
        self.thread = threading.Thread(target=self.RunPrediction, args=())
        self.thread.daemon = True
        self.thread.start()

    def RunPrediction(self):
        # Start prediction
        selectedModel = self.ModelChoice.GetString(
            self.ModelChoice.GetSelection())
        prediction = process.predict(selectedModel, self.imagePath)

        # Update UI based on result
        if prediction < 0.5:
            self.imageLabel.SetLabel("Fake Image")
            self.imageLabel.SetForegroundColour(wx.RED)
        else:
            self.imageLabel.SetLabel("Real Image")
            self.imageLabel.SetForegroundColour(wx.GREEN)

        # Update UI
        wx.CallAfter(self.PredictionComplete)

    def PredictionComplete(self):
        # Show the prediction result
        self.predictButton.Hide()
        self.imageLabel.Show()

        # Enable predict button
        self.predictButton.SetLabel("Predict")
        self.predictButton.Enable()


def main():
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
