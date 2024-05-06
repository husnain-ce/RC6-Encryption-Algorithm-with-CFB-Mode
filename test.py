import atheris
import sys
import numpy as np

@atheris.instrument_func
def test_numpy_solve(data):
    fdp = atheris.FuzzedDataProvider(data)
    
    n = fdp.ConsumeIntInRange(1, 5)  # Limit the size of matrices to a maximum dimension of 5
    
    # Generate two square matrices, A and B, of size n x n
    try:
        A = np.array([fdp.ConsumeFloat() for _ in range(n * n)]).reshape(n, n)
        B = np.array([fdp.ConsumeFloat() for _ in range(n * n)]).reshape(n, n)
    except atheris.BufferTooSmallError:
        return

    try:
        x = np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        pass  # Ignore singular matrix errors

def main():
    atheris.Setup(sys.argv, test_numpy_solve)
    atheris.Fuzz()

if __name__ == "__main__":
    main()