#include "ODEsolver.h"
#include "ODEpoint.h"
#include <cmath>
using namespace std;

ODEsolver::ODEsolver(const vector<function<double(ODEpoint)>> functions){
    F = functions;
}

void ODEsolver::SetODEfunc(const vector<function<double(ODEpoint)>>& functions){
    F = functions;
}

const vector<ODEpoint>& ODEsolver::Euler(ODEpoint i, double step, double T){
    double t = i.T();
    vector <ODEpoint> V;
    V.push_back(i);

    while (t < T){
        ODEpoint Pcurr = V.back();

        // Logica
        vector<double> vetor = Pcurr.X();
        //double nextPos = vetor[0] + (step * F[0](Pcurr));
        //double nextVel = vetor[1] + (step * F[1](Pcurr));

        vector<double> posVel;
        for (int count = 0; count < F.size(); count++) {
            double val = vetor[count] + (step * F[count](Pcurr));
            posVel.push_back(val);
        }

        ODEpoint nextP = ODEpoint(t + step, Xvar(posVel));
        V.push_back(nextP);

        t += step;
    }

    MS["Euler"] = V;
    return MS["Euler"];
}

const vector<ODEpoint>& ODEsolver::PredictorCorrector(ODEpoint i, double step, double T){
    double t = i.T();
    vector <ODEpoint> V; //vetor que tem todos os ODEpoints calculados com Euler
    V.push_back(i); //colocar o primeiro ponto no vetor de ODEpoints

    while (t < T){
        ODEpoint Pcurr = V.back(); //ir buscar o último ponto adicionado ao vetor de ODEpoints


        // Logica
        vector<double> vetor = Pcurr.X(); //vetor posição do último ponto calculado
        vector<double> posVel; //vetor em que se armazena a posição do ponto em (t + step) com o método de Euler
        vector<double> posVel_novo; //vetor que vai armazenar a posição em (t + step) com o novo método

        for (int count = 0; count < F.size(); count++) {            //método de Euler
            double val = vetor[count] + (step * F[count](Pcurr));
            posVel.push_back(val);
        }

        ODEpoint Pnext (t+step, posVel); //cria o ponto seguinte (t + step)

        for (int j = 0; j < F.size(); j++){
            double val = vetor[j] + step * 0.5 * (F[j](Pcurr) + F[j](Pnext));
            posVel_novo.push_back(val);
        }

        ODEpoint nextP_novo = ODEpoint(t + step, Xvar(posVel_novo));
        V.push_back(nextP_novo);

        t += step;
    }

    MS["PredictorCorrector"] = V;
    return MS["PredictorCorrector"];
}

const vector<ODEpoint>& ODEsolver::LeapFrog(ODEpoint i, double step, double T){
    double t = i.T(); //tempo do primeiro ponto
    vector<ODEpoint> V; //criar o vetor de pontos
    V.push_back(i); //inserir o ponto dado como primeiro ponto
    
    vector<double> vetor_2; //vetor posição do segundo ponto
    for (int count = 0; count < F.size(); count++) {            //método de Euler
        double val = i.X()[count] + (step * F[count](i));
        vetor_2.push_back(val);
        cout << val << "lk"<< endl;
    }

    t+=step;
    cout << t << "t" << endl;
    
    ODEpoint ponto_2 (t, vetor_2);
    V.push_back(ponto_2);
    
    t+=step;

    while (t < T){
        ODEpoint Pcurr = V.back(); //ponto y
        ODEpoint Pant = V[V.size() - 2]; //ponto y-1

        // Logica
        vector<double> vetor_01 = Pant.X();
        vector<double> posVel;
        for (int count = 0; count < F.size(); count++) {
            double val = vetor_01[count] + (2 * step * F[count](Pcurr));
            posVel.push_back(val);
        }
        
        ODEpoint nextP = ODEpoint(t, Xvar(posVel));
        V.push_back(nextP);
        cout << t << endl;
        
        t += step; 
    }

    MS["LeapFrog"] = V;
    return MS["LeapFrog"];
}

