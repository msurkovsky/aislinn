#include <mpi.h>
#include <stdio.h>
#include <string.h>
 
int main(int argc, char *argv[])
{
	int rank;
	MPI_Status status;
 
	MPI_Init(&argc, &argv);

	MPI_Datatype type;
	MPI_Type_contiguous(2, MPI_INT, &type);

 
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	if (rank == 0)
	{
		int buffer[1000];
		for (int i = 0; i < 1000; i++) {
			buffer[i] = i;
		}
		// 2 * (6x int + 5x space)
		MPI_Datatype vtype;
		MPI_Type_hvector(2, 3, 5 * sizeof(int) * 2, type, &vtype);
		MPI_Type_commit(&vtype);

		MPI_Send(buffer, 4, vtype, 1, 123, MPI_COMM_WORLD);
		MPI_Send(buffer, 4, vtype, 1, 123, MPI_COMM_WORLD);
	}
	else if (rank == 1)
	{
		int buffer1[1000], buffer2[1000];
		for (int i = 0; i < 1000; i++) {
			buffer1[i] = -1;
			buffer2[i] = -1;
		}
		MPI_Recv(buffer1, 48, MPI_INT, 0, 123, MPI_COMM_WORLD, &status);
		for (int i = 0; i < 50; i++) {
			printf("%i ", buffer1[i]);
		}
		printf("\n");

		MPI_Datatype vtype;
		MPI_Type_hvector(4, 6, 7 * sizeof(int), MPI_INT, &vtype);
		MPI_Type_commit(&vtype);

		MPI_Recv(buffer2, 2, vtype, 0, 123, MPI_COMM_WORLD, &status);
		for (int i = 0; i < 50; i++) {
			printf("%i ", buffer2[i]);
		}
		printf("\n");
	}
 
	MPI_Finalize();
	return 0;
}
