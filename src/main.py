import os
import time # Importado para podermos calcular o tempo caso queiramos envolver as duas fases juntas
from src.environment import CityEnvironment
from src.agent import AmbulanceAgent
from src.problem import GraphProblem
from src.search import a_star_search, breadth_first_search, depth_first_search, greedy_search
from src.metrics import Metrics 

def executar_simulacao_completa(env_path, local_partida, local_emergencia, hospitais_disponiveis, alertas_sensores, algoritmo_busca, nome_algoritmo, precisao_sensor):
    print("\n" + "="*60)
    print(f"INICIANDO SIMULAÇÃO: Chamado em {local_emergencia} | Motor: {nome_algoritmo}")
    print(f"CONFIGURAÇÃO: Confiabilidade do Sensor definida em {precisao_sensor * 100:.1f}%")
    print("="*60)

    env = CityEnvironment(env_path)
    ambulancia = AmbulanceAgent(env, start_location=local_partida, sensor_accuracy=precisao_sensor)

    print("\n[FASE DE PERCEPÇÃO] Lendo sensores de tráfego...")
    
    if alertas_sensores:
        for avenida in alertas_sensores:
            # Pega a probabilidade antes usando apenas a string da avenida
            prob_antes = ambulancia.beliefs.get(avenida, ambulancia.prior_prob)
            
            print(f"  🚨 ALERTA RECEBIDO: Possível bloqueio na avenida {avenida}.")
            
            # Atualiza crença baseada na avenida
            ambulancia.update_beliefs(avenida, sensor_alert=True)
            prob_depois = ambulancia.beliefs.get(avenida, 0.0)
            
            print(f"Teorema de Bayes: Chance de bloqueio foi de {prob_antes*100:.1f}% para {prob_depois*100:.1f}%")
        
        print("\nAtualizando as penalidades do mapa com base nas crenças...")
        ambulancia.update_environment_weights(threshold=0.65, penalty_factor=5.0)
    else:
        print(" ✅ Nenhum alerta crítico. O agente assume fluxo natural de trânsito.")

    print(f"\n[FASE DE AÇÃO] Calculando rotas usando {nome_algoritmo}...")
    
    start_time = time.perf_counter()
    
    rota_ida, rota_volta = ambulancia.atender_chamado(
        local_emergencia=local_emergencia,
        hospitais_disponiveis=hospitais_disponiveis,
        problem_class=GraphProblem,
        search_algorithm=algoritmo_busca 
    )
    
    end_time = time.perf_counter()
    tempo_total_ms = (end_time - start_time) * 1000

    print("\n[RELATÓRIO DA MISSÃO]")
    if rota_ida and rota_volta:
        prob_ida = GraphProblem(local_partida, local_emergencia, env.graph)
        prob_volta = GraphProblem(local_emergencia, rota_volta.state, env.graph)

        relatorio_ida = Metrics.get_full_report(rota_ida, prob_ida, execution_time_ms=(tempo_total_ms / 2))
        relatorio_volta = Metrics.get_full_report(rota_volta, prob_volta, execution_time_ms=(tempo_total_ms / 2))

        painel_relatorios = {
            f"Fase 1: Indo até a Emergência ({nome_algoritmo})": relatorio_ida,
            f"Fase 2: Levando paciente ao {rota_volta.state} ({nome_algoritmo})": relatorio_volta
        }

        Metrics.print_comparison(painel_relatorios)
        
        # Opcional: Um mini resumo final do custo total
        custo_total = relatorio_ida['custo_total_trajeto'] + relatorio_volta['custo_total_trajeto']
        print(f"  🚑 CUSTO TOTAL COMBINADO DA OPERAÇÃO: {custo_total:.1f}")
        print(f"  ⏱️ TEMPO TOTAL DE NAVEGAÇÃO: {tempo_total_ms:.4f} ms\n")
    else:
        print("  ❌ FALHA CRÍTICA: O agente não conseguiu formular um plano válido.")
    
    print("="*60 + "\n")


def main():
    mapa = "data/mapa_natal.json"
    hospitais = ["Walfredo Gurgel", "Giselda Trigueiro", "Hospital da Policia", "Hospital do Coracao", "Hospital Deoclecio", "Hospital Santa Catarina"]

    print("\n" + "#"*60)
    print(" 🚑 TERMINAL DE DESPACHO INTELIGENTE - IMD3001")
    print("#"*60 + "\n")

    try:
        env_temp = CityEnvironment(mapa)
        av_disponiveis = sorted(list(env_temp.graph.nodes()))
        print("LOCAIS MAPEADOS DISPONÍVEIS PARA NAVEGAÇÃO:")
        print(" | ".join(av_disponiveis))
        print("-" * 60 + "\n")
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a lista de avenidas do mapa: {e}\n")

    local_partida = input("Digite a avenida/hospital de partida da ambulância: ").strip()
    local_emergencia = input("Digite a avenida da emergência: ").strip()

    print("\nEscolha o algoritmo de roteamento:")
    print("  [1] A* (Busca Informada - Ótima)")
    print("  [2] Busca Gulosa (Busca Informada)")
    print("  [3] BFS (Busca em Largura)")
    print("  [4] DFS (Busca em Profundidade)")
    escolha_alg = input("Digite o número do algoritmo (1-4): ").strip()

    mapa_algoritmos = {
        "1": (a_star_search, "A*"),
        "2": (greedy_search, "Busca Gulosa"),
        "3": (breadth_first_search, "BFS"),
        "4": (depth_first_search, "DFS")
    }
    
    algoritmo_escolhido, nome_algoritmo = mapa_algoritmos.get(escolha_alg, (a_star_search, "A* (Padrão)"))

    input_precisao = input("\nDefina a precisão do sensor (0.0 a 1.0) [Aperte Enter para usar o padrão 0.85]: ").strip()
    precisao_sensor = 0.85
    if input_precisao != "":
        try:
            precisao_sensor = float(input_precisao)
            if not (0.0 <= precisao_sensor <= 1.0):
                print("Valor fora do intervalo [0.0, 1.0]. Utilizando o padrão 0.85.")
                precisao_sensor = 0.85
        except ValueError:
            print("Entrada inválida. Utilizando o padrão 0.85.")

    alertas_sensores = []
    quer_transito = input("\n🚦 Deseja simular um alerta de trânsito em alguma avenida? (s/n): ").strip().lower()

    if quer_transito == 's':
        print("\nDefina a avenida onde o sensor apitou.")
        av = input("  Nome da Avenida com trânsito: ").strip()
        alertas_sensores.append(av)
        
        while input("Deseja adicionar outra avenida com trânsito? (s/n): ").strip().lower() == 's':
            av_extra = input("  Nome da Avenida: ").strip()
            alertas_sensores.append(av_extra)

    print("\nInicializando o sistema...")
    executar_simulacao_completa(
        env_path=mapa,
        local_partida=local_partida,
        local_emergencia=local_emergencia,
        hospitais_disponiveis=hospitais,
        alertas_sensores=alertas_sensores,
        algoritmo_busca=algoritmo_escolhido,
        nome_algoritmo=nome_algoritmo,
        precisao_sensor=precisao_sensor
    )

if __name__ == "__main__":
    while True:
        main()
        continuar = input("Deseja realizar um novo despacho? (s/n): ").strip().lower()
        if continuar != 's':
            print("\nEncerrando o Terminal de Despacho. Até logo!\n")
            break