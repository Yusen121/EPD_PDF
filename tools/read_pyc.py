import dis
import marshal

# Define the path to the .pyc file
pyc_file_path = "/Users/apple/PycharmProjects/EPDLibrary/config/__pycache__/default.cpython-312.pyc"

# Read and disassemble the .pyc file
with open(pyc_file_path, 'rb') as f:
    f.seek(16)  # Skip the .pyc header
    code = marshal.load(f)
    disassembled_code = dis.dis(code)

print(disassembled_code)

