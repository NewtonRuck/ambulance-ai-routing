class AmbulanceAgent:
    def __init__(self, environment, start_location, sensor_accuracy=0.85, false_positive=0.10, prior_prob=0.20):
        # sensor_accuracy: P(Alerta | Engarrafado) - Chance do sensor acertar se a via estiver engarrafada
        # false_positive_rate: P(Alerta | Livre) - Chance do sensor apitar mesmo com a via livre
        # prior_prob: P(Engarrafado) - Probabilidade prévia inicial de qualquer via ter trânsito

        self.environment = environment
        self.current_location = start_location
        self.sensor_accuracy = sensor_accuracy
        self.false_positive_rate = false_positive
        self.prior_prob = prior_prob
        # Um dicionario que mapeia cada rua para a probabilidade dela estar engarrafada
        self.beliefs = {}
        self._initialize_beliefs()
    
    def _initialize_beliefs(self):
        # Preenche a memoria do agente com a probabilidade previa de transito para todas as ruas conhecidas no mapa
        for u, v in self.environment.graph.edges():
            # Usa uma tupla ordenada para padronizar chaves em grafos-nao direcionados
            edge = tuple(sorted((u, v)))
            self.beliefs[edge] = self.prior_prob

    def update_beliefs(self, edge, sensor_alert):
        # Atualiza a probabilidade real de um bloqueio com base no Teorema de Bayes
        edge = tuple(sorted(edge))
        # Se a rua que o sensor tenta atualizar nao existe para o agente, a funcao simplesmente nao retorna nada.
        if edge not in self.beliefs:
            return
        
        # B: Bloqueio
        # E: Evidencia
        p_b = self.beliefs[edge] # P(B): Crença atual que o agente tem de que a rua está bloqueada antes de consultar o sensor
        p_not_b = 1.0 - p_b # P(~B): Probabilidade de nao haver bloqueio

        if sensor_alert:
            # O sensor apitou (Evidencia E é verdadeira)

            p_e_given_b = self.sensor_accuracy # Probabilidade de apitar dado que existe bloqueio
            p_e_given_not_b = self.false_positive_rate # Probabilidade de apitar dado que nao existe bloqueio
        else:
            # O sensor indicou via limpa (Evidencia E é falsa)

            p_e_given_b = 1.0 - self.sensor_accuracy # Probabilidade de nao apitar dado que existe bloqueio
            p_e_given_not_b = 1.0 - self.false_positive_rate # Probabilidade de nao apitar dado que nao existe bloqueio

        # Teorema de Bayes: P(B|E) = [P(E|B) * P(B)] / [P(E|B) * P(B) + P(E|~B) * P(~B)]
        numerador = p_e_given_b * p_b
        denominador = numerador + (p_e_given_not_b * p_not_b)

        p_b_given_e = numerador / denominador if denominador > 0 else 0.0

        self.beliefs[edge] = p_b_given_e

    def update_environment_weights(self, threshold=0.7, penalty_factor=5.0):
        # Verifica as crenças da ambulancia e penaliza o ambiente (aumentando o custo) se a probabilidade de congestionamento for alta

        for edge, prob in self.beliefs.items():

            # Se a chance de bloqueio for maior que o limite...
            if prob > threshold:
                u, v = edge

                # Multiplica o peso original da aresta usando simulate_congestion
                self.environment.simulate_congestion(u, v, penalty_factor)
                # Apos aplicar a penalidade no mapa, reseta a crença dessa via para evitar sua penalizaçao em iteraçoes futuras
                self.beliefs[edge] = self.prior_prob

    def decide_route(self, destination, problem_class, search_algorithm):
        problem = problem_class(self.current_location, destination, self.environment.graph)
        caminho_otimo = search_algorithm(problem)
        
        if caminho_otimo:
            self.current_location = destination
        
        return caminho_otimo
