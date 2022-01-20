package com.codewithmarco;

public class Matrix {

    private int[][] matrix;

    public Matrix(){
        matrix = new int[0][0];
    }

    public Matrix(int dim){
        matrix = new int[dim][dim];
    }

    public Matrix adunare(Matrix a){
        Matrix rez = new Matrix(this.matrix.length);

        for(int i=0;i<this.matrix.length;i++){
            for(int j=0;j<this.matrix[i].length;j++){
                rez.matrix[i][j] = this.matrix[i][j] + a.matrix[i][j];
            }
        }

        return rez;
    }

    @Override
    public String toString(){
        String rez = new String();

        for(int i=0;i<this.matrix.length;i++){
            for(int j=0;j<this.matrix[i].length;j++){
                rez += this.matrix[i][j]+" ";
            }
            rez+="\n";
        }
        return rez;
    }

    public Matrix inmultire(Matrix a){
        Matrix rez = new Matrix(this.matrix.length);

        for(int i=0;i<this.matrix.length;i++){
            for(int j=0;j<a.matrix.length;j++){
                for(int k=0;k<a.matrix[i].length;k++){
                    rez.matrix[i][j] += this.matrix[i][k] * a.matrix[k][j];
                }
            }
        }

        return rez;
    }

    public static void main(String[] args) {
        Matrix a = new Matrix();
        Matrix b = new Matrix(3);
        Matrix c = new Matrix(3);
        b.matrix = new int[][]{{1, 1, 2},
                {2, 2, 3},
                {3, 3, 4}};
        System.out.println("b=\n"+b.toString());
        c.matrix = new int[][]{{0, 0, 1},
                {4, 4, 5},
                {5, 5, 6}};
        System.out.println("c=\n"+c.toString());
        System.out.println("adun b+c=\n"+(b.adunare(c).toString()));
        System.out.println("inmultesc b*c=\n"+(b.inmultire(c).toString()));
    }
}
