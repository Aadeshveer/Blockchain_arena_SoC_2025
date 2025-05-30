# Blockchain_arena_SoC_2025

**Name:** Aadeshveer Singh  
**Roll no:** 24B0926  
**github id:** Aadeshveer 

## P2P Network Generator - Assignment 1

This project implements a program to generate and visualize a connected Peer-to-Peer (P2P) network with specific peer degree constraints (each peer connected to 3-6 other peers, with the total number of peers between 50 and 100). This work is part of Assignment 1 for the "Blockchain Arena: Simulating Mining Wars and Network Attacks" project.

## How to Run

1.  **Prerequisites:**
    *   Python 3.x
    *   Required libraries: `numpy`, `networkx`, `matplotlib`
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Aadeshveer/Blockchain_arena_SoC_2025.git
    cd Blockchain_arena_SoC_2025
    ```
3.  **Install Dependencies:**
    ```bash
    pip install numpy networkx matplotlib
    ```
4.  **Execute the Script:**
    ```bash
    python3 main.py 
    ```
5.  **Output:**
    *   The script will print degree validation messages and a degree distribution summary to the console.
    *   The generated network graph will be saved as `network.png` in the root of the project directory.

## Key Features

-   **Random Network Generation:** Creates a P2P network with a random number of peers (50-100).
-   **Degree Constraints:** Enforces that each peer has a degree between 3 and 6 (inclusive).
-   **Guaranteed Connectivity:** Ensures the entire network is a single connected component (verified using NetworkX's `is_connected`, which typically uses BFS/DFS).
-   **Validation & Regeneration:** If the generated graph does not meet all constraints (connectivity or degree), it is discarded, and a new graph is generated until a valid one is produced.
-   **Visualization:** Outputs a visual representation of the generated network graph.
-   **Degree Distribution:** Prints a summary of the degree distribution of the final valid network.