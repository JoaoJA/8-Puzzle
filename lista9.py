import customtkinter as ctk
import random
import time
import heapq
from collections import deque
from PIL import Image, ImageTk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class Puzzle8(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lista 9 - Puzzle")
        self.geometry("400x600")

        self.grid_values = []
        self.board_state = []
        self.algorithm = ctk.StringVar(value="BFS")
        self.seed = ctk.StringVar()
        self.mode = ctk.StringVar(value="Números")
        self.solution_path = []
        self.solution_index = 0
        self.image_tiles = []

        self.seed.trace_add("write", lambda *args: self.shuffle_board())

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Semente:").pack(pady=(10, 0))
        ctk.CTkEntry(self, textvariable=self.seed).pack()

        ctk.CTkLabel(self, text="Escolha o algoritmo:").pack(pady=(10, 0))
        ctk.CTkOptionMenu(self, values=["BFS", "DFS", "A* (h1)", "A* (h2)"], variable=self.algorithm).pack()

        ctk.CTkLabel(self, text="Modo de exibição:").pack(pady=(10, 0))
        ctk.CTkOptionMenu(self, values=["Números", "Imagem"], variable=self.mode, command=lambda _: self.update_board()).pack()

        ctk.CTkButton(self, text="Embaralhar", command=self.shuffle_board).pack(pady=10)
        ctk.CTkButton(self, text="Resolver", command=self.solve_puzzle).pack(pady=10)

        self.label_tempo = ctk.CTkLabel(self, text="Tempo: 0.0s")
        self.label_tempo.pack()

        self.label_passos = ctk.CTkLabel(self, text="Passos: 0")
        self.label_passos.pack()

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)
        for i in range(3):
            row = []
            for j in range(3):
                btn = ctk.CTkButton(frame, text="", width=80, height=80, fg_color="white")
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.grid_values.append(row)

        import os
        import sys
        if hasattr(sys, '_MEIPASS'):
            img_path = os.path.join(sys._MEIPASS, "billgates.jpeg")
        else:
            img_path = os.path.join(os.path.dirname(__file__), "billgates.jpeg")
        self.prepare_image_tiles(img_path)
        self.reset_board()

    def prepare_image_tiles(self, path):
        try:
            img = Image.open(path).resize((240, 240))
            self.image_tiles = []
            for i in range(3):
                for j in range(3):
                    box = (j*80, i*80, (j+1)*80, (i+1)*80)
                    tile = ImageTk.PhotoImage(img.crop(box))
                    self.image_tiles.append(tile)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar a imagem: {e}")
            self.image_tiles = [None] * 9

    def reset_board(self):
        self.board_state = list(range(1, 9)) + [0]
        self.update_board()

    def shuffle_board(self):
        if self.seed.get().isdigit():
            random.seed(int(self.seed.get()))
        else:
            random.seed()
        while True:
            shuffled = self.board_state[:]
            random.shuffle(shuffled)
            if self.is_solvable(shuffled):
                self.board_state = shuffled
                break
        self.update_board()
        self.label_tempo.configure(text="Tempo: 0.0s")
        self.label_passos.configure(text="Passos: 0")

    def update_board(self):
        for i in range(3):
            for j in range(3):
                val = self.board_state[i * 3 + j]
                btn = self.grid_values[i][j]
                if self.mode.get() == "Números":
                    text = str(val) if val != 0 else ""
                    fg = "#333333" if val != 0 else "#DDDDDD"
                    btn.configure(text=text, image=None, fg_color=fg)
                else:
                    img = self.image_tiles[val] if val != 0 else None
                    btn.configure(text="", image=img, fg_color="#DDDDDD" if val == 0 else "white")

    def solve_puzzle(self):
        algo = self.algorithm.get()
        start = tuple(self.board_state)
        goal = tuple(range(1, 9)) + (0,)

        start_time = time.time()

        if algo == "BFS":
            path, visited = self.bfs(start, goal)
        elif algo == "DFS":
            path, visited = self.dfs(start, goal)
        elif algo == "A* (h1)":
            path, visited = self.astar(start, goal, heuristic=self.h1)
        elif algo == "A* (h2)":
            path, visited = self.astar(start, goal, heuristic=self.h2)
        else:
            return

        end_time = time.time()
        duracao = end_time - start_time
        passos = len(path) - 1 if path else 0

        self.label_tempo.configure(text=f"Tempo: {duracao:.4f}s")
        self.label_passos.configure(text=f"Passos: 0")  # Começa do zero e atualiza na animação

        if path:
            self.solution_path = path[1:]
            self.solution_index = 0
            self.animate_solution()

    def animate_solution(self):
        if self.solution_index < len(self.solution_path):
            self.board_state = list(self.solution_path[self.solution_index])
            self.update_board()
            self.solution_index += 1
            self.label_passos.configure(text=f"Passos: {self.solution_index}")
            self.after(300, self.animate_solution)

    def is_solvable(self, state):
        inv_count = 0
        for i in range(8):
            for j in range(i + 1, 9):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inv_count += 1
        return inv_count % 2 == 0

    def get_neighbors(self, state):
        neighbors = []
        zero_index = state.index(0)
        row, col = divmod(zero_index, 3)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in moves:
            r, c = row + dr, col + dc
            if 0 <= r < 3 and 0 <= c < 3:
                new_index = r * 3 + c
                lst = list(state)
                lst[zero_index], lst[new_index] = lst[new_index], lst[zero_index]
                neighbors.append(tuple(lst))
        return neighbors

    def bfs(self, start, goal):
        queue = deque([[start]])
        visited = set([start])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == goal:
                return path, len(visited)
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None, len(visited)

    def dfs(self, start, goal, limit=30):
        stack = [[start]]
        visited = set([start])
        while stack:
            path = stack.pop()
            node = path[-1]
            if node == goal:
                return path, len(visited)
            if len(path) > limit:
                continue
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(path + [neighbor])
        return None, len(visited)

    def astar(self, start, goal, heuristic):
        open_set = []
        heapq.heappush(open_set, (heuristic(start, goal), [start]))
        visited = set([start])
        while open_set:
            _, path = heapq.heappop(open_set)
            node = path[-1]
            if node == goal:
                return path, len(visited)
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    heapq.heappush(open_set, (len(new_path) + heuristic(neighbor, goal), new_path))
        return None, len(visited)

    def h1(self, state, goal):
        return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])

    def h2(self, state, goal):
        dist = 0
        for i, val in enumerate(state):
            if val == 0:
                continue
            goal_idx = goal.index(val)
            x1, y1 = divmod(i, 3)
            x2, y2 = divmod(goal_idx, 3)
            dist += abs(x1 - x2) + abs(y1 - y2)
        return dist

if __name__ == '__main__':
    app = Puzzle8()
    app.mainloop()
