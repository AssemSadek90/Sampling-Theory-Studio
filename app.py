# !/usr/bin/python

import ast
from math import floor
from plotter import Plot
from plotterMatplotlib import MplCanvas

# Definition of Main Color Palette
from Defs import COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, COLOR6

# importing Qt widgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QFileInfo

# importing numpy and pandas
import numpy as np
import pandas as pd

# importing pyqtgraph as pg
import pyqtgraph as pg
from pyqtgraph.dockarea import *

import sys
import os

# CONST
TMIN = 0
TMAX = np.pi


class TableView(QTableWidget):
    def __init__(self, *args):
        QTableWidget.__init__(self, *args)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Frequency', 'Magnitude', 'Phase'])

    def addData(self, frequency, magnitude, phase):
        rowPosition = self.rowCount()

        self.insertRow(rowPosition)
        self.setItem(rowPosition, 0, QTableWidgetItem(f"{frequency}Hz"))
        self.setItem(rowPosition, 1, QTableWidgetItem(f"{magnitude}"))
        self.setItem(rowPosition, 2, QTableWidgetItem(f"{phase}°"))

    def clearAllData(self):
        self.setRowCount(0)


class Window(QMainWindow):
    """Main Window."""

    def __init__(self):
        """Initializer."""
        super().__init__()

        # Initialize Variables
        self.mainDataPlot = []
        self.timePlot = []
        self.signalSummition = [0 for _ in range(0, 1000)]
        self.hidden = False
        self.maxFreq = 0
        self.currentFrequency = 0

        # setting Icon
        self.setWindowIcon(QIcon('images/icon.png'))

        # setting title
        self.setWindowTitle("Nyquist Theorem Illustrator")

        # UI contents
        self.createMenuBar()

        # self.createtoolBar()
        self.initUI()

        # Status Bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(f"""font-size:13px;
                                 padding: 3px; 
                                 color: {COLOR1}; 
                                 font-weight:900;""")
        self.statusBar.showMessage("Welcome to our application...")
        self.setStatusBar(self.statusBar)

        self.connect()

    # Menu
    def createMenuBar(self):

        # MenuBar
        menuBar = self.menuBar()

        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)

        openFile = QAction("Open...", self)
        openFile.setShortcut("Ctrl+o")
        openFile.setStatusTip('Open a new signal')
        openFile.triggered.connect(self.browseSignal)

        fileMenu.addAction(openFile)

        quit = QAction("Exit", self)
        quit.setShortcut("Ctrl+q")
        quit.setStatusTip('Exit application')
        quit.triggered.connect(self.exit)

        fileMenu.addAction(quit)

        # Add file tab to the menu
        menuBar.addMenu(fileMenu)

    # GUI
    def initUI(self):
        centralMainWindow = QWidget(self)
        self.setCentralWidget(centralMainWindow)
        self.setGeometry(120, 80, 1400, 900)

        # Outer Layout
        outerLayout = QVBoxLayout()

        ######### INIT GUI #########
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""color:{COLOR1}; 
                        font-size:15px;""")

        self.samplingTab = QWidget()
        self.samplingTab.setStyleSheet(f"""background: {COLOR5}""")
        self.composerTab = QWidget()
        self.composerTab.setStyleSheet(f"""background: {COLOR5}""")

        self.samplingLayout()
        self.composerLayout()

        # Add tabs
        self.tabs.addTab(self.samplingTab, "Sampling")
        self.tabs.addTab(self.composerTab, "Composer")

        outerLayout.addWidget(self.tabs)
        ######### INIT GUI #########

        centralMainWindow.setLayout(outerLayout)

    # Sampling
    def samplingLayout(self):
        outerSamplingLayout = QVBoxLayout()

        samplingLayout = QHBoxLayout()

        # Main Layout
        mainLayout = QVBoxLayout()

        # Main Plot
        self.mainPlot = MplCanvas("Main Plot")
        self.mainPlot.setMinimumSize(400, 300)

        # Main Buttons Layout
        self.mainButtons = QHBoxLayout()

        # Sampling slider
        self.frequencyStartLabel = QLabel("1")
        self.frequencyStartLabel.setStyleSheet(
            "font-size: 13px;padding: 2px;font-weight: 800;")

        self.sliderMainPlot = QSlider(Qt.Horizontal, self)
        self.sliderMainPlot.setMinimum(1)
        self.sliderMainPlot.setMouseTracking(False)
        self.sliderMainPlot.setSingleStep(50)
        self.sliderMainPlot.setMaximum(400)

        self.frequencyEndLabel = QLabel(u'4 F\u2098\u2090\u2093')

        self.frequencyEndLabel.setStyleSheet(
            "font-size: 13px;padding: 2px;font-weight: 800;")

        noiseLayout = QHBoxLayout()

        # Noise slider
        self.noiseLabel = QLabel("Noise")
        self.noiseLabel.setStyleSheet(
            "font-size: 13px;padding: 2px;font-weight: 800;")

        self.noiseSlider = QSlider(Qt.Horizontal, self)
        self.noiseSlider.setMinimum(-10)
        self.noiseSlider.setMouseTracking(False)
        self.noiseSlider.setSingleStep(1)
        self.noiseSlider.setMaximum(25)
        self.noiseSlider.setValue(25)

        self.snrLabel = QLabel("20 db")
        self.snrLabel.setStyleSheet(
            "font-size: 13px;padding: 2px;font-weight: 800;")

        noiseLayout.addSpacerItem(
            QSpacerItem(100, 50, QSizePolicy.Minimum))
        noiseLayout.addWidget(self.noiseLabel)
        noiseLayout.addWidget(self.noiseSlider)
        noiseLayout.addWidget(self.snrLabel)
        noiseLayout.addSpacerItem(
            QSpacerItem(100, 50, QSizePolicy.Minimum))

        # Reconstruct signal type : dotted or secondary graph
        self.reconstructType = QComboBox()
        self.reconstructType.setStyleSheet(f"""font-size:14px;
                                    height: 25px;
                                    padding: 0px 5px;
                                    background: {COLOR6};
                                    color:{COLOR1};""")
        self.reconstructType.addItem("Choose")
        self.reconstructType.addItem("Dotted signal")
        self.reconstructType.addItem("In Secondary graph")

        self.mainButtons.addSpacerItem(
            QSpacerItem(100, 50, QSizePolicy.Minimum))
        self.mainButtons.addWidget(self.frequencyStartLabel)
        self.mainButtons.addWidget(self.sliderMainPlot)
        self.mainButtons.addWidget(self.frequencyEndLabel)
        self.mainButtons.addSpacerItem(
            QSpacerItem(100, 50, QSizePolicy.Minimum))

        self.mainButtons.setSizeConstraint(QLayout.SetMaximumSize)

        mainLayout.addWidget(self.mainPlot)

        # Reconstraction layout
        reconstructionLayout = QVBoxLayout()

        # Reconstraction plot
        self.reconstractionPlot = MplCanvas(title="Reconstruction Plot")
        self.reconstractionPlot.setMinimumSize(400, 300)

        reconstructionLayout.addWidget(self.reconstractionPlot)

        samplingLayout.addLayout(mainLayout)
        samplingLayout.addLayout(reconstructionLayout)

        outerSamplingLayout.addLayout(samplingLayout)
        outerSamplingLayout.addLayout(self.mainButtons)
        outerSamplingLayout.addLayout(noiseLayout)

        self.samplingTab.setLayout(outerSamplingLayout)

        # difference Layout
        differenceLayout = QVBoxLayout()
        self.differencePlot = MplCanvas(title="Difference Plot")
        self.differencePlot.setMinimumSize(800, 300)

        differenceLayout.addWidget(self.differencePlot)

        outerSamplingLayout.addLayout(differenceLayout)

    # Frequency change

    def freqChange(self, value):
        sampling_freq = float(value)/100 * float(self.maxFreq)
        self.currentFrequency = sampling_freq

        # Update values of labels of slider
        self.frequencyStartLabel.setText(str(round(sampling_freq, 1)) + " Hz")
        text = str(value/100) + u'F\u2098\u2090\u2093'
        self.frequencyEndLabel.setText(text)

        # Sample signal
        sampledTime, sampledSignal = self.mainPlot.sampleSingal(sampling_freq)

        # Update Data in reconstructed Plot
        self.reconstractionPlot.set_data(
            self.mainPlot.yNoisy, self.mainPlot.x, sampling_freq, sampledTime, sampledSignal)
        self.reconstructSample()
        self.plotDifference()

    def snrChange(self, value):
        self.snrLabel.setText(str(round(value, 1)) + "db")
        self.mainPlot.addNoiseToSignal(value)

        # Get the current frequency from the mainPlot
        current_frequency = self.currentFrequency

        # Sample signal with the same frequency
        sampledTime, sampledSignal = self.mainPlot.sampleSingal(
            current_frequency)

        # Update Data in reconstructed Plot
        self.reconstractionPlot.set_data(
            self.mainPlot.yNoisy, self.mainPlot.x, current_frequency, sampledTime, sampledSignal)
        self.reconstructSample()
        self.plotDifference()

    # Composer Layout Tab

    def composerLayout(self):
        composerLayout = QVBoxLayout()

        # Sinusoidal Layout
        sinusoidalLayout = QHBoxLayout()

        panelGroupBox = QGroupBox("Sinusoidal Signal Panel")
        panelSinusoidal = QVBoxLayout()
        panelGroupBox.setLayout(panelSinusoidal)

        # Frequency Text Box
        self.freqBox = QSpinBox(self)
        self.freqBox.setStyleSheet(f"""font-size:14px; 
                            padding: 5px 15px; 
                            background: {COLOR4};
                            color: {COLOR1};""")
        self.freqBox.setValue(int(1))
        # Magnitude Text Box
        self.magnitudeBox = QSpinBox(self)
        self.magnitudeBox.setStyleSheet(f"""font-size:14px; 
                                padding: 5px 15px; 
                                background: {COLOR4};
                                color: {COLOR1};""")
        self.magnitudeBox.setValue(int(1))
        # Phase Text Box
        self.phaseBox = QSpinBox(self)
        self.phaseBox.setStyleSheet(f"""font-size:14px; 
                            padding: 5px 15px; 
                            background: {COLOR4};
                            color: {COLOR1};""")
        self.phaseBox.setValue(int(0))

        self.plotButton = QPushButton("Plot | Add")
        self.plotButton.setStyleSheet(f"""font-size:14px; 
                            border-radius: 6px;
                            border: 1px solid {COLOR1};
                            padding: 5px 15px; 
                            background: {COLOR2}; 
                            color: {COLOR6};""")

        self.plotButton.setIcon(QIcon("images/plot.svg"))

        panelSinusoidal.addWidget(QLabel("Frequency:"))
        panelSinusoidal.addWidget(self.freqBox)
        panelSinusoidal.addWidget(QLabel("Magnitude:"))
        panelSinusoidal.addWidget(self.magnitudeBox)
        panelSinusoidal.addWidget(QLabel("Phase:"))
        panelSinusoidal.addWidget(self.phaseBox)
        panelSinusoidal.addWidget(self.plotButton)

        # Sinusoidal Plot
        self.sinusoidalPlot = Plot()

        sinusoidalLayout.addWidget(panelGroupBox, 3)
        sinusoidalLayout.addWidget(self.sinusoidalPlot, 7)

        # Summition Layout
        summitionLayout = QHBoxLayout()

        summitionGroupBox = QGroupBox("Synthetic Signal Panel")
        summitionSinusoidal = QVBoxLayout()
        summitionGroupBox.setLayout(summitionSinusoidal)

        # Table of signals
        self.signalsTable = TableView()

        # List of signale layout
        listLayout = QHBoxLayout()

        # Signals List
        self.signalsList = QComboBox()
        self.signalsList.setStyleSheet(f"""font-size:14px;
                                    height: 25px;
                                    padding: 0px 5px;
                                    background: {COLOR4};
                                    color:{COLOR1};""")
        self.signalsList.addItem("Choose...")

        # Delete of signal button
        self.deleteButton = QPushButton()
        self.deleteButton.setIcon(QIcon("images/clear.svg"))
        self.deleteButton.setStyleSheet(f"""background: {COLOR3};
                                border-radius: 6px;
                                border: 1px solid {COLOR6};
                                padding: 5px 15px;""")

        listLayout.addWidget(self.signalsList, 4)
        listLayout.addWidget(self.deleteButton, 1)

        self.saveExampleButton = QPushButton("Append Example")
        self.saveExampleButton.setStyleSheet(f"""background: {COLOR2};
                                border-radius: 6px;
                                border: 1px solid {COLOR1};
                                padding: 5px 15px;
                                color:{COLOR6}""")

        saveAndConfLayout = QHBoxLayout()
        saveAndConfLayout.addWidget(self.saveExampleButton)

        self.moveSamplingButton = QPushButton("Move to Main Illustrator")
        self.moveSamplingButton.setStyleSheet(f"""background: {COLOR2};
                                border-radius: 6px;
                                border: 1px solid {COLOR1};
                                padding: 5px 15px;
                                color:{COLOR6}""")

        summitionSinusoidal.addWidget(self.signalsTable)
        summitionSinusoidal.addLayout(listLayout)
        summitionSinusoidal.addLayout(saveAndConfLayout)
        summitionSinusoidal.addWidget(self.moveSamplingButton)

        # Summition Plot
        self.summitionPlot = Plot()

        summitionLayout.addWidget(summitionGroupBox, 3)
        summitionLayout.addWidget(self.summitionPlot, 7)

        exampleGroupBox = QGroupBox("Saved Examples")
        exampleLayout = QHBoxLayout()
        exampleGroupBox.setLayout(exampleLayout)

        self.examplesList = QComboBox()
        self.examplesList.setStyleSheet(f"""font-size:14px;
                                    height: 25px;
                                    padding: 0px 5px;
                                    background: {COLOR4};
                                    color:{COLOR1};""")
        self.examplesList.addItem("Choose...")
        # Read Data of examples
        self.bigExamplesList = self.readExamples()

        self.export = QPushButton("Save as")
        self.export.setStyleSheet(f"""background: {COLOR2};
                                border-radius: 6px;
                                border: 1px solid {COLOR1};
                                padding: 5px 15px;
                                color:{COLOR6}""")

        self.deleteEx = QPushButton("")
        self.deleteEx.setIcon(QIcon("images/clear.svg"))
        self.deleteEx.setStyleSheet(f"""background: {COLOR3};
                                border-radius: 6px;
                                border: 1px solid {COLOR1};
                                padding: 5px 15px;""")

        exampleLayout.addWidget(self.examplesList, 10)
        exampleLayout.addWidget(self.export, 4)
        exampleLayout.addWidget(self.deleteEx, 1)

        composerLayout.addLayout(sinusoidalLayout)
        composerLayout.addLayout(summitionLayout)
        composerLayout.addWidget(exampleGroupBox)

        self.composerTab.setLayout(composerLayout)

        freq = float(self.freqBox.text())
        magnitude = float(self.magnitudeBox.text())
        phase = float(self.phaseBox.text())

        signal, t = self.getContinuosSignal(freq, magnitude, phase)
        self.sinusoidalPlot.plotSignal(t, signal)

    # Browse signal

    def browseSignal(self):
        path, fileExtension = QFileDialog.getOpenFileName(
            None, "Load Signal File", os.getenv('HOME'), "csv(*.csv)")
        if path == "":
            return

        if fileExtension == "csv(*.csv)":
            self.mainDataPlot = pd.read_csv(path).iloc[:, 1].values.tolist()
            self.timePlot = pd.read_csv(path).iloc[:, 0].values.tolist()
        else:
            QMessageBox.critical(self, "Error", "You must open csv file.")
            return

        self.maxFreq = self.getFmax()  # Get Frequency Maximum

        self.mainPlot.clearSignal()
        self.mainPlot.set_data(self.mainDataPlot, self.timePlot)
        self.mainPlot.plotSignal()

    def getFmax(self):
        # gets array of fft magnitudes
        fft_magnitudes = np.abs(np.fft.fft(self.mainDataPlot))
        # gets array of frequencies
        fft_frequencies = np.fft.fftfreq(
            len(self.timePlot), self.timePlot[2]-self.timePlot[1])
        # create new "clean array" of frequencies
        fft_clean_frequencies_array = []
        for index in range(len(fft_frequencies)):
            # checks if signigifcant frequency is present
            if fft_magnitudes[index] > np.average(fft_magnitudes):
                fft_clean_frequencies_array.append(fft_frequencies[index])

        maxFreq = floor(max(fft_clean_frequencies_array))

        return maxFreq

    def reconstructSample(self):
        self.reconstractionPlot.resampleSignalLine()

    def plotDifference(self):
        diffY = self.mainPlot.y - self.reconstractionPlot.resampledSignal

        self.differencePlot.set_data(diffY, self.reconstractionPlot.x)
        self.differencePlot.plotSignal()

    # Plot Composer Signal

    def plotSinusoidalSignal(self):
        freq = float(self.freqBox.text())
        magnitude = float(self.magnitudeBox.text())
        phase = float(self.phaseBox.text())

        signal, t = self.getContinuosSignal(freq, magnitude, phase)

        self.sinusoidalPlot.plotSignal(t, signal)
        self.signalsTable.addData(freq, magnitude, phase)
        self.signalsList.addItem("Signal " + str(self.signalsTable.rowCount()))

        self.signalSummitionPlot()

    # Signal Summution
    def signalSummitionPlot(self):
        self.signalSummition = np.zeros(1000)
        t = np.array([])
        i = 0
        while i < self.signalsTable.rowCount():
            frequency = self.signalsTable.item(i, 0).data(0)[:-2]
            magnitude = self.signalsTable.item(i, 1).data(0)
            phase = self.signalsTable.item(i, 2).data(0)[:-1]

            y, t = self.getContinuosSignal(frequency, magnitude, phase)
            i += 1

            self.signalSummition = np.add(self.signalSummition, y)

        self.summitionPlot.clearPlot()
        self.summitionPlot.plotSignal(t, self.signalSummition)

    # Delete signal from the list
    def deleteSignal(self):
        if self.signalsList.currentText() != "Choose...":
            currentIndex = int(self.signalsList.currentIndex()) - 1

            self.signalsTable.removeRow(
                int(self.signalsList.currentText()[7])-1)
            self.signalsList.removeItem(self.signalsList.currentIndex())

            while currentIndex < self.signalsList.count():
                currentIndex += 1
                self.signalsList.setItemText(
                    currentIndex, "Signal " + str(currentIndex))

        self.signalSummitionPlot()

    # Choose one signal from plot and plot it.
    def plotSingleSignal(self):
        if self.signalsList.currentText() != "Choose...":
            currentIndex = int(self.signalsList.currentIndex()) - 1

            frequency = self.signalsTable.item(currentIndex, 0).data(0)[:-2]
            magnitude = self.signalsTable.item(currentIndex, 1).data(0)
            phase = self.signalsTable.item(currentIndex, 2).data(0)[:-1]

            signal, t = self.getContinuosSignal(frequency, magnitude, phase)

            self.summitionPlot.clearPlot()
            self.summitionPlot.plotSignal(t, signal)

        else:
            self.signalSummitionPlot()

    # Return continuos signal given frequency, magnitude and phase: A cos(2*pi*freq*t + phase)

    def getContinuosSignal(self, frequency, magnitude, phase):
        t = np.linspace(TMIN, TMAX, 1000)
        y = float(magnitude) * np.sin(2 * np.pi *
                                      float(frequency) * t + float(phase))

        return (y, t)

    # Move signal in summer plot to the main plot.
    def moveToSamplePlot(self):
        self.reconstractionPlot.clearSignal()
        self.differencePlot.clearSignal()
        self.tabs.setCurrentIndex(0)
        freqList = list()
        i = 0
        # Get Fmax
        while i < self.signalsTable.rowCount():
            frequency = self.signalsTable.item(i, 0).data(0)[:-2]
            freqList.append(float(frequency))
            i += 1
        self.maxFreq = max(freqList)
        self.mainPlot.clearSignal()
        self.mainPlot.set_data(self.signalSummition,
                               np.linspace(TMIN, TMAX, 1000))
        self.mainPlot.plotSignal()

    def connect(self):
        self.sliderMainPlot.valueChanged[int].connect(self.freqChange)
        self.noiseSlider.valueChanged[int].connect(self.snrChange)

        self.deleteButton.clicked.connect(self.deleteSignal)
        self.signalsList.currentTextChanged.connect(self.plotSingleSignal)
        self.saveExampleButton.clicked.connect(self.AddExample)
        self.moveSamplingButton.clicked.connect(self.moveToSamplePlot)

        self.plotButton.clicked.connect(self.plotSinusoidalSignal)

        self.examplesList.currentTextChanged.connect(self.loadExample)
        self.export.clicked.connect(self.exportExample)
        self.deleteEx.clicked.connect(self.deleteExample)

    # Examples Functions

    # Delete saved example
    def deleteExample(self):
        currentIndex = int(self.examplesList.currentIndex()) - 1

        self.bigExamplesList.pop(int(self.examplesList.currentText()[-1])-1)
        self.examplesList.removeItem(self.examplesList.currentIndex())

        while currentIndex < self.examplesList.count():
            currentIndex += 1
            self.examplesList.setItemText(
                currentIndex, "Example " + str(currentIndex))

        df = pd.DataFrame(self.bigExamplesList)
        df.to_csv('ExamplesList.csv')

    # Save As example
    def exportExample(self):
        exampleIndex = int(self.examplesList.currentText()
                           [-1]) - 1  # compoBox Begin from 1
        exampleInfo = self.bigExamplesList[exampleIndex]

        t = np.linspace(TMIN, TMAX, 1000)
        signal = 0 * t

        for signalInfo in exampleInfo:
            freq = signalInfo[0]
            magnitude = signalInfo[1]
            phase = signalInfo[2]

            partSignal, _ = self.getContinuosSignal(freq, magnitude, phase)
            signal += partSignal

        dict = {'time': t, 'magnitude': signal}
        df = pd.DataFrame(dict)
        output_file, _ = QFileDialog.getSaveFileName(
            self, 'Save as File', None, 'CSV files (.csv);')
        if output_file != '':
            if QFileInfo(output_file).suffix() == "":
                output_file += '.csv'

        df.to_csv(output_file, index=False)

    # Transfer list to string
    def stringToList(self, stringList):
        List = ast.literal_eval(stringList)
        try:
            List = [n.strip() for n in List]
        except:
            pass
        List = [float(n) for n in List]

        return List

    # Read Examples from csv file
    def readExamples(self):
        listExamples = list()
        df = pd.read_csv("ExamplesList.csv")
        for i in range(df.shape[0]):
            listExample = list()
            for j in range(1, df.shape[1]):
                signalData = (df.iloc[i, j])
                if not pd.isna(signalData):
                    signalData = self.stringToList(signalData)
                    listExample.append(signalData)
            listExamples.append(listExample)

        for _ in listExamples:
            self.examplesList.addItem(
                "Example " + str(self.examplesList.count()))

        return listExamples

    # Preview loaded example

    def loadExample(self):
        if self.examplesList.currentText() != "Choose...":
            exampleIndex = int(self.examplesList.currentText()
                               [-1]) - 1  # compoBox Begin from 1
            exampleInfo = self.bigExamplesList[exampleIndex]

            self.signalsTable.clearAllData()
            self.signalsList.clear()

            self.signalsList.addItem("Choose...")
            self.previewExample(exampleInfo)

    def AddExample(self):
        signalSum = []
        i = 0
        while i < self.signalsTable.rowCount():
            frequency = self.signalsTable.item(i, 0).data(0)[:-2]
            magnitude = self.signalsTable.item(i, 1).data(0)
            phase = self.signalsTable.item(i, 2).data(0)[:-1]

            signalInfo = [frequency, magnitude, phase]
            signalSum.append(signalInfo)
            i += 1

        self.bigExamplesList.append(signalSum)
        self.examplesList.addItem("Example " + str(self.examplesList.count()))

        df = pd.DataFrame(self.bigExamplesList)

        try:
            df.to_csv('ExamplesList.csv')
        except:
            QMessageBox.critical(
                self, "Error", "There is a problem, be sure that the examples.csv is closed.")

    def previewExample(self, exampleInfo):
        for signalInfo in exampleInfo:
            freq = signalInfo[0]
            magnitude = signalInfo[1]
            phase = signalInfo[2]

            self.signalsTable.addData(freq, magnitude, phase)
            self.signalsList.addItem(
                "Signal " + str(self.signalsTable.rowCount()))

            self.signalSummitionPlot()

    def exit(self):
        exitDlg = QMessageBox.critical(self,
                                       "Exit the application",
                                       "Are you sure you want to exit the application?",
                                       buttons=QMessageBox.Yes | QMessageBox.No,
                                       defaultButton=QMessageBox.No)

        if exitDlg == QMessageBox.Yes:
            sys.exit()
