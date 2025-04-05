import pygame
import math
import heapq
from datetime import datetime
import matplotlib.pyplot as plt
import networkx as nx
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 800
GRID_SIZE = 5  # 5x5 grid
NODE_RADIUS = 15
FONT_SIZE = 12
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
BACKGROUND = (240, 240, 240)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dijkstra's Algorithm - Limited Connection Grid")
font = pygame.font.SysFont('Arial', FONT_SIZE)
clock = pygame.time.Clock()

class TrafficLight:
    def _init_(self):
        self.cycle_time = 20  # Fixed cycle time
        self.green_time = self.cycle_time / 2
        self.red_time = self.cycle_time / 2
        self.current_light = 'red' if random.random() < 0.5 else 'green'
        self.last_light_change = pygame.time.get_ticks()  # gets the time in milliseconds since pygame.init() was called, this is useful for implementing timers, animations, and game logic
    
    def update(self):
        current_time = pygame.time.get_ticks()  # time passed since the initialization of the window.
        elapsed = (current_time - self.last_light_change) / 1000  # total time elapsed since the window was created and a light changed.
        
        if self.current_light == 'green' and elapsed > self.green_time:
            self.current_light = 'red'
            self.last_light_change = current_time
        elif self.current_light == 'red' and elapsed > self.red_time:
            self.current_light = 'green'
            self.last_light_change = current_time
    
    def get_remaining_time(self):
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_light_change) / 1000
        
        if self.current_light == 'green':
            remaining = max(0, self.green_time - elapsed)
            return remaining, 'green'
        else:
            remaining = max(0, self.red_time - elapsed)
            return remaining, 'red'

class Node:
    def _init_(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.connections = {}
        self.traffic_light = TrafficLight() if random.random() < 0.7 else None
    
    def update_traffic_light(self):
        if self.traffic_light:
            self.traffic_light.update()
    
    def get_light_delay(self):
        if not self.traffic_light:
            return 0
        remaining, current = self.traffic_light.get_remaining_time()
        return remaining if current == 'red' else 0
    
    def draw(self, screen, selected=False):
        color = BLUE
        if selected:
            color = RED
        elif self.traffic_light:
            remaining, current = self.traffic_light.get_remaining_time()
            color = GREEN if current == 'green' else RED
        
        pygame.draw.circle(screen, color, (self.x, self.y), NODE_RADIUS)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y - NODE_RADIUS - 5))
        screen.blit(text, text_rect)
        
        if self.traffic_light:
            remaining, current = self.traffic_light.get_remaining_time()
            light_text = font.render(f"{remaining:.1f}s", True, BLACK)
            light_rect = light_text.get_rect(center=(self.x, self.y + NODE_RADIUS + 5))
            screen.blit(light_text, light_rect)

