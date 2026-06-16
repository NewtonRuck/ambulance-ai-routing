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

        self.carrying_patient = False
        # Um dicionario que mapeia cada rua para a probabilidade dela estar engarrafada
        self.beliefs = {}
        self._initialize_beliefs()
    
    def _initialize_beliefs(self):
        # Preenche a memoria do agente com a probabilidade previa de transito para todas as avenidas conhecidas no mapa
        for node in self.environment.graph.nodes():
            self.beliefs[node] = self.prior_prob

    def update_beliefs(self, node, sensor_alert):
        # Se a avenida que o sensor tenta atualizar não existe, a função ignora
        if node not in self.beliefs:
            return
        
        # B: Bloqueio
        # E: Evidencia
        p_b = self.beliefs[node] # P(B): Crença atual que o agente tem de que a avenida está bloqueada antes de consultar o sensor
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

        self.beliefs[node] = p_b_given_e

    def update_environment_weights(self, threshold=0.7, penalty_factor=5.0):

        # Verifica as crenças sobre as avenidas e penaliza seus acessos
        for node, prob in self.beliefs.items():
            if prob > threshold:
                self.environment.simulate_congestion(node, penalty_factor)
                # Reseta a crença dessa avenida para evitar punição infinita
                self.beliefs[node] = self.prior_prob

    def decide_route(self, destination, problem_class, search_algorithm):
        problem = problem_class(self.current_location, destination, self.environment.graph)
        caminho_otimo = search_algorithm(problem)
        
        if caminho_otimo:
            # Se o destino for uma lista de hospitais, o algoritmo retorna o caminho mais rapido
            # Atualizamos a localizacao da ambulancia exatamente para o nó do hospital encontrado
            self.current_location = caminho_otimo.state
        
        return caminho_otimo

    def atender_chamado(self, local_emergencia, hospitais_disponiveis, problem_class, search_algorithm):
        print(f"\n[FASE 1] 🚑 Saindo de {self.current_location} para buscar o paciente em {local_emergencia}...")
        self.carrying_patient = False

        rota_para_paciente = self.decide_route(local_emergencia, problem_class, search_algorithm)

        if not rota_para_paciente:
            print("❌ Falha Crítica: Nenhuma rota encontrada para o paciente!")
            return None, None
        
        self.carrying_patient = True
        print(f"🩺 Paciente embarcado em {local_emergencia}! (carrying_patient = {self.carrying_patient})")

        print(f"\n[FASE 2] 🏥 Paciente a bordo. Buscando rota para o hospital mais próximo...")
        rota_para_hospital = self.decide_route(hospitais_disponiveis, problem_class, search_algorithm)

        if not rota_para_hospital:
            print("❌ Falha Crítica: Nenhuma rota encontrada para os hospitais!")
            return rota_para_paciente, None
        
        self.carrying_patient = False
        hospital_escolhido = rota_para_hospital.state
        print(f"🏥 Paciente entregue com segurança no {hospital_escolhido}! (carrying_patient = {self.carrying_patient})")

        return rota_para_paciente, rota_para_hospital