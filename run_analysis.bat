@echo off
echo Starting analysis...
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" -c "import pandas as pd; print('Pandas version:', pd.__version__)" > output.log 2>&1
echo Check output.log for results
pause
