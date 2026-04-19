@echo off
echo =================================
echo Cai dat thu vien...
echo =================================
call .venv\Scripts\activate
pip install -r requirements.txt

echo.
echo =================================
echo Dang nap du lieu...
echo =================================
python create_db.py

echo.
echo =================================
echo Chay server...
echo =================================
python -m movieapp.index

pause