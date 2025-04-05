import time
import itertools

directions = ['N', 'E', 'S','W']

running = True
timealgo = 5
timer = timealgo

while running:

    for green_directions in directions:
        print("traffic signal status")

        for direction in directions:
            signal = '0' if direction == green_directions else '1'

            print(f"{direction}: {signal}")

        time.sleep(timealgo)







