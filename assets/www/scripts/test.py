import sys
import signal
TIMEOUT = 1 # seconds
signal.signal(signal.SIGALRM, input)
signal.alarm(TIMEOUT)

try:
    for line in sys.stdin:
        argval = line.split('=')
        farenheit = float(argval[1])*9/5.0+32
        print(farenheit)
except:
    ignorar = True


for line in sys.argv:
    argval = line.split('=')
    if(len(argval) > 1):
        print("Hola "+argval[1]+"!")
