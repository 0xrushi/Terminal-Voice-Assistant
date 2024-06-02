@echo off
REM Activate the Conda environment
call activate base

REM Run the Python script with specified parameters
python main.py --keyword_paths ./wakewords/hey-nami_en_windows_v3_0_0.ppn --audio_device_index 3

REM
pause
