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
        self.active_slots = [] # Stores indices with data for resolution phase
        self.current_resolution_index = 0

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
        
        # Button container for dual buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Collision Demonstration", command=self.start_demonstration)
        self.start_button.pack(side="left", padx=5)

        self.resolution_button = ttk.Button(button_frame, text="Start Resolution (Empty Chains)", command=self.start_resolution, state=tk.DISABLED)
        self.resolution_button.pack(side="left", padx=5)

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
        self.resolution_button.config(state=tk.DISABLED)
        self.current_input_index = 0
        self.total_collisions = 0
        self.hash_table = [[] for _ in range(HASH_SPACE_SIZE)]
        self.collision_label.config(text="Collisions Found: 0")
        self.status_label.config(text="Status: Running Collision Phase", foreground="#34d399")
        self.draw_grid() # Redraw clean grid
        self.animate_hashing()

    def animate_hashing(self):
        """The main animation loop, adding one input at a time."""
        
        if self.current_input_index >= NUM_INPUTS:
            self.status_label.config(text="Status: Collision Phase Complete!", foreground="#facc15")
            self.start_button.config(state=tk.NORMAL, text="Restart Demonstration")
            # Enable resolution phase button
            self.resolution_button.config(state=tk.NORMAL)
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
        self.redraw_slot_content(hash_output)
        
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

    def redraw_slot_content(self, index):
        """Redraws the visual chain list within the slot based on the current hash_table state."""
        rect_id = self.slot_rects[index]
        
        # Get position details of the slot
        coords = self.canvas.coords(rect_id)
        x1, y1, x2, y2 = coords
        
        chain_length = len(self.hash_table[index])
        max_visible_items = 3
        
        # Clear old inputs and count
        self.canvas.delete(f"input-{index}")
        self.canvas.delete(f"count-{index}")
        
        # --- 1. Update Hash Count Label ---
        is_empty = chain_length == 0
        self.canvas.create_text(x2 - 5, y1 + 5, anchor='ne', 
                                text=f"({chain_length})", 
                                fill='#a5b4fc' if not is_empty else '#9ca3af', 
                                font=('Inter', 8, 'bold'), 
                                tags=f"count-{index}")

        # --- 2. Update Slot Background Color (for cleanup phase) ---
        if is_empty:
            # When the chain empties, revert the slot color
            self.canvas.itemconfig(rect_id, fill='#2c2c2c')

        # --- 3. Redraw List Items (Chaining) ---
        if is_empty:
            return

        display_list = self.hash_table[index]
        
        # Handle overflow indicator
        if chain_length > max_visible_items:
            # Display only the last max_visible_items items
            display_list = display_list[chain_length - max_visible_items:]
            self.canvas.create_text(x1 + 5, y1 + 18, anchor='nw', text=f"...+ {chain_length - max_visible_items} more", fill='#facc15', tags=f"input-{index}", font=('Inter', 8))

        # Start Y position for items
        start_y_offset = 18 + (chain_length > max_visible_items) * 10
        
        for i, input_item in enumerate(display_list):
            y_pos = y1 + start_y_offset + i * 14 # 14 pixels per item
            
            # Draw the input string as a text element
            self.canvas.create_text(x1 + 5, y_pos, anchor='nw', 
                                    text=f"{input_item}", 
                                    fill='#a7f3d0', 
                                    tags=f"input-{index}", 
                                    font=('Courier', 8))

    def start_resolution(self):
        """Initializes and starts the collision resolution animation."""
        self.start_button.config(state=tk.DISABLED)
        self.resolution_button.config(state=tk.DISABLED, text="Resolving...")
        self.status_label.config(text="Status: Starting Resolution Phase", foreground="#818cf8")
        
        # Get all indices that actually have inputs (are not empty)
        self.active_slots = [i for i, chain in enumerate(self.hash_table) if chain]
        self.current_resolution_index = 0
        
        if not self.active_slots:
            self.status_label.config(text="Status: Nothing to resolve (all chains are empty).", foreground="#facc15")
            self.resolution_button.config(state=tk.DISABLED, text="No Chains")
            self.start_button.config(state=tk.NORMAL)
            return

        self.animate_resolution()

    def animate_resolution(self):
        """Animates the removal (retrieval/emptying) of chains one by one."""
        
        if self.current_resolution_index >= len(self.active_slots):
            self.status_label.config(text="Status: All Data Retrieved and Collisions Resolved!", foreground="#34d399")
            self.resolution_button.config(text="Resolution Complete", state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL, text="Restart Demonstration")
            return

        hash_index = self.active_slots[self.current_resolution_index]
        chain = self.hash_table[hash_index]

        if not chain:
            # Chain is empty, move to the next slot after a slight pause
            self.current_resolution_index += 1
            self.master.after(DELAY_MS * 3, self.animate_resolution)
            return

        # 1. Pop the input from the chain (simulating retrieval/cleanup)
        input_data = chain.pop(0)
        
        # 2. Update Status and UI
        self.status_label.config(text=f"Resolving Hash #{hash_index}: Retrieving '{input_data}'. Items remaining: {len(chain)}")
        
        self.highlight_resolution_slot(hash_index)
        self.redraw_slot_content(hash_index)
        
        # Schedule the next removal step (either next item in the same chain or next slot)
        self.master.after(DELAY_MS, self.animate_resolution)

    def highlight_resolution_slot(self, index):
        """Highlights the slot being resolved (retrieval color)."""
        rect_id = self.slot_rects[index]
        # Flash light blue for retrieval/resolution
        flash_color = '#3b82f6' 
        self.canvas.itemconfig(rect_id, fill=flash_color, outline=flash_color, width=4)
        
        # Determine the return color (empty/base or still-collided/indigo)
        permanent_color = '#2c2c2c' if not self.hash_table[index] else '#3730a3'
        
        # Return to base color after the flash
        self.master.after(int(DELAY_MS * 0.8), lambda: self.canvas.itemconfig(rect_id, fill=permanent_color, outline='#444444', width=2))


if __name__ == "__main__":
    root = tk.Tk()
    # Handle window resizing to redraw the grid properly
    root.bind('<Configure>', lambda event: visualizer.draw_grid() if event.widget == root else None)
    visualizer = HashVisualizer(root)
    root.mainloop()
