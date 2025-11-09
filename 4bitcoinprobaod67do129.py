import random
import time
import sys
import urllib.request
import multiprocessing
from urllib.error import URLError
import psutil
import os
from bit import Key, MultiSig
from bit.format import bytes_to_wif
from rich.console import Console
import threading

# Kolory terminala
W  = '\033[0m'
R  = '\033[31m'
G  = '\033[32m'
O  = '\033[33m'
B  = '\033[34m'
P  = '\033[35m'
my_colours = [W, R, G, O, B, P]

console = Console()

# =======================
# Wczytywanie adresów (ignorowanie salda)
def load_addresses():
    addresses = set()
    with open('adresy.txt', 'r') as file:
        for line in file:
            parts = line.strip().split()  # Dzielimy linię na części
            if parts:  # Sprawdzamy, czy linia nie jest pusta
                address = parts[0]  # Pierwszy element to adres
                if address.startswith(('1', '3', 'bc1')):  # Tylko Bitcoinowe adresy
                    addresses.add(address)
    print(f"Loaded {len(addresses)} Bitcoin addresses from 'adresy.txt'.")
    return addresses

# =======================
# Generowanie adresu z nieregularnymi skokami
def jump_generator(start, stop, jump_range):
    position = random.randint(start, stop)
    while True:
        offset = int(jump_range * random.uniform(0.9, 1.1))  # Nieregularne skoki o ok. 9.57%
        position = (position + offset) % (stop - start) + start
        yield position

# =======================
# Funkcja sprawdzająca salda
def get_balance(address):
    url = f"https://blockchain.info/q/getreceivedbyaddress/{address}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        response = urllib.request.urlopen(url, timeout=10)  # Ustawiamy timeout na 10 sekund
        return int(response.read().decode('utf-8').strip())
    except URLError as e:
        print(f"Error with URL: {e}")
        return 0
    except Exception as e:
        print(f"General error: {e}")
        return 0

# =======================
# Worker dla multiprocessing
def worker(a, b, target_addresses, process_id, found_addresses, total_checked):
    local_counter = 0
    proc = psutil.Process(os.getpid())
    jump_range = (b - a) // 10  # Skok na 9.57% w całym zakresie
    key_gen = jump_generator(a, b, jump_range)

    while True:
        local_counter += 1
        total_checked.value += 5  # Zwiększamy wspólny licznik
        rand_int = next(key_gen)
        key = Key.from_int(rand_int)
        wif = bytes_to_wif(key.to_bytes(), compressed=False)
        wif1 = bytes_to_wif(key.to_bytes(), compressed=True)
        key1 = Key(wif)

        caddr = key.address
        uaddr = key1.address
        saddr = key.segwit_address
        multisig = MultiSig(key, {key.public_key, key1.public_key}, 2)
        multi_addr = multisig.address

        # Sprawdzamy, czy adresy są już sprawdzone
        if uaddr in found_addresses or caddr in found_addresses or saddr in found_addresses or multi_addr in found_addresses:
            continue  # Pomijamy, jeśli adres już był sprawdzony

        # Sprawdzanie salda
        balance = 0
        for addr in [uaddr, caddr, saddr, multi_addr]:
            balance += get_balance(addr)

        # Jeśli saldo jest większe niż 1 000 000 satoshi (1 BTC)
        if balance >= 1000000:
            console.print(f"[red]Found address with balance![/red] [Thread {process_id}]")
            with open("winner.txt", "a") as f:
                f.write(f"\nPrivate Key (WIF): {wif}\nPrivate Key (HEX): {key.to_hex()}\n")
                f.write(f"Addresses:\n{caddr} - Total Received: {balance} satoshi\n")
                f.write(f"{uaddr} - Total Received: {balance} satoshi\n")
                f.write(f"{saddr} - Total Received: {balance} satoshi\n")
                f.write(f"{multi_addr} - Total Received: {balance} satoshi\n")
                f.write(f"Balance: {balance}\n{'='*50}\n")

            # Zapisujemy adresy do zbioru 'found_addresses'
            found_addresses.append(caddr)
            found_addresses.append(uaddr)
            found_addresses.append(saddr)
            found_addresses.append(multi_addr)

        if local_counter % 5000 == 0:
            print(f"[Process {process_id}] Checked: {local_counter} | Total Checked: {total_checked.value}")

# =======================
# Niezależny licznik w osobnym wątku
def print_counter(total_checked):
    while True:
        print(f"Total Addresses Checked: {total_checked.value}", end='\r')
        time.sleep(1)  # Aktualizacja licznika co 1 sekundę

# =======================
# Uruchomienie wieloprocesowego przetwarzania
if __name__ == '__main__':
    addresses = load_addresses()  # Ładowanie adresów
    print(f"Total Bitcoin Addresses Loaded: {len(addresses)}")

    start_bit = int(input("Start range in BITs (Start Number) -> "))
    end_bit = int(input("Stop range Max in BITs (End Number) -> "))
    a = 2**start_bit
    b = 2**end_bit

    print(f"Starting search in range: {a} to {b}")
    
    # Multiprocessing
    manager = multiprocessing.Manager()
    found_addresses = manager.list()  # Zbiór jako lista, aby przechowywać sprawdzone adresy
    total_checked = manager.Value('i', 0)  # Licznik ogólny sprawdzonych adresów
    processes = []

    # Uruchomienie wątku do wyświetlania licznika
    counter_thread = threading.Thread(target=print_counter, args=(total_checked,))
    counter_thread.daemon = True
    counter_thread.start()

    # Uruchomienie procesów
    for process_id in range(15):
        p = multiprocessing.Process(target=worker, args=(a, b, addresses, process_id, found_addresses, total_checked))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"Total addresses checked: {total_checked.value}")
