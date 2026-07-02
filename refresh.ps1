# AIA manual refresh
Set-Location "C:\Users\rmalk\projects\razel369-aia"
python -X utf8 -m agent.loop | Tee-Object -FilePath "logs\manual.log.txt"
