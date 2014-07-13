#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
	MPI_Init(&argc, &argv);
	if (argc != 2) {
		return -1;
	}

	int target = atoi(argv[1]);

	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Request r;
	int d;
	if (rank == 0) {
		MPI_Send(&d, 1, MPI_INT, target, 10, MPI_COMM_WORLD);
	}
	if (rank == 1) {
		MPI_Recv(&d, 1, MPI_INT, 0, 10, MPI_COMM_WORLD);
	}
	MPI_Finalize();
	return 0;
}
