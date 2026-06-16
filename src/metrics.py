import math
import time

class Metrics:
    @staticmethod
    def measure_execution_time(search_function, problem):
        start_time = time.perf_counter()
        result_node = search_function(problem)
        end_time = time.perf_counter()
        
        # Converte a diferença para milissegundos
        execution_time_ms = (end_time - start_time) * 1000
        return result_node, execution_time_ms

    @staticmethod
    def calculate_path_cost(node):
        if node is None:
            return float('inf')
        return node.path_cost

    @staticmethod
    def calculate_path_length(node):
        if node is None:
            return 0
        return len(node.path()) - 1  

    @staticmethod
    def evaluate_efficiency(node, graph_problem):
        if node is None:
            return 0.0
            
        # Usa o método que corrigimos em problem.py
        distancia_ideal = graph_problem._distancia_euclidiana(graph_problem.initial, graph_problem.goal)
        custo_real = node.path_cost
        
        if custo_real == 0: 
            return 1.0
            
        return distancia_ideal / custo_real

    @staticmethod
    def get_full_report(node, graph_problem, execution_time_ms=None, nodes_expanded=None):
        if node is None:
            return {
                "sucesso": False,
                "mensagem": "Nenhum caminho foi encontrado até o hospital."
            }

        report = {
            "sucesso": True,
            "custo_total_trajeto": Metrics.calculate_path_cost(node),
            "avenidas_percorridas": Metrics.calculate_path_length(node),
            "eficiencia_da_rota_percentual": Metrics.evaluate_efficiency(node, graph_problem) * 100,
            "rota": [n.state for n in node.path()]
        }

        if execution_time_ms is not None:
            report["tempo_de_execucao_ms"] = round(execution_time_ms, 4)
            
        if nodes_expanded is not None:
            report["nos_expandidos_computacionalmente"] = nodes_expanded

        return report

    @staticmethod
    def print_comparison(reports_dict):
        print("\n" + "="*50)
        print("   📊 PAINEL COMPARATIVO DE ROTEAMENTO DE AMBULÂNCIA")
        print("="*50)
        
        for algo_name, r in reports_dict.items():
            print(f"\nAlgoritmo: {algo_name}")
            if not r["sucesso"]:
                print("  ❌ Falha ao encontrar rota.")
                continue
            print(f"  • Custo total do trajeto (Tempo/Trânsito): {r['custo_total_trajeto']:.1f}")
            print(f"  • Avenidas no caminho: {r['avenidas_percorridas']}")
            print(f"  • Eficiência geométrica da rota: {r['eficiencia_da_rota_percentual']:.2f}%")
            if "tempo_de_execucao_ms" in r:
                print(f"  • Tempo de processamento: {r['tempo_de_execucao_ms']} ms")
            print(f"  • Rota sugerida: {' -> '.join(r['rota'])}")
        print("\n" + "="*50)