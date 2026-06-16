import os
import time # Importado para podermos calcular o tempo caso queiramos envolver as duas fases juntas
from src.environment import CityEnvironment
from src.agent import AmbulanceAgent
from src.problem import GraphProblem
from src.search import a_star_search, breadth_first_search, depth_first_search, greedy_search
from src.metrics import Metrics

class Estilo:
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'

def carregar_animacao(mensagem, segundos=3):
    print(f"{Estilo.CIANO}{mensagem}{Estilo.RESET}", end="", flush=True)
    passos = 3
    tempo_pausa = segundos / passos
    for _ in range(passos):
        time.sleep(tempo_pausa)
        print(".", end="", flush=True)
    print()

def executar_simulacao_completa(env_path, local_partida, local_emergencia, hospitais_disponiveis, alertas_sensores, algoritmo_busca, nome_algoritmo, precisao_sensor):
    print(f"\n{Estilo.AZUL}{'='*60}{Estilo.RESET}")
    print(f"{Estilo.NEGRITO}{Estilo.AMARELO}INICIANDO SIMULAÇÃO:{Estilo.RESET} Chamado em {local_emergencia} | Motor: {nome_algoritmo}")
    print(f"{Estilo.NEGRITO}CONFIGURAÇÃO:{Estilo.RESET} Confiabilidade do Sensor definida em {precisao_sensor * 100:.1f}%")
    print(f"{Estilo.AZUL}{'='*60}{Estilo.RESET}")

    env = CityEnvironment(env_path)
    ambulancia = AmbulanceAgent(env, start_location=local_partida, sensor_accuracy=precisao_sensor)

    print(f"\n{Estilo.NEGRITO}[FASE DE PERCEPÇÃO]{Estilo.RESET} Lendo sensores de tráfego...")
    
    if alertas_sensores:
        for avenida in alertas_sensores:
            prob_antes = ambulancia.beliefs.get(avenida, ambulancia.prior_prob)
            
            print(f"  🚨 {Estilo.VERMELHO}ALERTA RECEBIDO:{Estilo.RESET} Possível bloqueio na avenida {avenida}.")
            
            ambulancia.update_beliefs(avenida, sensor_alert=True)
            prob_depois = ambulancia.beliefs.get(avenida, 0.0)
            
            print(f"  {Estilo.AMARELO}Teorema de Bayes:{Estilo.RESET} Chance de bloqueio foi de {prob_antes*100:.1f}% para {prob_depois*100:.1f}%")
        
        carregar_animacao("\nAtualizando as penalidades do mapa com base nas crenças")
        ambulancia.update_environment_weights(threshold=0.65, penalty_factor=5.0)
    else:
        print(f"  ✅ {Estilo.VERDE}Nenhum alerta crítico. O agente assume fluxo natural de trânsito.{Estilo.RESET}")

    print(f"\n{Estilo.NEGRITO}[FASE DE AÇÃO]{Estilo.RESET}")
    carregar_animacao(f"Calculando rotas usando {nome_algoritmo}")
    
    start_time = time.perf_counter()
    
    rota_ida, rota_volta = ambulancia.atender_chamado(
        local_emergencia=local_emergencia,
        hospitais_disponiveis=hospitais_disponiveis,
        problem_class=GraphProblem,
        search_algorithm=algoritmo_busca 
    )
    
    end_time = time.perf_counter()
    tempo_total_ms = (end_time - start_time) * 1000

    print(f"\n{Estilo.NEGRITO}[RELATÓRIO DA MISSÃO]{Estilo.RESET}")
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
        
        custo_total = relatorio_ida['custo_total_trajeto'] + relatorio_volta['custo_total_trajeto']
        print(f"  🚑 {Estilo.NEGRITO}CUSTO TOTAL COMBINADO DA OPERAÇÃO:{Estilo.RESET} {Estilo.VERDE}{custo_total:.1f}{Estilo.RESET}")
        print(f"  ⏱️  {Estilo.NEGRITO}TEMPO TOTAL DE NAVEGAÇÃO:{Estilo.RESET} {Estilo.AMARELO}{tempo_total_ms:.4f} ms{Estilo.RESET}\n")
    else:
        print(f"  ❌ {Estilo.VERMELHO}{Estilo.NEGRITO}FALHA CRÍTICA:{Estilo.RESET} {Estilo.VERMELHO}O agente não conseguiu formular um plano válido.{Estilo.RESET}")
    
    print(f"{Estilo.AZUL}{'='*60}{Estilo.RESET}\n")


