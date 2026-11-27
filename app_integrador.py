from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
import mysql.connector

app = Flask(__name__)


def conectar_banco():
  return mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db_robo",
  )


comando_atual = {
    "id": 0,
    "acao": "andar_cm",
    "velocidade": 30,
    "valor": 20.0,
}

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle LEGO EV3 + MySQL</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #f0f0f0; margin: 0; padding: 24px; display: flex; flex-direction: column; align-items: center; }
        .container { display: flex; flex-wrap: wrap; gap: 24px; max-width: 1020px; width: 100%; justify-content: center; }
        .card { background: #1e1e1e; padding: 24px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); width: 380px; }
        .card-historico { width: 560px; }
        h2, h3 { margin-top: 0; color: #4caf50; }
        label { display: block; margin-top: 14px; font-size: 14px; color: #bbb; }
        select, input { width: 100%; padding: 10px; margin-top: 5px; border-radius: 6px; border: 1px solid #333; background: #2c2c2c; color: #fff; box-sizing: border-box; font-size: 15px; }
        button { width: 100%; padding: 11px; margin-top: 18px; border: none; border-radius: 6px; background: #4caf50; color: white; font-size: 15px; font-weight: bold; cursor: pointer; }
        button:hover { background: #45a049; }
        button.secundario { background: #2196f3; margin-top: 10px; }
        button.secundario:hover { background: #1e88e5; }
        .status { margin-top: 12px; font-size: 13px; color: #aaa; min-height: 18px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
        th, td { border-bottom: 1px solid #333; padding: 8px 6px; text-align: left; }
        th { color: #4caf50; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>Controle LEGO EV3</h2>
            <label for="acao">Ação do Robô:</label>
            <select id="acao">
                <option value="andar_cm">Andar para Frente (cm)</option>
                <option value="girar_seg">Girar no Eixo (segundos)</option>
                <option value="cacamba">Mover Caçamba (graus)</option>
            </select>

            <label for="velocidade">Velocidade (10 a 100):</label>
            <input type="number" id="velocidade" value="20" min="10" max="100">

            <label for="valor">Valor (cm, seg ou graus):</label>
            <input type="number" id="valor" value="10" step="0.5">

            <button onclick="enviarComando()">Enviar para o EV3</button>
            <div class="status" id="status">Pronto para enviar comandos.</div>
        </div>

        <div class="card card-historico">
            <h3>Histórico no MySQL (viagens)</h3>
            <button class="secundario" onclick="carregarHistorico()">Atualizar Histórico</button>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Data/Hora</th>
                        <th>Ação</th>
                        <th>Valor</th>
                        <th>Vel.</th>
                    </tr>
                </thead>
                <tbody id="historico-body">
                    <tr><td colspan="5">Carregando...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function enviarComando() {
            const payload = {
                acao: document.getElementById('acao').value,
                velocidade: Number(document.getElementById('velocidade').value),
                valor: Number(document.getElementById('valor').value)
            };
            const statusEl = document.getElementById('status');
            statusEl.style.color = "#ffeb3b";
            statusEl.innerText = "Enviando comando...";

            try {
                const res = await fetch('/api/comando', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                statusEl.style.color = "#4caf50";
                statusEl.innerText = `Comando #${data.id} enviado! Aguarde execução do EV3.`;
                setTimeout(carregarHistorico, 2500);
            } catch (err) {
                statusEl.style.color = "#f44336";
                statusEl.innerText = "Falha ao enviar comando.";
            }
        }

        async function carregarHistorico() {
            const tbody = document.getElementById('historico-body');
            try {
                const res = await fetch('/api/viagens');
                const linhas = await res.json();
                if (!Array.isArray(linhas) || linhas.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5">Nenhum registo encontrado.</td></tr>';
                    return;
                }
                tbody.innerHTML = linhas.slice(-8).reverse().map(item => `
                    <tr>
                        <td>${item.id}</td>
                        <td>${item.data_hora}</td>
                        <td>${item.acao ?? '-'}</td>
                        <td>${item.valor ?? item.distancia_cm}</td>
                        <td>${item.velocidade ?? '-'}</td>
                    </tr>
                `).join('');
            } catch (err) {
                tbody.innerHTML = '<tr><td colspan="5">Erro ao consultar API.</td></tr>';
            }
        }

        carregarHistorico();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
  return render_template_string(HTML_INTERFACE)


@app.route("/api/comando", methods=["POST"])
def definir_comando():
  global comando_atual
  dados = request.get_json() or {}
  comando_atual = {
      "id": comando_atual["id"] + 1,
      "acao": dados.get("acao", "andar_cm"),
      "velocidade": dados.get("velocidade", 30),
      "valor": dados.get("valor", 0),
  }
  return jsonify(comando_atual), 200


@app.route("/api/comando", methods=["GET"])
def ler_comando():
  return jsonify(comando_atual), 200


@app.route("/api/viagens", methods=["GET"])
def listar_viagens():
  try:
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM viagens")
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(resultados), 200
  except Exception as e:
    return jsonify({"erro": str(e)}), 500


@app.route("/api/viagens", methods=["POST"])
def receber_viagem():
  dados = request.get_json() or {}
  data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  acao = dados.get("acao", "andar_cm")
  valor = dados.get("valor", dados.get("distancia_cm", 0))
  velocidade = dados.get("velocidade", 0)
  distancia_cm = dados.get("distancia_cm", valor)

  if valor is None and distancia_cm is None:
    return jsonify({"erro": "Dados incompletos"}), 400

  try:
    conexao = conectar_banco()
    cursor = conexao.cursor()
    sql = """
            INSERT INTO viagens (data_hora, distancia_cm, velocidade, acao, valor)
            VALUES (%s, %s, %s, %s, %s)
        """
    cursor.execute(
        sql,
        (
            data_hora,
            float(distancia_cm),
            int(velocidade),
            str(acao),
            float(valor),
        ),
    )
    conexao.commit()
    cursor.close()
    conexao.close()
    return jsonify({"mensagem": "Viagem salva com sucesso no MySQL!"}), 201
  except Exception as e:
    return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)