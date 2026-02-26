import sys
from cowsay import cowsay
if len(sys.argv) < 3:
	print("error")
	sys.exit()

print(cowsay(sys.argv[2], sys.argv[1]))
