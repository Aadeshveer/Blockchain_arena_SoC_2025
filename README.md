# Blockchain Arena: P2P Cryptocurrency Network Simulator (Assignment 2)

**Name:** Aadeshveer Singh  
**Roll no:** 24B0926  
**GitHub:** Aadeshveer  
**SoC 2025 Midterm Checkpoint Submission**

## 1. Project Overview

This project implements a discrete-event simulator for a Peer-to-Peer (P2P) cryptocurrency network based on Proof-of-Work (PoW). The simulation models key aspects including P2P network topology, peer heterogeneity (CPU power and network speed), transaction generation and propagation, PoW mining, block creation and propagation with latencies, and fork resolution using the longest chain rule.

The primary objective is to build a foundational simulator to study the dynamics of blockchain networks, such as block propagation, the formation of forks, proof or work and the overall structure of the blockchain tree as perceived by different peers under various network conditions and parameters. This work corresponds to Assignment 1 and 2 of the "Blockchain Arena: Simulating Mining Wars and Network Attacks" project.

## 2. System Design and Implementation

The simulator is implemented in Python and leverages the `networkx` library for graph operations and `matplotlib` for visualization. The system is designed with a modular approach, comprising the following key classes:

*   **`Transaction` (`src/chain.py`):** Represents a basic transaction with an ID, sender ID (optional for coinbase), receiver ID, and amount.
*   **`Block` (`src/chain.py`):** Represents a block containing an ID, the ID of the previous block in the chain, the creator's ID, and a list of transactions.
*   **`TreeNode` & `BlockTree` (`src/chain.py`):** Each peer maintains its view of the blockchain as a tree of `TreeNode` objects. The `BlockTree` class manages adding blocks, validating transactions against the parent block's account state, finding the longest chain, and visualizing the tree. Account balances are tracked within each `TreeNode` to reflect the state after its block's transactions.
*   **`Peer` (`src/peer.py`):** Represents a node in the P2P network. Each peer:
    *   Has attributes for ID, CPU power (LOW/HIGH), and network speed (SLOW/FAST).
    *   Maintains its own `BlockTree`.
    *   Calculates its hashing fraction based on global CPU power distribution.
    *   Manages a pool of transactions to be included in blocks (`to_process_transactions`).
    *   **Generates new transactions:** Periodically (based on a Poisson distribution with mean `MEAN_TRANSACTION_INTERVAL * SCALE`) if it has a balance.
    *   **Mines new blocks (Proof-of-Work):**
        *   Selects transactions for a new block (up to 1000 or max block size).
        *   Includes a coinbase transaction rewarding itself `MINING_FEE`.
        *   Mining time is drawn from a Poisson distribution with mean `(target_block_interval * SCALE) / hashing_fraction_of_peer`.
        *   If a new, longer valid chain is received while mining, the peer switches to mining on top of the new longest chain tip.
    *   Keeps track of seen transaction and block IDs to prevent redundant processing/forwarding.
*   **`Network` (`src/network.py`):**
    *   Initializes the P2P network topology using the generator from Assignment 1 (random number of peers between 50-100, degree 3-6, ensured connectivity).
    *   Assigns CPU power and network speed attributes to peers.
    *   Calculates and assigns hashing power fractions to peers.
    *   Initializes and calculates message latencies between connected peers based on propagation delay, link speed (100 Mbps for FAST-FAST links, 5 Mbps otherwise), message size (1KB per transaction + 1KB block overhead), and a Poisson-distributed queuing delay.
    *   Provides a method to visualize the P2P network topology.
*   **`Event` & `DiscreteEventSimulator` (`src/main.py`):**
    *   The `Event` class encapsulates event details (type, peer, message, time).
    *   The `DiscreteEventSimulator` manages the main simulation loop:
        *   Maintains a global simulation `time`.
        *   Uses a FIFO queue (`queue.Queue`) for events scheduled for the *current* time step, and a `future_event_queue` for events scheduled for later times.
        *   In each time step:
            1.  Allows each peer to perform operations: attempt to mine (decrementing mining timer or starting new mining if current block is stale) and attempt to generate a new transaction (decrementing transaction timer). These can generate `BLOCK_SEND` or `TRANSACTION_SEND` events for the current time.
            2.  Processes all events in the current time step's queue:
                *   `BLOCK_SEND` / `TRANSACTION_SEND`: Schedules `_RECIEVE` events for all neighbors with calculated latency.
                *   `BLOCK_RECIEVE` / `TRANSACTION_RECIEVE`: If message not seen, peer processes it (e.g., adds block to tree if valid, adds transaction to pool) and then re-schedules a `_SEND` event to propagate it further.
        *   Periodically saves a visualization of Peer 0's blockchain tree.

