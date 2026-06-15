import math
class Problem:
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        # Retorna as ações possíveis a partir do estado atual
        raise NotImplementedError

    def result(self, state):
        # Retorna o estado resultante da execução de uma ação
        raise NotImplementedError
    
    def goal_test(self, state):
        # Retorna True se o estado for um estado objetivo
        return state == self.goal
    
    def path_cost(self, c, state1, action, state2):
        # Custo padrão de +1 caso não seja sobrescrito
        return c + 1

class GraphProblem(Problem):
    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal)
        self.graph = graph

    def actions(self, state):
        # Retorna uma lista com os nomes de todos os bairros conectados ao atual
        return list(self.graph.neighbors(state))

    def result(self, state, action):
        return action

    def path_cost(self, c, state1, action, state2):
        # Consulta o peso da rua que liga state1 a state2
        # .get('weight', 1) caso a aresta não tenha peso definido
        custo_do_passo = self.graph[state1][state2].get('weight', 1.0)
        return c + custo_do_passo

    def h(self, node):
        # Calcula a distância em linha reta do nó atual direto para o hospital.
        return self._distancia_euclidiana(node.state, self.goal)

    def _distancia_euclidiana(self, estado1, estado2):
        # Pega as coordenadas (x, y) de cada estado no grafo
        pos1 = self.graph.nodes[estado1].get('pos')
        pos2 = self.graph.nodes[estado2].get('pos')

        return math.dist(pos1, pos2)

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        # Rastrea a profundidade do nó na árvore
        self.depth = 0 if parent is None else parent.depth + 1
    
    def __lt__(self, node):
        # Define a regra de comparação '<' entre dois nós
        return self.path_cost < node.path_cost
    
    def path(self):
        # Faz o caminho reverso usando 'parents' e depois inverte a lista
        node = self
        path_back = []
        while node is not None:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))
    
    def solution(self):
        # Retorna a sequencia de ações tomadas da raiz até esse nó (ignorando o índice 0)
        return [node.action for node in self.path()[1:]]

    def expand(self, problem):
        # Gera uma lista de todos os nós filhos alcançáveis a partir deste nó
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]
    
    def child_node(self, problem, action):
        # Cria e retorna um novo nó filho, resultado de aplicar uma 'action' ao estado atual
        next_state = problem.result(self.state, action)
        new_cost = problem.path_cost(self.path_cost, self.state, action, next_state)
        return Node(state=next_state,
                    parent=self,
                    action=action,
                    path_cost=new_cost)
    
    def __repr__(self):
        return f"<Node {self.state}>"