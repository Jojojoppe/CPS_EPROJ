#include "Client.hpp"
#include <cstdio>
#include <cmath>
#include <sys/socket.h> 

void hexdump(void * d, int len){
    for(int i=0; i<len; i++){
        printf("%02x ", ((unsigned char*)d)[i]);
    }
    printf("\r\n");
}

Client::Client(int socket, std::vector<Client*> * clients, int id, std::mutex * m_clients){
    this->socket = socket;
    this->clients = clients;
    this->id = id;
    this->m_clients = m_clients;

    this->x = 0.0;
    this->y = 0.0;
    this->txp = 0.0;

    this->L = 0.0;
}

Client::~Client(){
}

void Client::send_to(uint8_t * data, uint32_t length, int id){
    // type in data[0]
    // RSSI in data[1]
    Client * c = (*(this->clients))[id];
    if(c==NULL) return;
    send(c->socket, &length, 4, 0);
    send(c->socket, data, length, 0);
}

void Client::recv(uint8_t * data, uint32_t length){
    if(length==0) return;
    uint8_t type = data[0];
    if(type==1){
        // CONTROL MESSAGE
        float * fdata = (float*) (&data[1]);
        this->txp = fdata[0];
        this->x = fdata[1];
        this->y = fdata[2];
        this->calculateLoss();

    }else if(type==0xff){

        // END REACHED, SHUTDOWN
        exit(0);

    }else{
        // DATA MESSAGE
        for(int i=0; i<this->clients->size(); i++){
            Client * c = (*(this->clients))[i];
            this->sent = true;
            if(c!=NULL && c->id!=this->id){
                // Try to send to client. Get distance between client and self
                float dist = sqrt(pow(c->x-this->x, 2) + pow(c->y-this->y, 2));
                float RSSI = this->calculateRSSI(dist);
                // TODO packet loss function?
                if(RSSI>=noiseFloor){
                    // Set RSSI in packet
                    data[1] = (uint8_t)RSSI;
                    this->send_to(data, length, c->id);
                    this->sentToList.push_back(c->id);
                }
            }
        }
    }
}

void Client::calculateLoss(){
    this->L = this->txp*FSPL*Dt*Dr*pow(lambda/1000,2)/39.48;
    printf("L=%f\r\n", this->L);
}

float Client::calculateRSSI(float distance){
    return 20.0*log10(this->L/(distance*distance));
}

float Client::calculateDistance(float RSSI){
    return sqrt(this->L/(pow(10.0, (RSSI/20.0))));
}