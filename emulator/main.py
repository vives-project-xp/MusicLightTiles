from tile import Tile
import multiprocessing

if __name__ == '__main__':
  # Request user input
  amount = int(input("How many tiles do you want to create? "))

  # Create a list of tiles
  tiles = [Tile(f"Tile{i+1}") for i in range(amount)]

  # Create a stop event to signal child processes to exit
  stop_event = multiprocessing.Event()

  # Create a list of processes
  processes: list[multiprocessing.Process] = []
  for tile in tiles:
    process = multiprocessing.Process(target=tile.run)
    processes.append(process)

  # Start all processes
  for process in processes:
    process.start()

  # Wait for user input (Enter key) to stop the program
  try:
    # Wait for user input (Enter key)
    input("Press enter to stop the program")
  except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    pass
  finally:
    # Set the stop_event to signal child processes to exit
    stop_event.set()

  # Join all processes to ensure they have finished
  for process in processes:
    process.join()
  
