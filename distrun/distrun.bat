@Echo off

set "BOT1=192.168.178.50"
set "BOT2=192.168.178.50"
set "BOT3=192.168.178.50"

set "SRC=%CD%\%1"
set "DST=%2"
set "CMD=%3"

START CMD /C type %SRC% | ssh %BOT1% "cat > "%DST% "; "%CMD%
START CMD /C type %SRC% | ssh %BOT2% "cat > "%DST% "; "%CMD%
START CMD /C type %SRC% | ssh %BOT3% "cat > "%DST% "; "%CMD%