## 3. How to Run the Simulation

1.  **Prerequisites:**
    *   Python 3.x
    *   Required libraries: `numpy`, `networkx`, `matplotlib`, `scipy`
        ```bash
        pip install numpy networkx matplotlib scipy
        ```
2.  **Clone the Repository:**
    ```bash
    git clone [URL_OF_YOUR_REPO]
    cd [REPO_DIRECTORY_NAME]
    ```
3.  Execution:

    a. **Execute the Powershell(for Windows) Script:**
        The simplest way to run is using the powershell script run.ps1 for Windows users. It runs the simulator for 4 mean intervals [5, 10, 50, 100] and for 3 mean transaction times [1, 5, 10]. These can be changed in script itself.  
        ```powershell
            .\run.ps1
        ```

    b. **Execute the Bash(for linux or mac) Script:**
        The simplest way to run is using the Bash script run.sh for Windows users. It runs the simulator for 4 mean intervals [5, 10, 50, 100] and for 3 mean transaction times [1, 5, 10]. These can be changed in script itself.  
        ```bash
            .\run.sh
        ```

    c. **Execute the Python Script:**
        The simulation is run via `src/main.py`. It takes four command-line arguments:
        ```bash
        python3 src/main.py <num_peers> <slow_network_percentage> <low_cpu_percentage> <mean_block_interval> <mean_transaction_interval> <logging(T/F)>
        ```
    *   `<num_peers>`: Integer, number of peers in the network (50-100).
    *   `<slow_network_percentage>`: Integer, percentage of peers with slow network speed (0-100).
    *   `<low_cpu_percentage>`: Integer, percentage of peers with low CPU power (0-100).
    *   `<mean_block_interval>`: Integer, target mean interval for block mining across the entire network (e.g., 60 for a target of 60 seconds, which becomes `60 * SCALE` simulation ticks).
    *   `<mean_transaction_interval>`: Integer, target mean interval for transaction generation for each peer (e.g., 10 for a target of 10 seconds, which becomes `10 * SCALE` simulation ticks).
    *   `<logging(T/F)>`: T or F to turn on or off logging. Note that logging slows the program significantly. Hence the scripts run the program without logging

    **Example:**
    ```bash
    python3 src/main.py 80 50 50 60 10
    ```
    This will run a simulation with 80 peers, 50% having slow network, 50% having low CPU, and a target mean block interval of 60 (scaled by `SCALE=10` in simulation ticks for mining).  
    **Note:** More hyperparameters can be changed by altering settings.py and running again.

4.  **Output:**
    *   The script will print "Checking degree" messages during initial P2P network generation.
    *   During the simulation, it will print "Processing for time X" every 20,000 time steps.
    *   A visualization of the P2P network topology (`results_{mining_interval}_{transaction_interval}/network.png`) is saved at the beginning.
    *   Visualizations of Peer 0's blockchain tree (`results_{mining_interval}_{transaction_interval}/blockchain<timestamp_multiple>.png`) are saved periodically.
    *   Data logging for quantitative analysis as per assignment - e.g., block arrival times per peer to CSV files in the `results` directory.

## 4. Observations and Preliminary Results (Based on a sample run)


A sample simulation was run with the following parameters:
*   Number of Peers: 80
*   Percentage of Slow Network Peers: 50%
*   Percentage of Low CPU Peers: 50%
*   Target Mean Block Interval: 10 (scaled by `SCALE=10` to 100 simulation ticks for network-wide average)
*   Target Mean Transaction Interval: 1 (scaled by `SCALE=10` to 10 simulation ticks for peer)
*   Simulation Duration: 200,000 time steps
*   Non logfile as log files can go upto 1GB in space.

**Key Observations:**

1.  **P2P Network Topology:**
    *   The generated P2P network (Figure 1) shows a connected graph with the specified peer heterogeneity. Nodes are colored based on CPU power, and outline thickness indicates network speed, while edge thickness indicates link capacity.
    ![network](.\results_10_1\network.png) 
    *Figure 1: Sample P2P Network Topology (60 peers, 50% slow network, 50% low CPU).*

