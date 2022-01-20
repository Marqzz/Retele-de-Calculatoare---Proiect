#include <stdio.h>
#include <iostream>
#include "Header.h"
#include <list>
#include <algorithm>
using namespace std;

binaryTree* createNode(int x)
{
	binaryTree *b=new binaryTree;
	b->data = x;
	b->left = NULL;
	b->right = NULL;
	return b;
}
int lep(int x[], int n)
{
	list<binaryTree*> B;
	B.clear();
	int res = 0;
	sort(x, x+n);
	for (int i = 0; i < n; i++)
	{
		binaryTree* nod = createNode(x[i]);
		B.push_back(nod);
	}
	while (B.size() > 1)
	{
		binaryTree* t1 = B.front();
		B.pop_front();
		binaryTree* t2 = B.front();
		B.pop_front();
		binaryTree* t = createNode(t1->data + t2->data);
		if (t1->data <= t2->data)
		{
			t->left = t1;
			t->right = t2;
		}
		else
		{
			t->left = t2;
			t->right = t1;
		}
		res += t->data;
		B.push_front(t);
	}
	return res;
}