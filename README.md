# Roteamento Inteligente de Ambulâncias (Ambulance AI Routing)

> **Trabalho Prático da Disciplina IMD3001 - Introdução à Inteligência Artificial** > **Instituição:** Instituto Metrópole Digital (IMD) - UFRN  
> **Docente:** Prof. Dr. André Fonseca  

---

## Contextualização e Objetivo do Projeto

No gerenciamento de emergências médicas pré-hospitalares, cada segundo poupado é crucial para a preservação de vidas. Fatores urbanos imprevisíveis, como engarrafamentos repentinos, acidentes e bloqueios de vias, tornam o despacho estático ineficiente. 

Este projeto consiste em um **Simulador de Despacho e Roteamento Otimizado de Ambulâncias**, utilizando a topologia e a malha viária reais aproximadas da cidade de **Natal/RN**. O sistema simula o ciclo de atendimento completo em duas fases críticas:
1. **Fase de Ida:** A ambulância parte de uma base inicial, traça e percorre a rota ótima até o local onde a vítima se encontra.
2. **Fase de Retorno (Resgate):** Após resgatar a vítima, o agente recalcula a rota em tempo real direcionando-se ao hospital adequado mais próximo ou estrategicamente viável.

O grande diferencial do projeto está na inteligência do agente, que é capaz de ponderar o trânsito dinâmico utilizando **Raciocínio Probabilístico** para interpretar dados de sensores ruidosos e atualizar suas buscas de forma autônoma.

---

## Fundamentos de IA: Modelagem PEAS e Ambiente

### Descrição PEAS (Performance, Environment, Actuators, Sensors)
* **P (Medida de Desempenho / Performance):** Minimizar o custo total do trajeto (distância percorrida e tempo gasto), otimizar o tempo de resposta conforme a gravidade da ocorrência e minimizar o custo computacional avaliado pelo número de nós expandidos no grafo.
* **E (Ambiente de Tarefa / Environment):** Malha rodoviária de Natal/RN modelada como um grafo ponderado. Os nós representam avenidas ou cruzamentos e as arestas representam as vias com trânsito dinâmico e variável.
* **A (Atuadores / Actuators):** Mecanismo de navegação urbana que comanda o deslocamento físico/lógico entre os nós vizinhos do grafo e sistema de seleção de destino.
* **S (Sensores / Sensors):** GPS integrado para leitura da localização atual exata e relatórios de tráfego enviados por uma central (alertas ruidosos de trânsito).

### Propriedades do Ambiente de Tarefa
* **Parcialmente Observável:** O agente conhece a estrutura das ruas e sua posição exata, mas não sabe de antemão o estado real de trânsito de todas as vias até receber leituras sensoriais ou aproximar-se delas.
* **Estocástico:** O tráfego urbano varia de forma aleatória e imprevisível através de eventos de congestionamento simulados.
* **Sequencial:** Uma decisão de rota tomada pelo agente em um cruzamento altera suas coordenadas futuras e limita ou expande suas opções de desvios subsequentes.
* **Dinâmico:** O ambiente (trânsito) continua mudando continuamente enquanto o agente toma decisões e se desloca.
* **Discreto:** A lógica de tomada de decisão é baseada em estados mapeados em um grafo discreto de avenidas e conexões.
* **Agente Único:** A ambulância interage e resolve o problema de otimização de forma isolada em relação ao ambiente.

---

## Métodos de Inteligência Artificial Implementados

O projeto foi construído sobre dois pilares clássicos da literatura de IA (Russell & Norvig):

### 1. Busca Informada Nao Informada e Heurística (Algoritmo A*, BFS, Greedy e DFS)
O motor de roteamento principal utiliza o algoritmo **A* (A-Estrela)** para garantir a otimalidade do caminho. A função de avaliação é descrita por $f(n) = g(n) + h(n)$, onde:
* $g(n)$: Custo acumulado da via (comprimento base multiplicado pelo fator de trânsito).
* **Heurística $h(n)$ (Admissível e Consistente):** Calculada utilizando a **Distância Euclidiana em linha reta** entre as coordenadas reais aproximadas (`pos`) capturadas no arquivo de dados. Na fase de retorno, a heurística é dinamicamente ajustada para mirar no hospital mais próximo entre todos os disponíveis no mapa.
* *Algoritmos de comparação:* Para fins de validação acadêmica, os módulos também trazem as implementações de **Busca em Largura (BFS)**, **Busca em Profundidade (DFS)** e **Busca Gulosa (Greedy Search)**.