2.  **Blockchain Tree Evolution (Peer 0):**
    *   The evolution of Peer 0's blockchain tree over 200,000 time steps was visualized periodically (Figures 2.1 - 2.11).
    *   **Initial Growth:** The chain starts from the Genesis(Figure: 2.1) block and grows linearly initially as blocks are mined and propagated. (Example: Figure 2.2 showing early blocks).
    *   **Fork Formation:** As the simulation progresses and multiple peers mine blocks concurrently, forks naturally occur. This is evident when a block has multiple children, representing competing chains (Example: Figure 2.3 showing a small fork).
    *   **Fork Resolution (Longest Chain Rule):** The simulation demonstrates peers adopting the longest valid chain they are aware of. Over time, one chain typically becomes dominant, and branches that were temporarily extended become stale/orphaned from the perspective of peers on the new longest chain. (Example: Figure 2.3 showing a previously shorter branch now being the longest, or a significant orphan branch).
    *   **Structure of the Final Tree:** The final observed tree for Peer 0 often shows a clear main chain with several smaller, orphaned side branches of varying lengths. This reflects the probabilistic nature of PoW mining and network propagation delays. (Example: Figure 2.11 - your final tree image).

    ![blockchain0](.\results_10_1\blockchain0.png) 
    *Figure 2.1: Initial blockchain for peer 0*
    ![blockchain1](.\results_10_1\blockchain1.png) 
    *Figure 2.2:  blockchain for peer 0*
    ![blockchain2](.\results_10_1\blockchain2.png) 
    *Figure 2.3:  blockchain for peer 0*
    ![blockchain3](.\results_10_1\blockchain3.png) 
    *Figure 2.4:  blockchain for peer 0*
    ![blockchain4](.\results_10_1\blockchain4.png) 
    *Figure 2.5:  blockchain for peer 0*
    ![blockchain5](.\results_10_1\blockchain5.png) 
    *Figure 2.6:  blockchain for peer 0*
    ![blockchain6](.\results_10_1\blockchain6.png) 
    *Figure 2.7:  blockchain for peer 0*
    ![blockchain7](.\results_10_1\blockchain7.png) 
    *Figure 2.8:  blockchain for peer 0*
    ![blockchain8](.\results_10_1\blockchain8.png) 
    *Figure 2.9:  blockchain for peer 0*
    ![blockchain9](.\results_10_1\blockchain9.png) 
    *Figure 2.10:  blockchain for peer 0*
    ![blockchain10](.\results_10_1\blockchain10.png) 
    *Figure 2.11:  blockchain for peer 0*


3.  **Qualitative Observations on Forks:**
    *   Forks appear to be more frequent when network latencies are higher or when hashing power is more evenly distributed (making it more likely for multiple peers to find blocks around the same time).
    *   Longer forks (e.g., forks of depth 2 or more) are less common than short, depth-1 forks, which often resolve quickly.

## 5. Analysis and Answers to Assignment Questions

The assignment requires studying the blockchain tree with different parameters and analyzing:
1.  **The ratio of the number of blocks in the longest chain to the total number of blocks generated in the network.**  
The ratio of number of blocks in longest chain to total generated blocks is very high. The ratio increses as the interval increases because the probabilty of a node generating a block before it recieves the last block keeps going down.
2.  **The number of branches in the blockchain tree and their lengths.**  
The number of branches significantly falls with higher interval periods. With their lengths being usually 1 and rarely 2(in low mining interval cases).
3.  **The effect of different parameters (number of peers, slow/fast peers, low/high CPU peers, block interval) on these metrics.**  
Number of peers affect the calculation duration and how long it takes for a message to transverse the system, hence more peers may lead to more branching. It is observable that mostly it is high CPU power peers that generate blocks and fast network speeds allow them to push their blocks before others.

## 6. Challenges and Future Work

**Challenges Encountered:**
*   Implementing the discrete-event simulation logic, especially managing event timings and interactions between peer mining, block creation, and network propagation, was complex.
*   Debugging race conditions or logical errors in fork resolution and chain selection.
*   Efficiently managing and visualizing the growing blockchain tree data for each peer.
*   Preventing infinite loops.
*   Setting up a robust experimental framework for running multiple simulations and collecting/analyzing data systematically.

## 7. Conclusion

This P2P cryptocurrency network simulator provides a functional foundation for exploring Proof-of-Work blockchain dynamics. The current implementation successfully models peer heterogeneity, network latencies, transaction and block propagation, PoW mining, and fork resolution via the longest chain rule. Preliminary observations from sample runs demonstrate the characteristic growth and forking behavior of decentralized ledgers. Further experimentation as outlined will provide quantitative insights into the system's performance under varied conditions. This project has been a significant learning experience in discrete-event simulation, P2P systems, and core blockchain concepts.

---