@echo off
echo Running Python script...
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" simple_csv_reader.py > output.txt 2>&1
type output.txt
del output.txt
pause