class Graph:
    def _init_(self):
        self.nodes = []
        self.selected_start = None
        self.selected_end = None
        self.optimal_path = []
        self.optimal_distance = 0
        self.optimal_time = 0
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def connect_nodes(self, node1, node2):
        dx = node1.x - node2.x
        dy = node1.y - node2.y
        distance = math.sqrt(dx*dx + dy*dy)
        node1.connections[node2] = {'distance': distance, 'weight': distance}
        node2.connections[node1] = {'distance': distance, 'weight': distance}
    
    def update_traffic_lights(self):
        for node in self.nodes:
            node.update_traffic_light()
        
        for node in self.nodes:
            for neighbor in node.connections:
                node.connections[neighbor]['weight'] = (
                    node.connections[neighbor]['distance'] + 
                    neighbor.get_light_delay()
                )
    
    def dijkstra(self, start, end):
        heap = [(0, start, [])]
        visited = set()
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        
        while heap:
            current_weight, current_node, path = heapq.heappop(heap)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            new_path = path + [current_node]
            
            if current_node == end:
                total_distance = sum(
                    new_path[i].connections[new_path[i+1]]['distance'] 
                    for i in range(len(new_path)-1)
                )
                return new_path, total_distance, current_weight
            
            for neighbor, data in current_node.connections.items():
                if neighbor not in visited:
                    new_weight = current_weight + data['weight']
                    if new_weight < distances[neighbor]:
                        distances[neighbor] = new_weight
                        heapq.heappush(heap, (new_weight, neighbor, new_path))
        
        return None, 0, 0
    
    def find_optimal_path(self):
        if self.selected_start and self.selected_end:
            path, distance, time = self.dijkstra(self.selected_start, self.selected_end)
            if path:
                self.optimal_path = path
                self.optimal_distance = distance
                self.optimal_time = time
                return True
        return False
    
    def draw(self, screen):
        # Draw connections first (under nodes)
        for node in self.nodes:
            for neighbor, data in node.connections.items():
                color = GRAY
                width = 2
                
                # Highlight optimal path
                if (node in self.optimal_path and neighbor in self.optimal_path and
                    abs(self.optimal_path.index(node) - self.optimal_path.index(neighbor)) == 1):
                    color = YELLOW
                    width = 4
                
                pygame.draw.line(screen, color, (node.x, node.y), (neighbor.x, neighbor.y), width)
                
                # Draw distance label
                mid_x = (node.x + neighbor.x) // 2
                mid_y = (node.y + neighbor.y) // 2
                dist_text = font.render(f"{data['distance']:.1f}", True, BLACK)
                screen.blit(dist_text, (mid_x - 10, mid_y - 10))
        
        # Draw nodes on top of connections
        for node in self.nodes:
            selected = (node == self.selected_start or node == self.selected_end)
            node.draw(screen, selected)
        
        # Draw path info
        if self.optimal_path:
            info_text = [
                f"Optimal Path: {' -> '.join([node.name for node in self.optimal_path])}",
                f"Total Distance: {self.optimal_distance:.1f}",
                f"Estimated Time: {self.optimal_time:.1f} (including traffic delays)"
            ]
            
            for i, text in enumerate(info_text):
                rendered = font.render(text, True, BLACK)
                screen.blit(rendered, (10, 10 + i * 20))
    
    def save_map_image(self, filename):
        plt.figure(figsize=(12, 10))
        G = nx.Graph()
        
        pos = {}
        for node in self.nodes:
            G.add_node(node.name)
            pos[node.name] = (node.x, HEIGHT - node.y)
        
        edge_colors = []
        for node in self.nodes:
            for neighbor in node.connections:
                if node.name < neighbor.name:  # Avoid duplicate edges
                    G.add_edge(node.name, neighbor.name, weight=node.connections[neighbor]['distance'])
                    if (node in self.optimal_path and neighbor in self.optimal_path and
                        abs(self.optimal_path.index(node) - self.optimal_path.index(neighbor)) == 1):
                        edge_colors.append('red')
                    else:
                        edge_colors.append('gray')
        
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, 
                edge_color=edge_colors, width=3, font_size=12)
        
        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        if self.optimal_path:
            plt.title(
                f"Optimal Path: {' -> '.join([node.name for node in self.optimal_path])}\n"
                f"Distance: {self.optimal_distance:.1f}, Time: {self.optimal_time:.1f}",
                fontsize=12
            )
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()

def generate_limited_connection_grid():
    graph = Graph()
    spacing_x = WIDTH // (GRID_SIZE + 1)
    spacing_y = HEIGHT // (GRID_SIZE + 1)
    
    # Create nodes in grid
    nodes = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = (col + 1) * spacing_x
            y = (row + 1) * spacing_y
            name = f"{chr(65 + row)}{col + 1}"  # A1, A2, ..., B1, B2, etc.
            node = Node(x, y, name)
            graph.add_node(node)
            nodes.append((row, col, node))
    
    # Connect nodes with exactly 2 connections (when possible)
    for row, col, node in nodes:
        possible_directions = []
        
        # Determine possible connection directions
        if row > 0:
            possible_directions.append((row - 1, col))  # Up
        if row < GRID_SIZE - 1:
            possible_directions.append((row + 1, col))  # Down
        if col > 0:
            possible_directions.append((row, col - 1))  # Left
        if col < GRID_SIZE - 1:
            possible_directions.append((row, col + 1))  # Right
        
        # Randomly select 2 directions (or fewer if not possible)
        random.shuffle(possible_directions)
        selected_directions = possible_directions[:2]
        
        # Make connections
        for r, c in selected_directions:
            neighbor = next((n for (nr, nc, n) in nodes if nr == r and nc == c), None)
            if neighbor and neighbor not in node.connections:
                graph.connect_nodes(node, neighbor)
    
    return graph

def main():
    graph = generate_limited_connection_grid()
    running = True
    
    while running:
        screen.fill(BACKGROUND)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for node in graph.nodes:
                    dx = node.x - mouse_pos[0]
                    dy = node.y - mouse_pos[1]
                    if math.sqrt(dx*dx + dy*dy) <= NODE_RADIUS:
                        if event.button == 1:  # Left click
                            graph.selected_start = node
                        elif event.button == 3:  # Right click
                            graph.selected_end = node
                        graph.find_optimal_path()
                        break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"optimal_path_{timestamp}.jpg"
                    graph.save_map_image(filename)
                    print(f"Map saved as {filename}")
                elif event.key == pygame.K_r:
                    graph = generate_limited_connection_grid()
                    graph.selected_start = None
                    graph.selected_end = None
                    graph.optimal_path = []
        
        graph.update_traffic_lights()
        graph.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "_main_":
    main()