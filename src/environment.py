import networkx as nx
import json
import random

class CityEnvironment:
    def __init__(self, map_file_path=None):
        # Inicializa um grafo em branco
        self.graph = nx.Graph()
        self.base_weights = {}
        # Se for fornecido um caminho, ele carrega o mapa
        if map_file_path:
            self.load_map_from_json(map_file_path)
        # Dicionario para guardar o custo das ruas (sem transito)

    def load_map_from_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. Adiciona Nós (Bairros/Cruzamentos)
            for node_data in data.get('nodes', []):
                name = node_data['id']
                position = tuple(node_data['pos'])

                self.graph.add_node(name, pos=position)

            # 2. Adiciona Arestas (Ruas/Conexões)
            for edge_data in data.get("edges", []):
                source = edge_data["source"]
                target = edge_data["target"]
                weight = edge_data.get("weight", 1)

                self.graph.add_edge(source, target, weight=weight)
            
            self._save_base_weights()
            print(f"Mapa carregado com sucesso: {self.graph.number_of_nodes()} nós e {self.graph.number_of_edges()} arestas.")

        except FileNotFoundError:
            print(f"Erro: Arquivo {filepath} não encontrado. Inicializando mapa vazio.")
        except Exception as e:
            print(f"Erro ao carregar o mapa: {e}")
        
    def _save_base_weights(self):
        # Salva os pesos das arestas para poder permitir resetar o transito
        for u, v, data in self.graph.edges(data=True):
            edge = tuple(sorted((u, v)))
            self.base_weights[edge] = data['weight']
    
    def simulate_congestion(self, u, v, severity_multiplier):
        # Simula um evento externo alterando o peso de uma aresta especifica
        if self.graph.has_edge(u, v):
            current_weight = self.graph[u][v]['weight']
            # Aumenta o custo da via com base na gravidade
            new_weight = current_weight * severity_multiplier
            self.graph[u][v]['weight'] = new_weight
            print(f"⚠️ Trânsito alterado entre {u} e {v}: Custo foi de {current_weight:.1f} para {new_weight:.1f}")
        else:
            print(f"Não existe conexão direta entre {u} e {v} para aplicar congestionamento.")
    
    # probability quer dizer que cada rua tem 20% de chance de ficar engarrafada
    # max_multiplier quer dizer que o custo da rua pode ficar ate 3 vezes maior
    def apply_random_traffic(self, probability=0.2, max_multiplier=3.0):
        # Adiciona transito aleatorio na cidade para testar o replanejamento de rotas do agente
        for u, v, data in self.graph.edges(data=True):
            if random.random() < probability:
                multiplier = random.uniform(1.5, max_multiplier)
                self.simulate_congestion(u, v, multiplier)
    
    def reset_traffic(self):
        for edge, original_weight in self.base_weights.items():
            u, v = edge
            if self.graph.has_edge(u, v):
                self.graph[u][v]['weight'] = original_weight
        print("Trânsito normalizado.")

    def get_graph(self):
        return self.graph