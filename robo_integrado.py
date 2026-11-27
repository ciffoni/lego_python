#!/usr/bin/env python3
import json
from time import sleep
import urllib.request
from ev3dev2.motor import (
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_C,
    LargeMotor,
    MediumMotor,
    MoveTank,
)
from ev3dev2.sound import Sound

ev3 = Sound()
tank_drive = MoveTank(OUTPUT_B, OUTPUT_C)
motor_cacamba = MediumMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_B)
right_motor = LargeMotor(OUTPUT_C)

BASE_URL = "http://169.254.22.179:5000"
URL_COMANDO = BASE_URL + "/api/comando"
URL_VIAGENS = BASE_URL + "/api/viagens"


def registrar_no_banco(acao, valor, velocidade, distancia_cm):
  payload = {
      "acao": str(acao),
      "valor": round(float(valor), 2),
      "velocidade": int(velocidade),
      "distancia_cm": round(float(distancia_cm), 2),
  }
  try:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL_VIAGENS, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
      print("MySQL resposta:", resp.getcode(), resp.read().decode("utf-8"))
  except Exception as e:
    print("Erro ao gravar no MySQL:", str(e))


ultimo_id = 0
ev3.beep()
print("EV3 conectado ao painel e pronto para receber comandos...")

while True:
  try:
    with urllib.request.urlopen(URL_COMANDO, timeout=2) as resp:
      cmd = json.loads(resp.read().decode("utf-8"))

    if cmd["id"] > ultimo_id:
      ultimo_id = cmd["id"]
      acao = cmd["acao"]
      vel = int(cmd["velocidade"])
      val = float(cmd["valor"])

      print(
          "Executando comando #" + str(ultimo_id) + ":",
          acao,
          val,
          "| Vel:",
          vel,
      )
      ev3.beep()

      distancia_registrada = 0.0

      if acao == "andar_cm":
        left_motor.reset()
        right_motor.reset()
        rotacoes = val / 17.5
        tank_drive.on_for_rotations(
            left_speed=-vel, right_speed=-vel, rotations=rotacoes
        )
        graus = (abs(left_motor.position) + abs(right_motor.position)) / 2.0
        distancia_registrada = (graus / 360.0) * 17.5

      elif acao == "girar_seg":
        tank_drive.on_for_seconds(
            left_speed=-vel, right_speed=vel, seconds=val
        )
        distancia_registrada = val

      elif acao == "cacamba":
        motor_cacamba.on_for_degrees(speed=vel, degrees=abs(val))
        sleep(1)
        motor_cacamba.on_for_degrees(speed=vel, degrees=-abs(val))
        distancia_registrada = abs(val)

      registrar_no_banco(acao, val, vel, distancia_registrada)

  except Exception as e:
    print("Aguardando conexao:", str(e))

  sleep(0.5)