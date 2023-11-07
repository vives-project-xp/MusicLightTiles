from tile import Tile
import multiprocessing
import threading
import random
import time

def random_presence_detection(tile: Tile, stop_event: multiprocessing.Event) -> None:
  """Simulates random presence detection."""
  MIN = 1
  MAX = 10
  while not stop_event.is_set():
    # Generate a random number between MIN and MAX
    # 50% chance for presence to be set
    # 50% chance for presence to be reset
    gen = random.randint(MIN, MAX)
    if gen <= MAX / 2:
      tile.set_presence(False)
    if gen > MAX / 2:
      tile.set_presence(True)
    # Sleep for gen seconds
    time.sleep(gen)

def create_and_run_tile(name: str, stop_event: multiprocessing.Event, random_presence: bool = False) -> None:
  """Creates a tile and runs it until the stop_event is set."""
  # TODO: Add random presence detection
  tile = Tile(name)

  if random_presence:
    # Create two threads, one for random presence detection and one to run the tile
    thread1 = threading.Thread(target=random_presence_detection, args=(tile, stop_event))
    thread2 = threading.Thread(target=tile.run, args=(stop_event,))
    # Start the threads
    thread1.start()
    thread2.start()
    # Wait for the threads to finish
    thread1.join()
    thread2.join()
  else:
    tile.run(stop_event)

if __name__ == '__main__':
  # Request user input
  amount = int(input("How many tiles do you want to simulate? "))

  # Create a stop event to signal child processes to exit
  stop_event = multiprocessing.Event()

  # Create a list of processes and start them
  processes: list[multiprocessing.Process] = []
  for i in range(amount):
    process = multiprocessing.Process(target=create_and_run_tile, args=(f"TILE{i+1}", stop_event, True))
    processes.append(process)
    process.start()

  # Wait for user input (Enter key) to stop the program
  try:
    # Wait for user input (Enter key)
    input("Press enter to stop the program")
  except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    pass
  finally:
    print("Stopping program...")
    # Set the stop_event to signal child processes to exit
    stop_event.set()

  # Join all processes to ensure they have finished
  for process in processes:
    process.join()

  # Print a message to indicate the program has stopped
  print("Program stopped")
  
