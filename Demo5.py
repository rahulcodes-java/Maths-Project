import hashlib
import os

# Configuration
HASH_SPACE_SIZE = 100  # Number of pigeonholes (hash buckets)
NUM_INPUTS = 150       # Number of pigeons (inputs)
INPUT_LENGTH = 8       # Random input length in bytes

# Initialize the hash table: each slot is a list (chaining)
hash_table = [[] for _ in range(HASH_SPACE_SIZE)]

total_collisions = 0

def generate_random_input(length):
    # Generates a random hex string of given byte length
    return os.urandom(length).hex()

def sha256_hash_to_slot(data, space_size):
    # Hash data with SHA-256, return integer slot index in [0, space_size-1]
    hash_hex = hashlib.sha256(data.encode('utf-8')).hexdigest()
    # Use first 8 hex chars (~32 bits) to map into space size
    slot = int(hash_hex[:8], 16) % space_size
    return slot

def main():
    global total_collisions
    for i in range(NUM_INPUTS):
        input_data = generate_random_input(INPUT_LENGTH)
        slot_index = sha256_hash_to_slot(input_data, HASH_SPACE_SIZE)
        is_collision = len(hash_table[slot_index]) > 0
        if is_collision:
            total_collisions += 1
        hash_table[slot_index].append(input_data)
        
        print(f"Input {i + 1:3}: {input_data} → Slot {slot_index} ({'Collision' if is_collision else 'No collision'})")
    
    print("\n--- DEMONSTRATION COMPLETE! ---")
    print(f"Total inputs   : {NUM_INPUTS}")
    print(f"Hash slots     : {HASH_SPACE_SIZE}")
    print(f"Total collisions: {total_collisions}")
    print(f"Unique slots used: {sum(1 for x in hash_table if x)} / {HASH_SPACE_SIZE}")
    print("\nSample chains (slots with collisions):")
    for idx, chain in enumerate(hash_table):
        if len(chain) > 1:
            print(f" Slot #{idx} ({len(chain)} items): {chain}")

if __name__ == "__main__":
    main()
