import os
from src.environment import CityEnvironment
from src.agent import AmbulanceAgent
from src.problem import GraphProblem
from src.search import a_star_search
import random

def main():
    print("="*50)
    print("🚑 SIMULADOR DE DESPACHO INTELIGENTE DE AMBULÂNCIAS")
    print("="*50)

    # Ajusta o caminho para ler o arquivo da pasta 'data' de forma segura
    caminho_mapa = os.path.join(os.path.dirname(__file__), '..', 'data', 'mapa_natal.json')
    env = CityEnvironment(caminho_mapa)

    origem = 'Alecrim'
    destino = 'Tirol'

    agente = AmbulanceAgent(environment=env, start_location=origem)

    print(f"\n[ALERTA] Emergência detectada!")
    print(f"📍 Posição da Ambulância: {origem}")
    print(f"🏥 Destino do Chamado: {destino}")

    print("\nCalculando rota ótima inicial...")

    no_solucao = agente.decide_route(destino, GraphProblem, a_star_search)

    if no_solucao:
        # Extrai a rota percorrendo os nós pai
        rota_inicial = [no.state for no in no_solucao.path()]
        custo_inicial = no_solucao.path_cost
        print(f"✅ Rota encontrada: {' -> '.join(rota_inicial)}")
        print(f"⏱️ Custo total estimado: {custo_inicial:.2f}")
    else:
        print("❌ Nenhuma rota encontrada!")
        return

    print("\n" + "-"*50)
    print("📡 [SENSOR DE TRÂNSITO] Atualização recebida em tempo real...")

    # Simulaçao da atualizaçao probabilistica de transito via Teorema de Bayes
    if len(rota_inicial) > 1:
        #
        indice_aleatorio = random.randint(0, len(rota_inicial) - 2)
        via_suspeita = (rota_inicial[indice_aleatorio], rota_inicial[indice_aleatorio + 1])
        print(f"⚠️ Alerta de congestionamento disparado para a via: {via_suspeita}")

        # Formata a aresta do jeito que esta no dicionario de crenças para acessar a probabilidade calculada
        agente.update_beliefs(via_suspeita, sensor_alert=True)

        edge_key = tuple(sorted(via_suspeita))
        probabilidade_atualizada = agente.beliefs.get(edge_key, 0.85)
        print(f"🧠 Nova probabilidade calculada (Bayes) de bloqueio real: {probabilidade_atualizada:.2%}")

        agente.update_environment_weights()

        print("\nRecalculando rota com as novas condições do ambiente (Replanejamento)...")
        agente.current_location = origem

        novo_no_solucao = agente.decide_route(destino, GraphProblem, a_star_search)

        if novo_no_solucao:
            nova_rota = [no.state for no in novo_no_solucao.path()]
            novo_custo = novo_no_solucao.path_cost
            print(f"✅ Nova Rota Alternativa: {' -> '.join(nova_rota)}")
            print(f"⏱️ Novo Custo total estimado: {novo_custo:.2f}")

            if rota_inicial != nova_rota:
                print("🔄 A ambulância foi desviada inteligentemente do congestionamento!")
            else:
                print("🛣️ A rota foi mantida, pois não havia desvio melhor ou o trânsito era na rua final indispensável.")
        else:
            print("❌ Nenhuma rota alternativa encontrada!")

if __name__ == "__main__":
    main()