from collections import deque
import heapq

from src.problem import Node

def breadth_first_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    
    frontier = deque([node])
    explored = {problem.initial}
    
    while frontier:
        node = frontier.popleft()
        
        for child in node.expand(problem):
            s = child.state
            if problem.goal_test(s):
                return child
            if s not in explored:
                explored.add(s)
                frontier.append(child)
                
    return None

def depth_first_search(problem):
    
    frontier = deque([Node(problem.initial)])
    explored = set()
    
    while frontier:
        node = frontier.pop()
        
        if problem.goal_test(node.state):
            return node
            
        if node.state not in explored:
            explored.add(node.state)
            for child in node.expand(problem):
                if child.state not in explored:
                    frontier.append(child)
                    
    return None

def greedy_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
        
    unique_id = 0
    frontier = []
    heapq.heappush(frontier, (problem.h(node), unique_id, node))
    
    explored = {node.state}
    
    while frontier:
        _, _, node = heapq.heappop(frontier)
        
        if problem.goal_test(node.state):
            return node
            
        for child in node.expand(problem):
            s = child.state
            if s not in explored:
                explored.add(s)
                unique_id += 1
                heapq.heappush(frontier, (problem.h(child), unique_id, child))
                
    return None

def a_star_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
        
    unique_id = 0
    frontier = []
    f_cost = node.path_cost + problem.h(node)
    heapq.heappush(frontier, (f_cost, unique_id, node))
    
    frontier_states = {node.state: node.path_cost}
    explored = set()
    
    while frontier:
        _, _, node = heapq.heappop(frontier)
        
        if problem.goal_test(node.state):
            return node
            
        explored.add(node.state)
        
        for child in node.expand(problem):
            s = child.state
            
            if s in explored:
                continue
                
            if s not in frontier_states or child.path_cost < frontier_states[s]:
                frontier_states[s] = child.path_cost
                child_f_cost = child.path_cost + problem.h(child)
                unique_id += 1
                heapq.heappush(frontier, (child_f_cost, unique_id, child))
                
    return None
