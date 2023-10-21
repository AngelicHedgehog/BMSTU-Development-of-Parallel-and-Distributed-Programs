from mpi4py import MPI

comm = MPI.COMM_WORLD
worker = comm.Get_rank()
size = comm.Get_size()
# print(worker, size)
if worker != 0:
    # print(worker)
    i = comm.recv(source=0)
    comm.send(i + 5, dest=0)
else:
    reqs = []
    reqr = []
    for i in range(size):
        reqs.append(comm.isend(i, dest=i))
        reqr.append(comm.irecv(source=i))
    res = []
    for i in range(size):
        reqs[i].wait()
        # reqs[i].Free()
        res.append(reqr[i].wait())
        # reqr[i].Free()
    print(res)

    reqs, reqr = [], []
    for i in range(size):
        reqs[i] = comm.isend(res[i], dest=i)
        reqr[i] = comm.irecv(source=i)

    # print(dir(reqs[0]))
    for i in range(size):
        reqs[i].wait()
        res[i] = reqr[i].wait()

    print(res)
