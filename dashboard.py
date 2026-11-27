from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
import mysql.connector

app = Flask(__name__)

# Limite de distância (em cm) para disparar o alerta de manutenção
LIMITE_MANUTENCAO_CM = 500.0


def conectar_banco():
  return mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db_robo",
  )


HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard LEGO EV3 — Telemetria e Manutenção</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f1115;
            color: #f1f5f9;
            margin: 0;
            padding: 24px;
        }
        .wrapper {
            max-width: 1240px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 22px;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            color: #4ade80;
        }
        .header p {
            margin: 4px 0 0;
            color: #94a3b8;
            font-size: 13px;
        }
        .filtros {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        select, input[type="date"], button {
            background: #1e242d;
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
        }
        button {
            background: #22c55e;
            color: #07130b;
            border: none;
            font-weight: 700;
            cursor: pointer;
        }
        button:hover { background: #16a34a; color: #fff; }
        button.btn-sec {
            background: #2563eb;
            color: #fff;
        }
        button.btn-sec:hover { background: #1d4ed8; }

        .kpis {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .card {
            background: #171b22;
            border: 1px solid #262d3a;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }
        .kpi-titulo {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        .kpi-valor {
            font-size: 26px;
            font-weight: 700;
            color: #38bdf8;
        }
        .kpi-sub {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 6px;
        }
        .badge-ok {
            display: inline-block;
            margin-top: 8px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: rgba(34, 197, 94, 0.16);
            color: #4ade80;
            border: 1px solid #22c55e;
        }
        .badge-alerta {
            display: inline-block;
            margin-top: 8px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid #f59e0b;
        }

        .graficos {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 18px;
            margin-bottom: 20px;
        }
        .card h3 {
            margin: 0 0 12px;
            font-size: 16px;
            color: #e2e8f0;
        }
        .tabela-topo {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            padding: 10px 8px;
            border-bottom: 1px solid #262d3a;
            text-align: left;
        }
        th {
            color: #4ade80;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <div>
                <h1>Dashboard LEGO EV3</h1>
                <p>Monitoramento de viagens, distância diária e alerta de manutenção (MySQL: db_robo)</p>
            </div>
            <div class="filtros">
                <select id="filtro-acao">
                    <option value="">Todas as ações</option>
                    <option value="andar_cm">andar_cm</option>
                    <option value="girar_seg">girar_seg</option>
                    <option value="cacamba">cacamba</option>
                </select>
                <input type="date" id="filtro-data">
                <button onclick="carregarDashboard()">Aplicar</button>
                <button class="btn-sec" onclick="limparFiltros()">Limpar</button>
            </div>
        </div>

        <div class="kpis">
            <div class="card">
                <div class="kpi-titulo">Distância Andada Hoje</div>
                <div class="kpi-valor" id="kpi-hoje">0.00 cm</div>
                <div class="kpi-sub" id="kpi-hoje-m">0.00 m percorridos hoje</div>
            </div>

            <div class="card">
                <div class="kpi-titulo">Distância Total Acumulada</div>
                <div class="kpi-valor" id="kpi-total">0.00 cm</div>
                <div class="kpi-sub" id="kpi-total-m">0.00 m no histórico</div>
            </div>

            <div class="card">
                <div class="kpi-titulo">Velocidade Média / Registros</div>
                <div class="kpi-valor" id="kpi-vel">0.0</div>
                <div class="kpi-sub" id="kpi-qtd">0 comandos registrados</div>
            </div>

            <div class="card">
                <div class="kpi-titulo">Manutenção do Veículo</div>
                <div class="kpi-valor" id="kpi-limite">500 cm</div>
                <div id="kpi-manutencao-badge" class="badge-ok">OK — Sem necessidade</div>
                <div class="kpi-sub" id="kpi-manutencao-detalhe">Aguardando dados...</div>
            </div>
        </div>

        <div class="graficos">
            <div class="card">
                <h3>Distância por Dia (andar_cm)</h3>
                <canvas id="chartDistanciaDia" height="160"></canvas>
            </div>
            <div class="card">
                <h3>Execuções por Tipo de Ação</h3>
                <canvas id="chartAcoes" height="160"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="tabela-topo">
                <h3>Registros Recentes (viagens)</h3>
                <span style="font-size: 12px; color: #94a3b8;" id="info-atualizacao"></span>
            </div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Data/Hora</th>
                            <th>Ação</th>
                            <th>Valor</th>
                            <th>Velocidade</th>
                            <th>Distância (cm)</th>
                        </tr>
                    </thead>
                    <tbody id="corpo-tabela">
                        <tr><td colspan="6">Carregando dados...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let chartDistanciaDia = null;
        let chartAcoes = null;

        function limparFiltros() {
            document.getElementById('filtro-acao').value = '';
            document.getElementById('filtro-data').value = '';
            carregarDashboard();
        }

        function renderGraficos(porDia, porAcao) {
            const ctxDia = document.getElementById('chartDistanciaDia').getContext('2d');
            const ctxAcao = document.getElementById('chartAcoes').getContext('2d');

            if (chartDistanciaDia) chartDistanciaDia.destroy();
            if (chartAcoes) chartAcoes.destroy();

            chartDistanciaDia = new Chart(ctxDia, {
                type: 'bar',
                data: {
                    labels: porDia.map(d => d.dia),
                    datasets: [{
                        label: 'Distância (cm)',
                        data: porDia.map(d => Number(d.total_cm)),
                        backgroundColor: '#38bdf8',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } }
                    }
                }
            });

            chartAcoes = new Chart(ctxAcao, {
                type: 'doughnut',
                data: {
                    labels: porAcao.map(a => a.acao),
                    datasets: [{
                        data: porAcao.map(a => Number(a.quantidade)),
                        backgroundColor: ['#4ade80', '#f59e0b', '#a78bfa'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } }
                }
            });
        }

        async function carregarDashboard() {
            const acao = document.getElementById('filtro-acao').value;
            const data = document.getElementById('filtro-data').value;
            const params = new URLSearchParams();
            if (acao) params.append('acao', acao);
            if (data) params.append('data', data);

            try {
                const res = await fetch('/api/dashboard?' + params.toString());
                const dados = await res.json();
                if (dados.erro) {
                    document.getElementById('corpo-tabela').innerHTML =
                        `<tr><td colspan="6">Erro: ${dados.erro}</td></tr>`;
                    return;
                }

                const kpis = dados.kpis;
                document.getElementById('kpi-hoje').innerText = `${Number(kpis.distancia_hoje_cm).toFixed(2)} cm`;
                document.getElementById('kpi-hoje-m').innerText = `${(Number(kpis.distancia_hoje_cm) / 100).toFixed(2)} m percorridos hoje`;

                document.getElementById('kpi-total').innerText = `${Number(kpis.distancia_total_cm).toFixed(2)} cm`;
                document.getElementById('kpi-total-m').innerText = `${(Number(kpis.distancia_total_cm) / 100).toFixed(2)} m no histórico`;

                document.getElementById('kpi-vel').innerText = `${Number(kpis.velocidade_media).toFixed(1)}`;
                document.getElementById('kpi-qtd').innerText = `${kpis.total_registros} comandos no filtro`;

                document.getElementById('kpi-limite').innerText = `${Number(kpis.limite_manutencao_cm).toFixed(0)} cm`;
                const badge = document.getElementById('kpi-manutencao-badge');
                const detalhe = document.getElementById('kpi-manutencao-detalhe');

                if (kpis.manutencao_necessaria) {
                    badge.className = 'badge-alerta';
                    badge.innerText = '⚠️ MANUTENÇÃO DO VEÍCULO';
                    detalhe.innerText = `Limite atingido (${Number(kpis.distancia_hoje_cm).toFixed(1)} cm hoje).`;
                } else {
                    badge.className = 'badge-ok';
                    badge.innerText = '✅ OPERAÇÃO NORMAL';
                    const restante = Math.max(0, Number(kpis.limite_manutencao_cm) - Number(kpis.distancia_hoje_cm));
                    detalhe.innerText = `Restam ${restante.toFixed(1)} cm hoje para o aviso.`;
                }

                renderGraficos(dados.por_dia || [], dados.por_acao || []);

                const tbody = document.getElementById('corpo-tabela');
                const viagens = dados.viagens || [];
                if (viagens.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6">Nenhum registro encontrado para o filtro.</td></tr>';
                } else {
                    tbody.innerHTML = viagens.map(v => `
                        <tr>
                            <td>${v.id}</td>
                            <td>${v.data_hora}</td>
                            <td>${v.acao ?? '-'}</td>
                            <td>${v.valor ?? '-'}</td>
                            <td>${v.velocidade ?? '-'}</td>
                            <td>${Number(v.distancia_cm || 0).toFixed(2)}</td>
                        </tr>
                    `).join('');
                }

                document.getElementById('info-atualizacao').innerText =
                    `Atualizado às ${new Date().toLocaleTimeString('pt-BR')}`;
            } catch (err) {
                document.getElementById('corpo-tabela').innerHTML =
                    `<tr><td colspan="6">Falha ao carregar dashboard: ${err.message}</td></tr>`;
            }
        }

        carregarDashboard();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
  return render_template_string(HTML_DASHBOARD)


@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
  acao = request.args.get("acao", "").strip()
  data_filtro = request.args.get("data", "").strip()
  hoje = datetime.now().strftime("%Y-%m-%d")

  where_clauses = []
  params = []
  if acao:
    where_clauses.append("acao = %s")
    params.append(acao)
  if data_filtro:
    where_clauses.append("DATE(data_hora) = %s")
    params.append(data_filtro)

  where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

  try:
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    # 1. Distância andada hoje (apenas andar_cm)
    cursor.execute(
        """
            SELECT COALESCE(SUM(distancia_cm), 0) AS dist_hoje
            FROM viagens
            WHERE DATE(data_hora) = %s AND acao = 'andar_cm'
        """,
        (hoje,),
    )
    dist_hoje = float((cursor.fetchone() or {}).get("dist_hoje") or 0.0)

    # 2. Métricas gerais conforme filtro
    cursor.execute(
        f"""
            SELECT
                COUNT(*) AS total_registros,
                COALESCE(AVG(velocidade), 0) AS velocidade_media,
                COALESCE(SUM(CASE WHEN acao = 'andar_cm' THEN distancia_cm ELSE 0 END), 0) AS dist_total
            FROM viagens
            {where_sql}
        """,
        tuple(params),
    )
    resumo = cursor.fetchone() or {}

    # 3. Distância por dia (andar_cm)
    cursor.execute("""
            SELECT DATE(data_hora) AS dia, COALESCE(SUM(distancia_cm), 0) AS total_cm
            FROM viagens
            WHERE acao = 'andar_cm'
            GROUP BY DATE(data_hora)
            ORDER BY dia ASC
            LIMIT 14
        """)
    por_dia = []
    for row in cursor.fetchall():
      por_dia.append({
          "dia": str(row["dia"]),
          "total_cm": round(float(row["total_cm"] or 0.0), 2),
      })

    # 4. Quantidade por ação
    cursor.execute(
        f"""
            SELECT COALESCE(acao, 'andar_cm') AS acao, COUNT(*) AS quantidade
            FROM viagens
            {where_sql}
            GROUP BY COALESCE(acao, 'andar_cm')
        """,
        tuple(params),
    )
    por_acao = cursor.fetchall()

    # 5. Lista de viagens recentes
    cursor.execute(
        f"""
            SELECT id, data_hora, acao, valor, velocidade, distancia_cm
            FROM viagens
            {where_sql}
            ORDER BY id DESC
            LIMIT 30
        """,
        tuple(params),
    )
    viagens = []
    for v in cursor.fetchall():
      viagens.append({
          "id": v["id"],
          "data_hora": str(v["data_hora"]),
          "acao": v.get("acao"),
          "valor": v.get("valor"),
          "velocidade": v.get("velocidade"),
          "distancia_cm": float(v.get("distancia_cm") or 0.0),
      })

    cursor.close()
    conn.close()

    return (
        jsonify({
            "kpis": {
                "distancia_hoje_cm": round(dist_hoje, 2),
                "distancia_total_cm": round(
                    float(resumo.get("dist_total") or 0.0), 2
                ),
                "velocidade_media": round(
                    float(resumo.get("velocidade_media") or 0.0), 1
                ),
                "total_registros": int(resumo.get("total_registros") or 0),
                "limite_manutencao_cm": LIMITE_MANUTENCAO_CM,
                "manutencao_necessaria": dist_hoje >= LIMITE_MANUTENCAO_CM,
            },
            "por_dia": por_dia,
            "por_acao": por_acao,
            "viagens": viagens,
        }),
        200,
    )
  except Exception as e:
    return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001)