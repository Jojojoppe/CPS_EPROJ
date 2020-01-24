#include <vector>
#include <stdint.h>
#include <mutex>

#define FSPL 1.0
#define Dt 1.0
#define Dr 1.0
#define lambda 1249.13524166667
#define noiseFloor -80

class Client{
    public:
        int socket;
        std::vector<Client*> * clients;
        int id;
        std::mutex * m_clients;

        float txp, x, y;
        float L;            // Loss (TXP*FSPL*Dt*Dr*lambda^2/39.48)

        Client(int socket, std::vector<Client*> * clients, int id, std::mutex * m_clients);
        ~Client();

        // Packet is received
        void recv(uint8_t * data, uint32_t length);
        // Send packet to node with ID [id]
        void send_to(uint8_t * data, uint32_t length, int id);
        // Recalculate Loss
        void calculateLoss();
        // Calculate RSSI for certain distance. In dB(m)
        float calculateRSSI(float distance);
        // Calculate distance for certain RSSI in m
        float calculateDistance(float RSSI);
};