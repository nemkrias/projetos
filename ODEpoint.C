#include "ODEpoint.h"
using namespace std;

Xvar::Xvar(int n) {
    x.resize(n);
}

Xvar::Xvar(vector<double> v) {
    x = v;
}

Xvar::Xvar(const initializer_list<double>& v) : x(v) {
}

Xvar::Xvar(const Xvar &X) : x(X.x){
}

Xvar& Xvar::operator=(const Xvar& other) {
    if (this != &other) {
        x = other.x;
    }
    return *this;
}

Xvar Xvar::operator+(const Xvar& other) {
    Xvar result(*this);
    for (size_t i = 0; i < x.size(); ++i) {
        result.x[i] += other.x[i];
    }
    return result;
}

double& Xvar::operator[](int index) {
    return x[index];
}

Xvar operator*(double scalar, const Xvar& var) {
    Xvar result(var);
    for (size_t i = 0; i < result.x.size(); ++i) {
        result.x[i] *= scalar;
    }
    return result;
}

ostream& operator<< (ostream& s, const Xvar& P){
    s << "[";
    for (int i = 0; i < P.x.size()-1; i++){
        s << P.x[i] << ",";
    }
    s<< P.x.back() << "]";
    return s;
}

vector<double>& Xvar::X() {
    return x;
}

void ODEpoint::SetODEpoint(double t_, Xvar& p){
    t = t_;
    x = p.X();
}

void ODEpoint::SetODEpoint(double t_, const initializer_list<double>& v) {
    t = t_;
    X() = v;
}

void ODEpoint::SetODEpoint(double t_, vector<double> v){
    t = t_;
    x = v;
}






