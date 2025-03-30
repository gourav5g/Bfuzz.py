import requests
import threading
import time
import argparse
import os

class BFuzz:
    def __init__(self, url, wordlist, threads, delay):
        self.url = url
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay
        self.lock = threading.Lock()
        self.results = []

    def request(self, word):
        try:
            response = requests.get(self.url.replace("FUZZ", word))
            if response.status_code == 200:
                with self.lock:
                    print(f"[+] Found: {self.url.replace('FUZZ', word)}")
                    self.results.append(self.url.replace("FUZZ", word))
            elif response.status_code == 404:
                pass  # Not found, ignore
        except requests.exceptions.RequestException as e:
            print(f"[-] Error: {e}")

    def run(self):
        with open(self.wordlist, 'r') as f:
            words = f.read().splitlines()

        threads = []
        for word in words:
            t = threading.Thread(target=self.request, args=(word,))
            threads.append(t)
            t.start()
            time.sleep(self.delay)  # Rate limiting

            if len(threads) >= self.threads:
                for t in threads:
                    t.join()
                threads = []

        # Join remaining threads
        for t in threads:
            t.join()

        # Save results to a file
        with open("results.txt", "w") as result_file:
            for result in self.results:
                result_file.write(result + "\n")

def main():
    parser = argparse.ArgumentParser(description="bfu\\zz - Directory Brute Forcing Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL with FUZZ placeholder")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use")
    parser.add_argument("-d", "--delay", type=float, default=0.5, help="Delay between requests in seconds")
    
    args = parser.parse_args()

    if not os.path.isfile(args.wordlist):
        print("[-] Wordlist file does not exist.")
        return

    bfuzz = BFuzz(args.url, args.wordlist, args.threads, args.delay)
    bfuzz.run()

if __name__ == "__main__":
    main()