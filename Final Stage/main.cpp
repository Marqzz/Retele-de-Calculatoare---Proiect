#include "Header.h"

int main() {
	nodeBTree* root = nullptr;
	creeazaBarbore(root);
	insereazaBarbore(root, 3);
	insereazaBarbore(root, 4);
	insereazaBarbore(root, 2);
	insereazaBarbore(root, 99);

	for (int i = 0; i < root->nrChei; i++) {
		cout << root->cheie[i] << endl;
	}

	system("PAUSE");
	return 0;
}