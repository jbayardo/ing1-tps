#include <stdio.h>
#include <stdlib.h>

using namespace std;

int main(int argc, char* argv[]) {

	if (argc != 5) {
		printf("%s top left right bottom\n", argv[0]);
		return 0;
	}

	int top    = atoi(argv[1]);  
	int left   = atoi(argv[2]);  
	int right  = atoi(argv[3]);  
	int bottom = atoi(argv[4]);

	printf("points=[");

	if (top == 1) {
		printf("[0.5,0],");
	} else {
		// top
		for (int i = 0; i < top; ++i) {
			printf("[%4.3f,0],", 1.0/(top-1)*i);
		}
	}

	if (left == 1) {
		printf("[0,0.5],");
	} else {
		// left
		for (int i = 0; i < left; ++i) {
			printf("[0,%4.3f],", 1.0/(left-1)*i);
		}
	}

	if (right == 1) {
		printf("[1,0.5],");
	} else {
		// right
		for (int i = 0; i < right; ++i) {
			printf("[1,%4.3f],", 1.0/(right-1)*i);
		}
	}

	if (bottom == 1) {
		printf("[0.5,1],");
	} else {
		// bottom
		for (int i = 0; i < bottom; ++i) {
			printf("[%4.3f,1],", 1.0/(bottom-1)*i);
		}
	}

	printf("]\n");

	return 0;

}