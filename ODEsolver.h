#ifndef __ODESOLVER__
#define __ODESOLVER__
#include <vector>
#include <iostream>
#include <map>
#include <functional>
#include "ODEpoint.h"
using namespace std;

class ODEsolver {
    public:
    ODEsolver(const vector<function<double(ODEpoint)>>);
    ~ODEsolver() = default;

    //set functions
    void SetODEfunc(const vector<function<double(ODEpoint)>>&);

    //solver methods
    const vector<ODEpoint>& Euler(ODEpoint i, double step, double T);
    const vector<ODEpoint>& PredictorCorrector(ODEpoint i, double step, double T);
    const vector<ODEpoint>& LeapFrog(ODEpoint i, double step, double T);
    const vector<ODEpoint>& RK2(ODEpoint i, double step, double T);
    const vector<ODEpoint>& RK4(ODEpoint i, double step, double T);

    private:
    vector<function<double(ODEpoint)>> F;
    map<string, vector<ODEpoint>> MS;
};

#endif  