# 🧠 Bitcoin Address Space Scanner (Parallelized Key Search)

This Python script performs a **parallelized exploration of the Bitcoin private key space**, generating random private keys and checking whether the corresponding addresses hold any balance on the blockchain.

It uses **multi-processing**, **threaded counters**, **randomized jump generation**, and **real-time network lookups** to search efficiently across the enormous 2²⁵⁶ key space.

> ⚠️ **Educational & research use only.**  
> This tool demonstrates the mechanics of Bitcoin key generation, address derivation, and balance lookup — **not** brute-force feasibility.

---

## ⚙️ Features

✅ Multi-processing — launches multiple independent processes for parallel key generation  
✅ Threaded progress counter — real-time address scanning statistics  
✅ Random jump generator — non-linear traversal of key space  
✅ Balance checking — live lookups from blockchain explorers  
✅ Multiple address formats per key:
   - Legacy (1...)
   - Compressed (1...)
   - SegWit (bc1...)
   - MultiSig (3...)  
✅ Automatic logging of “found” keys with balance into `winner.txt`

---

## 🧩 How It Works

1. **Loads Bitcoin addresses** from `adresy.txt` — the input list of potential target addresses.  
2. **Generates random private keys** across a specified bit range using a custom jump generator.  
3. **Derives all major address types** from each private key:
   - Uncompressed legacy address  
   - Compressed legacy address  
   - SegWit address  
   - MultiSig address  
4. **Checks balances** using public blockchain APIs (`blockchain.info`).  
5. If any address holds ≥ 1,000,000 satoshi (0.01 BTC), the script:
   - Prints an alert in red  
   - Logs private key and addresses to `winner.txt`  
   - Tracks found addresses to avoid repetition.  

---

## 🧮 Input File Format (`adresy.txt`)

A text file containing one Bitcoin address per line, e.g.:

1BoatSLRHtKNngkdXEeobR76b53LETtpyT
3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080


Only addresses starting with `1`, `3`, or `bc1` are considered valid.

---

## 🚀 Usage

### 1️⃣ Install dependencies

```bash
pip install bit psutil rich

2️⃣ Prepare adresy.txt

Place all Bitcoin addresses you want to monitor in the file adresy.txt (one per line).

3️⃣ Run the scanner
python3 scanner.py

4️⃣ Set key range

When prompted, enter your desired bit range for the search:

Start range in BITs (Start Number) -> 32
Stop range Max in BITs (End Number) -> 36


This scans keys between 2^32 and 2^36.

5️⃣ Monitor progress

The console displays:

Total addresses checked (live)

Per-process progress

Alerts for found addresses

Example output:

Loaded 12000 Bitcoin addresses from 'adresy.txt'.
Starting search in range: 4294967296 to 68719476736
[Process 3] Checked: 5000 | Total Checked: 75000
[red]Found address with balance![/red] [Thread 8]
Private Key (WIF): 5J4Gg...kYhF
Addresses:
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa - Total Received: 50000000 satoshi
==================================================

🧰 Technical Details
Component	Description
load_addresses()	Loads Bitcoin addresses from adresy.txt
jump_generator()	Produces randomized jumps to traverse key space non-linearly
get_balance()	Queries the blockchain API for total received balance
worker()	Main multiprocessing worker that generates and checks addresses
print_counter()	Displays global progress via threading
found_addresses	Shared list of addresses found with balances
winner.txt	Output log containing found private keys and addresses
⚙️ Configuration Parameters
Parameter	Description
processes = 15	Number of parallel processes (CPU cores)
jump_range	Jump interval for random key traversal
timeout = 10	Timeout for API requests
balance_threshold = 1000000	Minimum satoshi balance to trigger logging
📄 Output Files
File	Purpose
winner.txt	Stores found private keys and addresses with balance
adresy.txt	Input file containing target addresses
🧠 Example Logic Flow
adresy.txt  ──►  load_addresses()
       │
       ▼
  random key generation (jump_generator)
       │
       ▼
 derive addresses → check balances → if balance > threshold:
       │
       ▼
     log to winner.txt

⚠️ Security & Ethical Use

⚠️ This tool is provided for educational and research use only.
It demonstrates Bitcoin key generation, encoding, and address verification principles.
Attempting to brute-force real Bitcoin addresses is computationally infeasible and illegal when targeting third-party wallets.

Use it only for:

Educational research

Security experiments on your own wallets

Teaching blockchain fundamentals
BTC donation address: bc1q4nyq7kr4nwq6zw35pg0zl0k9jmdmtmadlfvqhr
