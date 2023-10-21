from mpi4py import MPI

comm = MPI.COMM_WORLD
worker = comm.Get_rank()
size = comm.Get_size()

initial = 2
if (worker == 0):
    print(size)
    comm.send(initial, dest=worker+1)
elif worker == size-1:
    rec = comm.recv(source=worker-1)
    print(rec * 2)
else:
    rec = comm.recv(source=worker-1)
    comm.send(rec*2, dest=worker+1)
    print(worker, rec)
