import random
import string
import time

# --- Configuration ---
# M: The size of the finite hash space (the 'Pigeonholes'). 
# We are intentionally keeping this very small (e.g., 100) to force a collision.
HASH_SPACE_SIZE = 100 

# N: The number of inputs (the 'Pigeons').
# N must be greater than M to guarantee at least one collision (Pigeonhole Principle).
NUM_INPUTS = 150 # N > M, guaranteeing at least 50 collisions (150 inputs - 100 unique slots)

# Length of random strings to generate
INPUT_LENGTH = 8 

def simple_non_crypto_hash(input_string, space_size):
    """
    A simple, non-cryptographic hash function designed only for demonstration.
    It takes a string and maps it to a small integer within the defined space.
    
    This function demonstrates the 'loss of information' inherent in hashing, 
    as many different input strings will inevitably map to the same small output.
    """
    hash_value = 0
    # Sum the ASCII values of the characters
    for char in input_string:
        hash_value += ord(char)
    
    # Use the modulo operator to constrain the hash output to the fixed space size (M)
    return hash_value % space_size

def generate_random_input(length):
    """Generates a random string of a given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def run_demonstration():
    """Runs the collision demonstration and reports the findings."""
    print("--- Cryptographic Hash Collision Demonstrator ---")
    print(f"1. Hash Space Size (M: Pigeonholes): {HASH_SPACE_SIZE} (Possible outputs: 0 to {HASH_SPACE_SIZE - 1})")
    print(f"2. Number of Inputs (N: Pigeons):    {NUM_INPUTS}")
    print("\nSince N > M, a collision is guaranteed by the Pigeonhole Principle.")
    print("-" * 50)
    
    # Store the generated inputs and their corresponding hash values
    hash_map = {} # Key: hash_value (pigeonhole), Value: list of input_strings (pigeons)
    total_collisions_found = 0
    first_collision = None

    # Step 1: Generate Inputs and Calculate Hashes
    print(f"Generating {NUM_INPUTS} inputs and calculating their hashes...")
    start_time = time.time()
    
    for i in range(NUM_INPUTS):
        input_data = generate_random_input(INPUT_LENGTH)
        hash_output = simple_non_crypto_hash(input_data, HASH_SPACE_SIZE)
        
        # Check for a collision before adding the data
        if hash_output in hash_map:
            # Collision detected!
            if len(hash_map[hash_output]) == 1:
                 # This is the moment the hash slot went from 1 input to 2
                total_collisions_found += 1
                if first_collision is None:
                    first_collision = {
                        'hash': hash_output,
                        'inputs': hash_map[hash_output] + [input_data]
                    }
            elif len(hash_map[hash_output]) > 1:
                # If there are already multiple inputs, it's an additional collision
                total_collisions_found += 1
                
            hash_map[hash_output].append(input_data)
        else:
            # First time seeing this hash output
            hash_map[hash_output] = [input_data]

    end_time = time.time()
    
    # Step 2: Output Findings
    print(f"Completed in {end_time - start_time:.4f} seconds.")
    print("-" * 50)
    
    print("\n--- Summary of Results ---")
    
    # Find the total number of unique hash slots used
    unique_hashes_used = len(hash_map)
    print(f"Unique Hash Slots Used (M'): {unique_hashes_used}")
    print(f"Total Collisions Found: {total_collisions_found}")
    
    # Step 3: Display the First Collision Found
    if first_collision:
        print("\n<<< GUARANTEED COLLISION DEMONSTRATED >>>")
        print(f"Hash Output (Pigeonhole): {first_collision['hash']}")
        print(f"Input 1: '{first_collision['inputs'][0]}'")
        print(f"Input 2: '{first_collision['inputs'][1]}'")
        print("------------------------------------------------------------------")
        print("These two different inputs (messages) produced the EXACT same hash.")
        print("This is the core concept of a collision, forced by N > M.")
    else:
        print("Error: Could not find a collision, check configuration (N > M).")


if __name__ == "__main__":
    run_demonstration()
