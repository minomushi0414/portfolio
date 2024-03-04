#include <stdio.h>
#include <math.h>

//モータ定数の定義
const double R=0.8; //R=0.8Ω
const double L=4.0e-3; //L=4.0mH
const double J=0.003; //J=0.003kgm^2
const double KT=0.85; //KT=0.85Nm/A=KE
const double KE=0.85;
const double b=R/L; const double c=(KT*KE)/(L*J);
//定数の定義
const int N=10; //三角波１周期あたりのデータ数
const double f=20000; //三角波の周波数.エリアシング注意.
const double T=1/f;
const double Amin=0; const double Amax=110; //定格電圧に合わせる
const double t_end=0.5;
const int sumN=(t_end*N)/T; //0~t_end[s]までの総データ数
const double dt=T/N; //サンプリングタイム
const double Vcc=110; //印加電圧. 定格電圧にしておく.
const double ref=50; //速度指令値[rad/s]

//プロトタイプ宣言
double triangle(double Amin, double Amax, int data,int N);
int comparator(double ref, double Amin, double Amax, int data, int N);
void DCmotor(double dt, double V, double *p_i, double *p_omega);
double P(double ref, double y);
double PID(double ref, double y, double dt, double *integral, double *diff);
double Servo(double ref, double *u, double y, double dt, double *i_h, double *omega_h, double *z);
void Plot();

int main(void){
    //ファイルの作成
    FILE *fp;
    fp=fopen("dataDCmotor.dat","w");
    //変数の定義
    double t(0);
    //P制御用
    double xP=0; double yP=0;
    double *pomega_P,*pi_P;
    pomega_P=&xP, pi_P=&yP;
    //PID制御用
    double xPID=0; double yPID=0;
    double *pomega_PID,*pi_PID;
    pomega_PID=&xPID; pi_PID=&yPID;
    double Int=0; double Diff=0;
    double *pintegral_PID, *pdiff_PID;
    pintegral_PID=&Int; pdiff_PID=&Diff;
    //サーボ用
    double x=0; double y=0; //ω=0[rad/s],ω'=0[rad/s/s]
    double *pomega,*pi;  
    pomega=&x; pi=&y; //ポインタ変数の初期化
    double xh1=100; double xh2=50; //推定値の初期値は適当に与えるしかない
    double z0=0; //偏差の積分
    double *pi_h, *pomega_h, *pz; //オブザーバ用
    pi_h=&xh1; pomega_h=&xh2; pz=&z0;
    //電圧
    double V_P=Vcc;
    double V_PID=Vcc;
    double V_servo=Vcc;
    double *p_V;
    p_V=&V_servo;

    //データ数
    int data=0;
    //DCモータのモデルを計算
    for(data=0; data <= sumN; data++){
        fprintf(fp,"%f %f %f %f\n",t,*pomega_P,*pomega_PID,*pomega);
        printf("%f %f\n",t,*pomega);
        //参照電圧を生成
        V_P=P(ref,*pomega_P);
        V_PID=PID(ref,*pomega_PID,dt,pintegral_PID,pdiff_PID);
        *p_V=Servo(ref,p_V,*pomega,dt,pi_h,pomega_h,pz);
        //コンパレータでPWM信号に変換（２値化）
        double PWM_P=Vcc*comparator(V_P,Amin,Amax,data,N);
        double PWM_PID=Vcc*comparator(V_PID,Amin,Amax,data,N);
        double PWM_servo=Vcc*comparator(*p_V,Amin,Amax,data,N);
        //制御対象のブロック線図を計算
        DCmotor(dt,PWM_P,pi_P,pomega_P);
        DCmotor(dt,PWM_PID,pi_PID,pomega_PID);
        DCmotor(dt,PWM_servo,pi,pomega);
        t += dt;
    }
    fclose(fp);
    Plot();

    return 0;
}

double triangle(double Amin, double Amax, int data,int N){
    double a=Amax-Amin;
    int phase=data/N;
    double x=(double)data/(double)N;
    double wave(0);
    if((data%N) <= N/2) wave=2*a*(x-phase)+Amin;
    else wave=-a*(2*(x-phase)-1)+Amax;

    return wave;
}

int comparator(double ref, double Amin, double Amax, int data, int N){
    int output(0);
    double career=triangle(Amin,Amax,data,N);
    if(ref >= career) output=1;
    else output=0;

    return output;
}

void DCmotor(double dt, double V, double *p_i, double *p_omega){
    double v=V-KE*(*p_omega); //電機子電圧と誘起電圧の差
    *p_i += 1/L*(v-R*(*p_i))*dt; //i=1/(Ls+R)をnegative feedbackとして捉えて積分器を計算
    double tau=KT*(*p_i); //発生トルク
    *p_omega += 1/J*(tau)*dt; //ω=1/Js*τを計算
}

//P制御
/* V_ref=Kref*ω_ref-Kp*ω
   Kref=KE+Kp
   ２自由度制御? */
double P(double ref, double y){
    double output(0);
    const double Kp=10;
    const double Kref=KE+Kp;
    output=Kref*ref-Kp*y;

    return output;
}

//PID制御
double PID(double ref, double y, double dt, double *integral, double *diff){
    double output(0);
    //実際にはPWMで定格を超える電圧は印加しないのでゲインは自由に設定
    const double Kp=100; const double KI=1000; const double KD=3;
    const double omega_c=500; //カットオフ周波数
    double de(0);
    //擬似微分
    de=((ref-y)- *diff)*omega_c;
    *diff += de*dt;
    //数値積分
    *integral += (ref-y)*dt;
    //指令値
    output=Kp*(ref-y)+KI*(*integral)+KD*de;

    return output;
}

