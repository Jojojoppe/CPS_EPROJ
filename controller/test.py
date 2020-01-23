import time

now = time.time() 
x = 0
while True:
    t = time.time() - now
    if t > 1:
        break
    x += 1

print(x)

