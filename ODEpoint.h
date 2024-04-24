#ifndef __ODEPOINT__
#define __ODEPOINT__
#include <vector>
#include <iostream>
using namespace std;

class Xvar {
    public:
    Xvar() = default;
    Xvar(int);              //número de variáveis dependentes
    Xvar(vector<double>);   //passar um vetor
    Xvar(const initializer_list<double>& v); //usar um initializer list para construir o objeto (whatever that means??)
    ~Xvar() = default; //destrutor

    Xvar(const Xvar &X); //construtor de cópia
    Xvar& operator=(const Xvar&); //assignment operator
    Xvar operator+(const Xvar&); //operador +
    double& operator[](int); //X[i]

    friend Xvar operator*(double, const Xvar&); //multiplicar um escalar por X
    friend ostream& operator<< (ostream&, const Xvar&);

    vector<double>& X(); //acessor to x

    protected:
    vector<double> x;  
};

class ODEpoint : public Xvar {
    private:
    double t; //time

    public:
    ODEpoint() : t(-1) {;}
    ODEpoint(double t_, Xvar a_) : t(t_), Xvar(a_) {;}
    ODEpoint(double t_, const vector<double>& v) : t(t_), Xvar(v) {;}
    ODEpoint(double t_, const initializer_list<double>&  v) : t(t_), Xvar(v) {;}

    void SetODEpoint(double t_, Xvar& p);
    void SetODEpoint(double t_, const initializer_list<double>& v);
    void SetODEpoint(double t_, vector<double> v);

    double& T() {return t;} //acessar o tempo
};

#endif