//１型サーボ系(観測器付き)
double Servo(double ref, double *u, double y, double dt, double *i_h, double *omega_h, double *z){
    double output(0);
    //極
    const double l1=-600; const double l2=-700; const double l3=-900; //状態FB器の極
    const double e1=-30000; const double e2=-40000; //オブザーバの極. FBの極よりも収束を速くすることに注意.
    //ゲイン(設計方程式より算出)
    const double f1=-L*(l1+l2+l3)-R; const double f2=L*J*(l1*l2+l2*l3+l3*l1)/KT-KE;
    const double h=-L*J*l1*l2*l3/KT;
    const double h2=-(e1+e2)-R/L; const double h1=J/KT*e1*e2-KE/L-(R*J)/(L*KT)*h2;
    //内部モデル
    /* オブザーバより先にこちらを計算しなければならない */
    //積分器
    *z += (ref-y)*dt;
    //状態FBで入力を算出
    output=-(f1*(*i_h)+f2*(*omega_h))+h*(*z); //u=-Fx+Hz

    //オブザーバ
    /* 行列計算を極力ラプラス領域でこれらを個別に算出 */
    //入力項
    double B1=1/L*(*u); //第１行成分
    double B2=0; //第２行成分
    //オブザーバゲインによる項
    double H1=h1*(y-*omega_h); //H(y-y^)の第１行成分
    double H2=h2*(y-*omega_h); //H(y-y^)の第２行成分
    //ドラフト項
    double A1=-R/L*(*i_h)-KE/L*(*omega_h); //Ax^の第１行成分
    double A2=KT/J*(*i_h); //Ax^の第２行成分
    //状態推定値の時間微分
    double di_h=A1+B1+H1; //x'^の第１行成分
    double domega_h=A2+B2+H2; //x'^の第２行成分
    //積分器
    *i_h += di_h*dt;
    *omega_h += domega_h*dt;

    return output;
}

void Plot(){
    FILE *gp;
    //Windowsユーザーは_popen()でお願いします
    gp=popen("/usr/local/bin/gnuplot -persist","w"); //パイプ開通.フルパス指定
    if(gp==NULL){
        printf("ERROR");
        exit(1);
    }
    //fprintf(gp,"set terminal pdf\n"); //gnuplotで見るときは消して下さい
    //fprintf(gp,"set out 'dataDCmotor.pdf'\n"); //gnuplotで見るときは消して下さい
    fprintf(gp,"set multiplot\n");

    fprintf(gp,"set lmargin screen 0.1\n");
    fprintf(gp,"set rmargin screen 0.9\n");
    fprintf(gp,"set tmargin screen 0.95\n");
    fprintf(gp,"set bmargin screen 0.75\n");
    fprintf(gp,"set xrange [0:0.1]\n");
    fprintf(gp,"set yrange [-10:80]\n");
    fprintf(gp,"set xtics 0.01\n");
    fprintf(gp,"set mxtics 5\n");
    fprintf(gp,"set ytics 10\n");
    fprintf(gp,"set mytics 5\n");
    //fprintf(gp,"set xlabel 't [s]'\n");
    fprintf(gp,"set ylabel 'ω [rad/s]'\n");
    fprintf(gp,"set nokey\n");
    fprintf(gp,"set label 1 'P' at screen 0.92,0.85\n");
    fprintf(gp,"plot 'dataDCmotor.dat' using 1:2 with lines lw 2\n");

    fprintf(gp,"set lmargin screen 0.1\n");
    fprintf(gp,"set rmargin screen 0.9\n");
    fprintf(gp,"set tmargin screen 0.65\n");
    fprintf(gp,"set bmargin screen 0.45\n");
    fprintf(gp,"set xrange [0:0.1]\n");
    fprintf(gp,"set yrange [-10:70]\n");
    fprintf(gp,"set xtics 0.01\n");
    fprintf(gp,"set mxtics 5\n");
    fprintf(gp,"set ytics 10\n");
    fprintf(gp,"set mytics 5\n");
    //fprintf(gp,"set xlabel 't [s]'\n");
    fprintf(gp,"set ylabel 'ω [rad/s]'\n");
    fprintf(gp,"set label 1 'PID' at screen 0.92,0.55\n");
    fprintf(gp,"plot 'dataDCmotor.dat' using 1:3 with lines lw 2\n");

    fprintf(gp,"set lmargin screen 0.1\n");
    fprintf(gp,"set rmargin screen 0.9\n");
    fprintf(gp,"set tmargin screen 0.35\n");
    fprintf(gp,"set bmargin screen 0.15\n");
    fprintf(gp,"set xrange [0:0.1]\n");
    fprintf(gp,"set yrange [-10:70]\n");
    fprintf(gp,"set xtics 0.01\n");
    fprintf(gp,"set mxtics 5\n");
    fprintf(gp,"set ytics 10\n");
    fprintf(gp,"set mytics 5\n");
    fprintf(gp,"set xlabel 't [s]'\n");
    fprintf(gp,"set ylabel 'ω [rad/s]'\n");
    fprintf(gp,"set label 1 'Servo' at screen 0.92,0.25\n");
    fprintf(gp,"plot 'dataDCmotor.dat' using 1:4 with lines lw 2\n");

    //fprintf(gp,"unset terminal\n"); //gnuplotで見るときは消して下さい
    fprintf(gp,"unset multiplot\n");

    fflush(gp);
    //Windowsユーザーは_pclose()でお願いします
    pclose(gp);
}