def main():

    mapa = "data/mapa_natal.json"
    hospitais = ["Walfredo Gurgel", "Giselda Trigueiro", "Hospital da Policia", "Hospital do Coracao", "Hospital Deoclecio", "Hospital Santa Catarina"]

    print(f"\n{Estilo.AZUL}{'#'*60}{Estilo.RESET}")
    print(f"{Estilo.NEGRITO}{Estilo.CIANO}{'🚑 TERMINAL DE DESPACHO INTELIGENTE - IMD3001':^60}{Estilo.RESET}")
    print(f"{Estilo.AZUL}{'#'*60}{Estilo.RESET}\n")

    try:
        env_temp = CityEnvironment(mapa)
        av_disponiveis = sorted(list(env_temp.graph.nodes()))
        print(f"{Estilo.NEGRITO}LOCAIS MAPEADOS DISPONÍVEIS PARA NAVEGAÇÃO:{Estilo.RESET}")
        print(f"{Estilo.AMARELO}{' | '.join(av_disponiveis)}{Estilo.RESET}")
        print(f"{Estilo.AZUL}{'-' * 60}{Estilo.RESET}\n")
    except Exception as e:
        print(f"{Estilo.VERMELHO}Aviso: Não foi possível carregar a lista de avenidas do mapa: {e}{Estilo.RESET}\n")

    local_partida = input(f"{Estilo.NEGRITO}Digite a avenida/hospital de partida da ambulância:{Estilo.RESET} ").strip()
    local_emergencia = input(f"{Estilo.NEGRITO}Digite a avenida da emergência:{Estilo.RESET} ").strip()

    print(f"\n{Estilo.NEGRITO}Escolha o algoritmo de roteamento:{Estilo.RESET}")
    print(f"  [{Estilo.CIANO}1{Estilo.RESET}] A* (Busca Informada - Ótima)")
    print(f"  [{Estilo.CIANO}2{Estilo.RESET}] Busca Gulosa (Busca Informada)")
    print(f"  [{Estilo.CIANO}3{Estilo.RESET}] BFS (Busca em Largura)")
    print(f"  [{Estilo.CIANO}4{Estilo.RESET}] DFS (Busca em Profundidade)")
    escolha_alg = input("Digite o número do algoritmo (1-4): ").strip()

    mapa_algoritmos = {
        "1": (a_star_search, "A*"),
        "2": (greedy_search, "Busca Gulosa"),
        "3": (breadth_first_search, "BFS"),
        "4": (depth_first_search, "DFS")
    }
    
    algoritmo_escolhido, nome_algoritmo = mapa_algoritmos.get(escolha_alg, (a_star_search, "A* (Padrão)"))

    input_precisao = input(f"\nDefina a precisão do sensor (0.0 a 1.0) [{Estilo.AMARELO}Aperte Enter para padrão 0.85{Estilo.RESET}]: ").strip()
    precisao_sensor = 0.85
    if input_precisao != "":
        try:
            precisao_sensor = float(input_precisao)
            if not (0.0 <= precisao_sensor <= 1.0):
                print(f"{Estilo.VERMELHO}Valor fora do intervalo [0.0, 1.0]. Utilizando o padrão 0.85.{Estilo.RESET}")
                precisao_sensor = 0.85
        except ValueError:
            print(f"{Estilo.VERMELHO}Entrada inválida. Utilizando o padrão 0.85.{Estilo.RESET}")

    alertas_sensores = []
    quer_transito = input(f"\n🚦 Deseja simular um alerta de trânsito em alguma avenida? ({Estilo.VERDE}s{Estilo.RESET}/{Estilo.VERMELHO}n{Estilo.RESET}): ").strip().lower()

    if quer_transito == 's':
        print(f"\n{Estilo.NEGRITO}Defina a avenida onde o sensor apitou.{Estilo.RESET}")
        av = input("  Nome da Avenida com trânsito: ").strip()
        alertas_sensores.append(av)
        
        while input(f"Deseja adicionar outra avenida com trânsito? ({Estilo.VERDE}s{Estilo.RESET}/{Estilo.VERMELHO}n{Estilo.RESET}): ").strip().lower() == 's':
            av_extra = input("  Nome da Avenida: ").strip()
            alertas_sensores.append(av_extra)

    print(f"\n{Estilo.NEGRITO}{Estilo.VERDE}Inicializando o sistema...{Estilo.RESET}")
    time.sleep(1)
    
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
        continuar = input(f"{Estilo.NEGRITO}Deseja realizar um novo despacho?{Estilo.RESET} ({Estilo.VERDE}s{Estilo.RESET}/{Estilo.VERMELHO}n{Estilo.RESET}): ").strip().lower()
        if continuar != 's':
            print(f"\n{Estilo.VERDE}Encerrando o Terminal de Despacho. Até logo!{Estilo.RESET}\n")
            break