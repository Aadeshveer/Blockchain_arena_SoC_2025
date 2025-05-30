# Blockchain_arena_SoC_2025

## P2P Network Generator 

This project implements a program to generate and visualize a connected P2P network with specific peer degree constraints, as per Assignment 1 of the "Blockchain Arena: Simulating Mining Wars and Network Attacks" project.

## How to Run
1.  Clone the repository.
2.  Ensure Python 3 is installed along with the required libraries:
    ```bash
    pip install numpy networkx matplotlib
    ```
3.  Execute the main script:
    ```bash
    python main.py 
    ```
4.  The generated network graph will be saved as `network.png`.

## Key Features
- Generates a random P2P network (50-100 peers).
- Enforces peer degree constraints (3-6 connections).
- Ensures the entire network is connected using BFS/DFS.
- Visualizes the network.