### 2. Tratamento de Incerteza (Teorema de Bayes)
A ambulância não possui acesso mágico ao estado exato do trânsito. Ela recebe um alerta sensorial ruidoso com precisão limitada (ex: 75% de confiabilidade). Antes de tomar a decisão de desviar ou não de uma avenida, o agente executa uma **Atualização Bayesiana** para calcular a probabilidade real de bloqueio dada a evidência do sensor:

$$P(\text{Trânsito Real} \mid \text{Alerta}) = \frac{P(\text{Alerta} \mid \text{Trânsito Real}) \cdot P(\text{Trânsito Real})}{P(\text{Alerta})}$$

Se a probabilidade posterior ultrapassar o limiar de aceitação do agente, ele infere que o engarrafamento é real, injeta uma penalidade no peso daquela aresta específica no grafo e comanda o A* a realizar um replanejamento preventivo.

---

## Estrutura Modular do Repositório

O código foi projetado seguindo as restrições de modularidade do padrão clássico **AIMA**, separando de forma estrita as responsabilidades do mundo, da mente e da visualização:

```text
ambulance-ai-routing/
├── data/
│   └── mapa_natal.json         # Base de dados: Nós geográficos (avenidas), hospitais e conexões (vias)
├── src/
│   ├── problem.py              # Padrão AIMA: Classes abstratas Node, Problem e a subclasse GraphProblem
│   ├── search.py               # Motores de Busca: Implementações de A*, BFS, DFS e Busca Gulosa
│   ├── environment.py          # O Mundo: Controla o grafo NetworkX, distâncias e a injeção estocástica de trânsito
│   ├── agent.py                # O Cérebro: Classe AmbulanceAgent (Teorema de Bayes e estados da ambulância)
│   ├── metrics.py              # Avaliação: Coleta estatísticas de nós expandidos, custo de caminho e tempos
│   └── main.py                 # O Orquestrador: Integra todos os módulos em um fluxo completo de simulação
├── requirements.txt            # Dependências obrigatórias do projeto
├── LICENSE                     # Licença MIT do repositório
└── README.md                   # Esta documentação explicativa
```
Instalação e Configuração
Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado em sua máquina.

Passo 1: Clonar o Repositório com: git clone [https://github.com/NewtonRuck/ambulance-ai-routing.git](https://github.com/NewtonRuck/ambulance-ai-routing.git)
cd ambulance-ai-routing

Passo 2: Criar e Ativar Ambiente Virtual (Recomendado) com: python3 -m venv venv
source venv/bin/activate (Linux) 

ou python -m venv venv
venv\Scripts\activate (Windows)

Passo 3: Instalar as Dependências
Instale as bibliotecas de terceiros necessárias listadas no gerenciador: pip install -r requirements.txt

Caso não funcione, instale manualmente com:

pip install networkx

pip install matplotlib

pip install scipy

Como Executar o Simulador
Para inicializar a simulação completa integrada, execute o arquivo principal na raiz do repositório: python src/main.py

O que acontece durante a execução?
Log de Missão no Terminal: O sistema carrega o grafo de Natal/RN, instacia o agente e gera uma chamada de emergência, uma origem, uma vítima e mapeando os hospitais da rede.

Injeção de Alertas e Atualização Bayesiana: O terminal exibirá o cálculo probabilístico feito pela mente da ambulância ao julgar se deve ou não desviar de uma via com base no alerta ruidoso.

Análise Comparativa de Métricas: Serão expostos os dados de eficiência da rota calculada pelo algoritmo (tempo de cálculo em milissegundos, custo real acumulado e número de nós expandidos).

Métricas e Validação de Resultados
O módulo src/metrics.py valida a eficácia dos algoritmos aplicados monitorando:

Custo da Trajetória: Soma exata dos pesos ponderados pelo trânsito das vias escolhidas.

Nós Expandidos: Demonstra a eficiência matemática do algoritmo.

Tempo de Execução: Medido em alta precisão via time.perf_counter() para avaliar a capacidade do algoritmo rodar em tempo real em cenários críticos.

Referências Bibliográficas
RUSSELL, Stuart; NORVIG, Peter. Inteligência Artificial: uma abordagem moderna. 4. ed. Rio de Janeiro: GEN LTC, 2022.

NETWORKX Developers. NetworkX Documentation: Network Analysis in Python. Disponível em: https://networkx.org/.
