import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import time

# --- Configuration ---
# M: The size of the finite hash space (Pigeonholes).
HASH_SPACE_SIZE = 50

# N: The number of inputs (Pigeons). N > M guarantees a collision.
NUM_INPUTS = 100

# Length of random strings to generate
INPUT_LENGTH = 8

# Speed of animation in milliseconds
DELAY_MS = 100

def simple_non_crypto_hash(input_string, space_size):
    """
    A simple, non-cryptographic hash function for demonstration.
    Maps a string to an integer in the fixed space [0, space_size - 1].
    """
    hash_value = 0
    # Sum the ASCII values of the characters
    for char in input_string:
        hash_value += ord(char)
    
    # Use modulo to constrain the hash output to the fixed space
    return hash_value % space_size

def generate_random_input(length):
    """Generates a random string of a given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class HashVisualizer:
    def __init__(self, master):
        self.master = master
        master.title("Pigeonhole Hash Collision Demonstrator")
        master.geometry("1000x800")
        
        # Data structure: List of lists (for chaining)
        self.hash_table = [[] for _ in range(HASH_SPACE_SIZE)]
        self.inputs_data = [] # List to hold all generated input strings
        self.current_input_index = 0
        self.total_collisions = 0

        # --- Styles ---
        self.master.tk_setPalette(background='#1e1e1e', foreground='white')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', background='#4f46e5', foreground='white', font=('Inter', 12, 'bold'))
        style.map('TButton', background=[('active', '#3c32e1')])
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Inter', 10))
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), foreground='#818cf8')

        # --- Setup UI Components ---

        # 1. Control Panel
        control_frame = ttk.Frame(master, padding="15", relief="groove")
        control_frame.pack(side="top", fill="x")

        ttk.Label(control_frame, text="Pigeonhole Principle Demonstration", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(control_frame, text=f"Pigeonholes (M, Hash Space): {HASH_SPACE_SIZE}", foreground="#a5b4fc").grid(row=1, column=0, sticky='w')
        ttk.Label(control_frame, text=f"Pigeons (N, Inputs): {NUM_INPUTS}", foreground="#a5b4fc").grid(row=1, column=1, sticky='w')
        
        self.status_label = ttk.Label(control_frame, text="Status: Ready", font=('Inter', 12, 'bold'), foreground="#facc15")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)

        self.collision_label = ttk.Label(control_frame, text="Collisions Found: 0", font=('Inter', 10), foreground="#f87171")
        self.collision_label.grid(row=3, column=0, columnspan=2, sticky='w')
        
        self.start_button = ttk.Button(control_frame, text="Start Animation (N > M)", command=self.start_demonstration)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        # 2. Hash Grid Visualization Area
        self.canvas = tk.Canvas(master, bg='#0f172a', highlightthickness=0)
        self.canvas.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        self.slot_rects = {} # Stores canvas item IDs for collision highlighting

        self.initialize_data()
        self.draw_grid()

    def initialize_data(self):
        """Generates all random inputs before the animation starts."""
        self.inputs_data = [generate_random_input(INPUT_LENGTH) for _ in range(NUM_INPUTS)]

    def draw_grid(self):
        """Draws the empty hash slots (pigeonholes) on the canvas."""
        self.canvas.delete("all")
        self.slot_rects.clear()
        
        padding = 10
        cols = 5
        rows = (HASH_SPACE_SIZE + cols - 1) // cols
        
        # Calculate size for each slot
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        slot_w = (canvas_width - padding * (cols + 1)) / cols
        slot_h = (canvas_height - padding * (rows + 1)) / rows
        
        for i in range(HASH_SPACE_SIZE):
            col = i % cols
            row = i // cols
            
            x1 = padding + col * (slot_w + padding)
            y1 = padding + row * (slot_h + padding)
            x2 = x1 + slot_w
            y2 = y1 + slot_h
            
            # Draw the slot rectangle
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                fill='#2c2c2c', outline='#444444', width=2)
            self.slot_rects[i] = rect
            
            # Draw the slot index label
            self.canvas.create_text(x1 + 5, y1 + 5, anchor='nw', text=f"#{i}", fill='#9ca3af', font=('Inter', 8))
            
            # Draw initial count
            self.canvas.create_text(x2 - 5, y1 + 5, anchor='ne', text=f"(0)", fill='#9ca3af', font=('Inter', 8), tags=f"count-{i}")
            
    def start_demonstration(self):
        """Resets and starts the animation."""
        self.start_button.config(state=tk.DISABLED, text="Animating...")
        self.current_input_index = 0
        self.total_collisions = 0
        self.hash_table = [[] for _ in range(HASH_SPACE_SIZE)]
        self.collision_label.config(text="Collisions Found: 0")
        self.status_label.config(text="Status: Running", foreground="#34d399")
        self.draw_grid() # Redraw clean grid
        self.animate_hashing()

    def animate_hashing(self):
        """The main animation loop, adding one input at a time."""
        
        if self.current_input_index >= NUM_INPUTS:
            self.status_label.config(text="Status: Complete!", foreground="#facc15")
            self.start_button.config(state=tk.NORMAL, text="Restart Demonstration")
            return
            
        input_data = self.inputs_data[self.current_input_index]
        hash_output = simple_non_crypto_hash(input_data, HASH_SPACE_SIZE)
        
        # Collision Check (Pigeonhole Logic)
        is_collision = len(self.hash_table[hash_output]) > 0
        
        if is_collision:
            self.total_collisions += 1
            self.collision_label.config(text=f"Collisions Found: {self.total_collisions}")
            # Collision color: Red
            flash_color = '#b91c1c' 
            permanent_color = '#3730a3' # Deeper Indigo for collision slots
        else:
            # First placement color: Green
            flash_color = '#10b981' 
            permanent_color = '#2c2c2c'
            
        # 1. Update Hash Table (Chaining Resolution)
        self.hash_table[hash_output].append(input_data)
        
        # 2. Update UI (The "frame" change)
        self.update_status_bar(input_data, hash_output)
        self.flash_slot(hash_output, flash_color, permanent_color, is_collision)
        self.update_slot_content(hash_output, input_data)
        
        self.current_input_index += 1
        
        # Schedule the next frame
        self.master.after(DELAY_MS, self.animate_hashing)

    def update_status_bar(self, input_data, hash_output):
        """Updates the top status bar with current pigeon details."""
        self.status_label.config(text=f"Processing Input {self.current_input_index + 1}/{NUM_INPUTS}: '{input_data}' -> Hash #{hash_output}")
        
    def flash_slot(self, index, flash_color, permanent_color, is_collision):
        """Highlights the pigeonhole temporarily."""
        rect_id = self.slot_rects[index]
        
        # Flash animation
        self.canvas.itemconfig(rect_id, fill=flash_color, outline=flash_color, width=4)
        
        # Return to base color after the flash
        self.master.after(int(DELAY_MS * 0.8), lambda: self.canvas.itemconfig(rect_id, fill=permanent_color, outline='#444444', width=2))
        
        # If it's a collision slot, make it the permanent collision color
        if is_collision:
            self.master.after(DELAY_MS, lambda: self.canvas.itemconfig(rect_id, fill='#3730a3'))

    def update_slot_content(self, index, new_input):
        """Adds the new input string to the visual chain list within the slot."""
        rect_id = self.slot_rects[index]
        
        # Get position details of the slot
        coords = self.canvas.coords(rect_id)
        x1, y1, x2, y2 = coords
        
        # Calculate where to place the text (pushed down with more items)
        chain_length = len(self.hash_table[index])
        
        # Limit the number of visible items to avoid overflow, or use a scrollbar (more complex in Tkinter canvas)
        max_visible_items = 3
        
        # Clear old inputs for this slot
        self.canvas.delete(f"input-{index}")
        
        # Display the chained inputs (up to max_visible_items)
        display_list = self.hash_table[index]
        if chain_length > max_visible_items:
            display_list = display_list[chain_length - max_visible_items:]
            self.canvas.create_text(x1 + 5, y1 + 18, anchor='nw', text=f"...+ {chain_length - max_visible_items} more", fill='#facc15', tags=f"input-{index}", font=('Inter', 8))

        # Start Y position for the newest item
        start_y = y1 + 18 + (chain_length > max_visible_items) * 10
        
        for i, input_item in enumerate(display_list):
            y_pos = y1 + 18 + i * 14 # 14 pixels per item
            
            # Draw the input string as a text element
            self.canvas.create_text(x1 + 5, y_pos, anchor='nw', 
                                    text=f"{input_item}", 
                                    fill='#a7f3d0', # Light green for input text
                                    tags=f"input-{index}", 
                                    font=('Courier', 8))
            
        # Update the hash count label
        self.canvas.delete(f"count-{index}")
        self.canvas.create_text(x2 - 5, y1 + 5, anchor='ne', 
                                text=f"({chain_length})", 
                                fill='#a5b4fc', 
                                font=('Inter', 8, 'bold'), 
                                tags=f"count-{index}")


if __name__ == "__main__":
    root = tk.Tk()
    # Handle window resizing to redraw the grid properly
    root.bind('<Configure>', lambda event: visualizer.draw_grid() if event.widget == root else None)
    visualizer = HashVisualizer(root)
    root.mainloop()
