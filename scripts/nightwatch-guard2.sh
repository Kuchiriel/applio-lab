#!/usr/bin/env bash
# Guarda da madrugada v2: se a fila Kaggle ainda estiver viva as 02:50,
# para o timer do nightwatch desta noite. Se ja terminou, nao mexe em nada.
Q=3974824
LOG=/tmp/opencode/nightwatch-guard.log
while [ "$(date +%H%M)" -lt 0250 ]; do sleep 60; done
if kill -0 $Q 2>/dev/null; then
  sudo systemctl stop nightwatch.timer 2>>$LOG \
    && echo "$(date) fila kaggle viva, nightwatch.timer PARADO esta noite" >>$LOG \
    || echo "$(date) fila viva, FALHA ao parar timer (sudo?)" >>$LOG
else
  echo "$(date) fila ja terminou, nightwatch mantido" >>$LOG
fi
