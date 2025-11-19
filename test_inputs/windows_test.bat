@echo off

::emulate startup taking some time
timeout /t 1 >nul

::emulate using the work directory
if not exist ".hw-agent-id" (
   echo "some id" > .hw-agent-id
)

if not exist ".hw-cache" (
   mkdir .hw-cache
   echo "some cahce data" > .hw-cache/cacheFile1
)

::emulate sending messages
:loop
   echo "Simulate a process message"
   timeout /t 1 >nul
goto loop
