@echo off
echo Downloading nlohmann/json library...
powershell -Command "Invoke-WebRequest -Uri https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp -OutFile json.hpp"
echo Done!
pause 