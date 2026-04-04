from time import sleep
from multiprocessing import Process, freeze_support, Queue
from console import main

def backend():
    for i in range(10):
        print(2)
        sleep(1)

if __name__ == "__main__":
    freeze_support()

    q_in = Queue()
    q_out = Queue()
    p = Process(target=main, args=(q_out, q_in,))
    p.start()

    while True:
        if not q_out.empty():
            message = q_out.get()
            if message[0][0] == "input":
                user_input = input(message[0][1])
                if user_input == "exit()":
                    p.terminate()
                    break
                q_in.put(user_input)
            else:
                print(message)