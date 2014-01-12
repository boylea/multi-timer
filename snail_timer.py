import time
import csv
import itertools
import os

from PyQt4 import QtCore, QtGui

class SnailTimer(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.snail_status_label =[]
        self.snail_time = []
        self.start_times = []
        self.snail_time_list = []
        self.master_start = None
        self.master_duration = None
        self.saved = False

        hlayout = QtGui.QHBoxLayout()

        nsnails = 8
        for isnail in range(nsnails):
            snail_number = QtGui.QLabel(str(isnail+1))
            label = QtGui.QLabel("DOWN")
            snail_time = QtGui.QLabel("00:00.0")
            snail_layout = QtGui.QVBoxLayout()
            snail_layout.addWidget(snail_number)
            snail_layout.addWidget(label)
            snail_layout.addWidget(snail_time)

            self.snail_status_label.append(label)
            self.snail_time.append(snail_time)
            self.start_times.append(None)
            self.snail_time_list.append([])

            hlayout.addLayout(snail_layout)

        self.master_time = QtGui.QLabel("00:00.0")
        self.file_field = QtGui.QLineEdit()
        start_button = QtGui.QPushButton("Start")
        start_button.clicked.connect(self.start_timer)
        save_button = QtGui.QPushButton("Save")
        save_button.clicked.connect(self.save_csv)
        save_button.setEnabled(False)

        divider = QtGui.QFrame()
        divider.setFrameShape(QtGui.QFrame.HLine)
        divider.setFrameShadow(QtGui.QFrame.Sunken)

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.master_time)
        button_layout.addStretch(1)
        button_layout.addWidget(self.file_field)
        button_layout.addWidget(start_button)
        button_layout.addWidget(save_button)
        self.start_button = start_button
        self.save_button = save_button

        master_layout = QtGui.QVBoxLayout()
        master_layout.addLayout(hlayout)
        master_layout.addWidget(divider)
        master_layout.addLayout(button_layout)

        self.setLayout(master_layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_times)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def start_timer(self, event):
        """Starts and stops (toggles) the main timer"""
        if self.start_button.text() == 'Start' or self.start_button.text() == 'Re-start':
            if self.start_button.text() == 'Re-start':
                response = QtGui.QMessageBox.question(self, 'Save warning', 
                    "Re-starting will overwrite existing times, make sure you have saved. \
                    \n\nAre you sure you want to restart?", 
                    QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Yes)
                if response == QtGui.QMessageBox.Cancel:
                    return
                for isnail in range(len(self.start_times)):
                    self.snail_time_list[isnail] = []
                    self.start_times[isnail] = None

            self.master_start = time.time()
            self.start_str = time.strftime("%m-%d-%Y %H:%M")
            self.timer.start(100)
            self.start_button.setText("Stop")
            self.save_button.setEnabled(False)
            self.saved = False
        else:
            self.master_duration = time.time() - self.master_start
            self.timer.stop()
            # make sure all snail timers are stopped
            for snail_num, label in enumerate(self.snail_status_label):
                if label.text() == 'UP':
                    self.stop_snail(snail_num)

            self.start_button.setText("Re-start")
            self.save_button.setEnabled(True)

    def keyPressEvent(self, event):
        if self.start_button.text() == 'Stop':
            if QtCore.Qt.Key_1 <= event.key() <= QtCore.Qt.Key_8:
                # in order to translate to list index numbers
                snail_num = event.key() - 49
                if self.snail_status_label[snail_num].text() == "DOWN":
                    self.snail_status_label[snail_num].setText("UP")
                    self.start_times[snail_num] = time.time()
                else:
                    self.stop_snail(snail_num)

    def stop_snail(self, snail_num):
        now = time.time()
        elapsed = now - self.start_times[snail_num]
        # self.snail_time_list[snail_num].append(elapsed) # elapsed
        # start, stop
        self.snail_time_list[snail_num].append(round(self.start_times[snail_num] - self.master_start, 2))
        self.snail_time_list[snail_num].append(round(now - self.master_start, 2)) 
        self.snail_status_label[snail_num].setText("DOWN")
        self.start_times[snail_num] = None
        self.snail_time[snail_num].setText("00:00.0")

    def update_times(self):
        now = time.time()
        elapsed = now - self.master_start
        self.master_time.setText("{:02d}:{:04.1f}".format(int(elapsed)/60, elapsed % 60))
        for isnail, label in enumerate(self.snail_status_label):
            if label.text() == 'UP':
                elapsed = now - self.start_times[isnail]
                self.snail_time[isnail].setText("{:02d}:{:04.1f}".format(int(elapsed)/60, elapsed % 60))

    def browse(self):
        filename = self.file_field.text()
        if len(filename) > 0:
            save_dir = os.path.dirname(str(filename))
        else:
            save_dir = os.getcwd()

        filename = QtGui.QFileDialog.getSaveFileName(self, 'Open or Create File', 
                save_dir, 'Text files (*.csv *.txt);; All files (*)', '', 
                QtGui.QFileDialog.DontConfirmOverwrite)

        if len(filename) > 0:
            self.file_field.setText(filename)

        return filename

    def save_csv(self):
        if self.saved:
            response = QtGui.QMessageBox.question(self, 'Duplicate Warning', 
                    "You have already saved this data, saving again may append a duplicate record. \
                    \n\nAre you sure you want to save?", 
                    QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Yes)
            if response == QtGui.QMessageBox.Cancel:
                return

        filename = self.file_field.text()
        if filename == '':
            filename = self.browse()
            if filename == '':
                return

        with open(filename, 'ab') as f:
            writer = csv.writer(f)
            writer.writerow([self.start_str])
            writer.writerow(['Times']+ map(str, range(1,9)))
            # insert blank row to end up with empty spacer column in csv file
            self.snail_time_list.insert(0, [])
            transposed = [x for x in itertools.izip_longest(*self.snail_time_list)]
            writer.writerows(transposed)
            writer.writerow([])
            # remove spacer row
            self.snail_time_list.pop(0)

            totals = []
            means = []
            ntimes = []
            # round off times
            for snail_times in self.snail_time_list:
                # decimal storage is inexact, so round again.
                elapsed = [round(stop - start, 2) for start, stop in zip(snail_times[0::2], snail_times[1::2])]
                if len(elapsed) > 0:
                    total = round(sum(elapsed), 2)
                    mean = round(total/len(elapsed), 2)
                else:
                    total = 0
                    mean = 0
                totals.append(total)
                means.append(mean)
                ntimes.append(len(elapsed))
            writer.writerow(['Total'] + totals)
            writer.writerow(['Mean'] + means)
            writer.writerow(['No. openings'] + ntimes)
            writer.writerow(['Master duration'] + [round(self.master_duration,2)])
            # add empty rows so there is a break between next set when appended
            writer.writerows([[],[]]) 
        self.saved = True

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
        
    snail_timer = SnailTimer()

    snail_timer.resize(400, 200)
    snail_timer.show()

    sys.exit(app.exec_())