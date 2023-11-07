from tile import Tile
import multiprocessing

def create_and_run_tile(name: str, stop_event: multiprocessing.Event) -> None:
  """Creates a tile and runs it until the stop_event is set."""
  tile = Tile(name)
  tile.run(stop_event)

if __name__ == '__main__':
  # Request user input
  amount = int(input("How many tiles do you want to create? "))

  # Create a stop event to signal child processes to exit
  stop_event = multiprocessing.Event()

  # Create a list of processes and start them
  processes: list[multiprocessing.Process] = []
  for i in range(amount):
    process = multiprocessing.Process(target=create_and_run_tile, args=(f"TILE{i+1}", stop_event))
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
    # Set the stop_event to signal child processes to exit
    stop_event.set()

  # Join all processes to ensure they have finished
  for process in processes:
    process.join()
  
