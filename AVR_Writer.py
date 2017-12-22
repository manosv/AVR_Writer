#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  AVR_Writer.py
#  
#  Copyright 2017 Michael <michael@UMO>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


import sys
import os
from PyQt4.QtCore import * 
from PyQt4.QtGui import *

class Window(QWidget):
	def __init__(self,parent = None): 
		super(Window, self).__init__(parent) 
		
		
		#Some Variables
		self.fileName = "/home/"
		self.chipName = ""
		self.programmer = "avrispmkII"
		#get Chip list
		self.chipList = {}
		
		#Quit Button
		self.btn = QPushButton("Quit", self)
		self.btn.clicked.connect(self.closeApp)
		self.btn.resize(self.btn.minimumSizeHint())
		self.btn.move(10,300)
		
		#Write Button
		self.write = QPushButton("write", self)
		self.write.clicked.connect(self.WriteCommand)
		self.write.resize(self.write.minimumSizeHint())
		self.write.move(110, 300)
		
		
		#Select File Button
		self.sf = QPushButton("Select File", self)
		self.sf.clicked.connect(self.selectFile)
		self.sf.resize(self.sf.minimumSizeHint())
		self.sf.move(210, 300)
		
		#MCU list
		self.mcu = QComboBox(self)
		self.mcu.resize(200, 30)
		self.mcu.move(100, 10)
		
		#Programmers List
		self.prog = QComboBox(self)
		self.prog.resize(200, 30)
		self.prog.move(100, 30)
		
		#layout
		self.layout = QFormLayout(self)
		
		#text box
		self.txt = QTextEdit()
		self.txt.setMaximumHeight(200)
		self.txt.setMaximumWidth(400)
		self.txt.move(0, 100)
		self.txt.setReadOnly(1)
		
		#some labels
		self.layout.addRow("MCU:", self.mcu)
		self.layout.addRow("Programmer:", self.prog)
		self.layout.addRow("Dialog:", self.txt)

		self.layout.addWidget(self.txt)
		self.setLayout(self.layout)
		self.setGeometry(200, 200, 310, 340)
		self.setFixedSize(self.size());
		self.setWindowTitle("AVR_Writer")
		self.setWindowIcon(QIcon('avrbug.png'))
		self.home()

	def chip(self, code, num):
		n = 0
		while not code[n:n+1] == " ":
			n = n+1
		if num == 0:
			return code[0:n]
		else :
			n = n+1
			c = n
			while not code[c:c+1] == "\n":
				c = c+1
			return code[n:c]
				

	def programmer(self, code):
		c = 0
		while not code[c:c+1] == "\n":
			c = c+1
		return code[0:c]
			
	def home(self):
		
		o = open("SourtedPartList.txt", "r")
		line = o.readline()
		while line:
			self.chipList[self.chip(line, 1)] = self.chip(line, 0)
			self.mcu.addItem(self.chip(line, 1))
			line = o.readline()
		o.close()
		
		o = open("SourtedProgrammerList.txt", "r")
		line = o.readline()
		while line:
			self.prog.addItem(line[0:len(line)-1])
			line = o.readline()
		o.close()
		
	def closeApp(self):
		#print("closing...")
		sys.exit()
	
	def selectFile(self):
		self.debug("Selecting File...", 0)
		fn = QFileDialog.getOpenFileName(self, 'Open File',
		self.fileName, 'Code Files (*.c *.asm)')
		if fn:
			self.fileName = fn
			self.debug("File Name: "+str(self.detectFileName(self.fileName)), 3)
		else :
			self.debug("File not selected", 1)
 
	def fileSelected(self):
		if self.detectFileFormat():
			return 1
		else:
			self.debug("File not .c or .asm", 1)
			return 0

	def chipSelected(self):
		self.chipName = str(self.mcu.currentText())
		if not self.chipName == "None":
			return 1
		else:
			self.debug("MCU not selected", 1)
			return 0

	def programmerSelected(self):
		self.programmer = str(self.prog.currentText())
		if not self.programmer == "None":
			return 1
		else:
			self.debug("Programmer not selected", 1)
			return 0

	def detectFileFormat(self):
		if self.fileName[len(self.fileName)-1:len(self.fileName)] == 'c':
			return "c"
		elif self.fileName[len(self.fileName)-3:len(self.fileName)] == 'asm':
			return "asm"
		else :
			return 0
		
	def WriteCommand(self):
		self.debug("writing command...", 0)
		if self.fileSelected() and self.chipSelected() and self.programmerSelected():
			fileFormat = self.detectFileFormat()
			if fileFormat == "asm":
				if self.asmRoutine():
					self.writeRoutine(0)
				else :
					self.error("assembly code")
			elif fileFormat == "c":
				if self.cRoutine():
					self.writeRoutine(1)
				else :
					self.error("C code")
		else :
			self.error("inputs")
	
	def asmRoutine(self):
		command = str("avra " + self.fileName)
		result = os.popen4(command)[1].read()
		self.debug(result, 0)
		if result == "":
			return 0
		else :
			return 1
	
	def cRoutine(self):
		command = str("avr-gcc -g -Os -mmcu="+self.chipName.lower()+" -c "+self.fileName)
		result = os.popen4(command)[1].read()
		self.debug(result, 0)
		if self.check(result):
			command = str("avr-gcc -g -mmcu="+self.chipName.lower()+" -o "+self.fileName[0:len(self.fileName)-2]+".elf "+self.fileName[0:len(self.fileName)-2]+".o")
			result = os.popen4(command)[1].read()
			self.debug(result, 0)
			if self.check(result):
				command = str("avr-objcopy -j .text -j .data -O ihex "+self.fileName[0:len(self.fileName)-2]+".elf "+self.fileName[0:len(self.fileName)-2]+".hex")
				result = os.popen4(command)[1].read()
				self.debug(result, 0)
				if self.check(result):
					return 1
				else :
					return 0
			else :
				return 0
		else :
			return 0
				
	def writeRoutine(self, num):
		if num:
			c = 2
		else :
			c = 4
		command = str("avrdude -p "+self.chipList[str(self.chipName)]+" -P usb -c "+self.programmer+" -e -U flash:w:"+self.fileName[0:len(self.fileName)-c]+".hex")
		result = os.popen4(command)[1].read()
		self.debug(result, 0)
		if self.check(result):
			return 1
		else :
			return 0

	def check(self, result):
		if not result == "":
			return 0
		else :
			return 1
	
	def debug(self, text, num):
		if num == 1:
			self.txt.setTextColor(QColor('red'))
		elif num == 3:
			self.txt.setTextColor(QColor('green'))
		else:
			self.txt.setTextColor(QColor('black'))
		self.txt.append(text)
		
	def error(self, message):
		self.debug("Please check the "+message, 1)
	
	def detectFileName(self, name):
		if name == None:
			return ""
		else :
			c = len(name)-1
			while not name[c-1:c] == "/":
				c = c-1
			return name[c:]
	
        
if __name__ == "__main__": 
    app = QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())