const vector<ODEpoint>& ODEsolver::RK2(ODEpoint i, double step, double T){
    //K1 = h/2 * f(ti, yi)
    //K2 = h * f(ti + h, yi + K1)
    //y(i+1) = yi + K2
    double t = i.T(); //vai buscar o tempo do primeiro ponto recebido como argumento
    vector <ODEpoint> V; //vetor que tem todos os ODEpoints calculados com Euler
    V.push_back(i); //colocar o primeiro ponto no vetor de ODEpoints

    while (t < T){
        ODEpoint Pcurr = V.back(); //ir buscar o último ponto adicionado ao vetor de ODEpoints


        // Logica
        vector<double> vetor = Pcurr.X(); //vetor posição do último ponto calculado
        vector<double> K1; //vetor em que se armazena a posição do ponto em (t + step) com o método de Euler

        //método de euler com o step igual a metade do step
        for (int count = 0; count < F.size(); count++) {           
            double val = vetor[count] + (step * 0.5 * F[count](Pcurr)); //calcular o vetor y com meio step
            K1.push_back(val); //armazenar o y do t(i+1) no vetor K1
        }

        ODEpoint intermedio (t+(step * 0.5), K1); //cria o ponto seguinte (t + step/2)

        vector<double> vetor_2; //segundo vetor onde se vai armazenar o y do y(i+1) pretendido

        for (int j = 0; j < F.size(); j++){
            double val = vetor[j] + step * (F[j](intermedio)); //calcular o K2 e somas ao yi
            vetor_2.push_back(val);
        }
        V.push_back(ODEpoint(t + step, vetor_2)); //colocar o novo ponto no vetor de pontos
        t += step;
    }
    MS["RK2"] = V;
   return MS["RK2"];
}

const vector<ODEpoint>& ODEsolver::RK4(ODEpoint i, double step, double T){

    //K1 = step * F(ti, yi)
    //K2 = step * F(ti + step/2, yi + K1/2)
    //K3 = step * F(ti + step/2, yi + K2/2)
    //K4 = step * F(ti + step, yi + K3)
    //y(i + 1) = yi + (K1 + 2K2 + 2K3 + K4)/6

    double t = i.T(); //vai buscar o tempo do primeiro ponto recebido como argumento
    vector <ODEpoint> V; //vetor que tem todos os ODEpoints calculados com Euler
    V.push_back(i); //colocar o primeiro ponto no vetor de ODEpoints

    while (t < T){
        ODEpoint Pcurr = V.back(); //ir buscar o último ponto adicionado ao vetor de ODEpoints

        vector<double> vetor_1; //vetor em que se armazena a posição do ponto em (t + step) com o método de Euler

        //método de euler com o step igual a metade do step para usar no K2 (expressão: ti + step/2, yi + K1/2)
        for (int count = 0; count < F.size(); count++) {           
            double K1 = step * F[count](Pcurr); //calcular o vetor y com meio step
            vetor_1.push_back(Pcurr.X()[count] + 0.5 * K1); //armazenar o y do t(i+1) no vetor K1
        }

        ODEpoint intermedio (t+(step * 0.5), vetor_1); //cria o ponto seguinte (t + step/2)

        vector<double> vetor_2; //segundo vetor onde se vai armazenar o y do y(i+1) pretendido

        //método de Euler com o step igual a metade para usar no K3 (expressão: ti + step/2, yi + K2/2)
        for (int j = 0; j < F.size(); j++){
            double K2 = step * (F[j](intermedio)); //calcular o K2 e somas ao yi
            vetor_2.push_back(Pcurr.X()[j] + 0.5 * K2);
        }

        ODEpoint intermedio2 (t+(step * 0.5), vetor_2);

        //método de Euler normal para usar no K4 (expressão: ti + step, yi + K3)
        vector<double> vetor_3;
        for (int j = 0; j < F.size(); j++){
            double K3 = step * F[j](intermedio2);
            vetor_3.push_back(Pcurr.X()[j] + K3);
        }

        ODEpoint intermedio3 (t + step, vetor_3);

        vector<double> vetor_4; //vetor com o resultado final do novo ponto
        for (int j = 0; j < F.size(); j++){
            double K1 = step * F[j](Pcurr);
            double K2 = step * F[j](intermedio);
            double K3 = step * F[j](intermedio2);
            double K4 = step * F[j](intermedio3);
            vetor_4.push_back(Pcurr.X()[j] + (K1+2*K2+2*K3+K4)/6);
        }

        V.push_back(ODEpoint(t+step, vetor_4));
        t += step;
    }
    MS["RK4"] = V;
    return MS["RK4"];
}

