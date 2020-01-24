#include <SDL2/SDL.h> 
#include <pthread.h>
#include <stdio.h>
#include <mutex>
#include <tuple>
#include <vector>

#include <unistd.h> 
#include <sys/socket.h> 
#include <stdlib.h> 
#include <netinet/in.h> 
#include <string.h>
#include <signal.h>
#include <sys/select.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <netinet/tcp.h>
#include <stdint.h>

#include <INIReader.hpp>
#include <Maze.hpp>
#include <Client.hpp>

Maze maze(16,16);
std::mutex m_maze;

bool running;

std::vector<Client*> clients;
std::mutex m_clients;

void DrawCircle(SDL_Renderer * renderer, int32_t centreX, int32_t centreY, int32_t radius){
   const int32_t diameter = (radius * 2);

   int32_t x = (radius - 1);
   int32_t y = 0;
   int32_t tx = 1;
   int32_t ty = 1;
   int32_t error = (tx - diameter);

   while (x >= y)
   {
      //  Each of the following renders an octant of the circle
      SDL_RenderDrawPoint(renderer, centreX + x, centreY - y);
      SDL_RenderDrawPoint(renderer, centreX + x, centreY + y);
      SDL_RenderDrawPoint(renderer, centreX - x, centreY - y);
      SDL_RenderDrawPoint(renderer, centreX - x, centreY + y);
      SDL_RenderDrawPoint(renderer, centreX + y, centreY - x);
      SDL_RenderDrawPoint(renderer, centreX + y, centreY + x);
      SDL_RenderDrawPoint(renderer, centreX - y, centreY - x);
      SDL_RenderDrawPoint(renderer, centreX - y, centreY + x);

      if (error <= 0)
      {
         ++y;
         error += ty;
         ty += 2;
      }

      if (error > 0)
      {
         --x;
         tx += 2;
         error += (tx - diameter);
      }
   }
}

void * GUI(void * params){
    SDL_Window * win = (SDL_Window*) params;
    SDL_Renderer* rend = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED); 

    while(running){
        // Poll for quit event
        SDL_Event event; 
        while (SDL_PollEvent(&event)){
            if(event.type == SDL_QUIT){
                running = false;
                break;
            }
        } 

        // Clear screen
        SDL_SetRenderDrawColor(rend, 255, 255, 255, SDL_ALPHA_OPAQUE);
        SDL_RenderClear(rend);

        // Draw maze
        m_maze.lock();
        SDL_SetRenderDrawColor(rend, 0, 0, 0, SDL_ALPHA_OPAQUE);
        for(int x=0; x<maze.width; x++){
            for(int y=0; y<maze.height; y++){
                if(maze.grid[std::tuple<int,int>(x,y)].west){
                    SDL_RenderDrawLine(rend, 16+x*16, 16+y*16, 16+x*16, 16+(y+1)*16);
                }
                if(maze.grid[std::tuple<int,int>(x,y)].north){
                    SDL_RenderDrawLine(rend, 16+x*16, 16+y*16, 16+(x+1)*16, 16+y*16);
                }
                if(maze.grid[std::tuple<int,int>(x,y)].east){
                    SDL_RenderDrawLine(rend, 16+(x+1)*16, 16+y*16, 16+(x+1)*16, 16+(y+1)*16);
                }
                if(maze.grid[std::tuple<int,int>(x,y)].south){
                    SDL_RenderDrawLine(rend, 16+x*16, 16+(y+1)*16, 16+(x+1)*16, 16+(y+1)*16);
                }
            }
        }
        m_maze.unlock();

        // Draw nodes
        // Client structure is needed: lock first
        m_clients.lock();
        for(auto& c : clients){
            if(c==NULL) continue;
            SDL_SetRenderDrawColor(rend, 255, 0, 0, SDL_ALPHA_OPAQUE);
            DrawCircle(rend, 16+c->x*16+8, 16+c->y*16+8, 2);

            // Draw RSSI lines
            float dist = c->calculateDistance(noiseFloor);
            uint32_t radius = (uint32_t)(16*dist);
            SDL_SetRenderDrawColor(rend, 0, 0, 255, SDL_ALPHA_OPAQUE);
            DrawCircle(rend, 16+c->x*16+8, 16+c->y*16+8, radius);
        }
        m_clients.unlock();

        SDL_RenderPresent(rend); 
        SDL_Delay(1000 / 15);
    }

    SDL_DestroyRenderer(rend); 
    pthread_exit(NULL);
}

void * client(void * param){
    int sock = *((int*)param);

    // Create a client structure and add it to clients
    // Client structure is lockec by m_clients
    m_clients.lock();
    // client ID is index in client structure
    int c_id = clients.size();
    Client c(sock, &clients, c_id, &m_clients);
    clients.push_back(&c);
    m_clients.unlock();

    // Receive packets
    bool in_packet = false;
    uint32_t packet_size;
    uint32_t received_size;
    uint8_t * packet;
    uint8_t * packet_ptr;
    uint8_t * packet_size_ptr = (uint8_t*)&packet_size;
    uint8_t packet_size_received = 0;
    while(running){
        // If not yet started receiving packets
        if(!in_packet){
            // Try to read up to 4 bytes for the packet size
            int count = read(sock, packet_size_ptr, 4-packet_size_received);
            if(count==0){
                // Link broken. remove client from list by setting client to NULL
                printf("> DISCONNECT %d\r\n", c_id);
                m_clients.lock();
                clients[c_id] = NULL;
                m_clients.unlock();
                break;
            }else if(count>0){
                // Received some bytes
                packet_size_received += count;
                packet_size_ptr += count;
                if(packet_size_received==4){
                    // Complete packet size is received
                    // Allocate memory for packet
                    packet = (uint8_t*) malloc(packet_size);
                    packet_ptr = packet;
                    packet_size_received = 0;
                    in_packet = true;
                    received_size = 0;
                }
            }
        }else{
            // Try to read packet
            int count = read(sock, packet_ptr, packet_size-received_size);
            if(count==0){
                // Link broken. remove client from list by setting client to NULL
                printf("> DISCONNECT %d\r\n", c_id);
                m_clients.lock();
                clients[c_id] = NULL;
                m_clients.unlock();
                break;
            }else if(count>0){
                // Received some bytes
                received_size += count;
                packet_ptr += count;
                if(received_size==packet_size){
                    // Full packet received
                    // Lock clients list and pass packet to client
                    // In client a packet can be sent to other clients
                    m_clients.lock();
                    c.recv(packet, packet_size);
                    m_clients.unlock();
                    // Packet is processed, free the packet
                    free(packet);
                    in_packet = false;
                    packet = NULL;
                    packet_ptr = NULL;
                    packet_size_ptr = (uint8_t*)&packet_size;
                }
            }
        }
    }

    pthread_exit(NULL);
}

int main(int argc, char ** argv){
    // Set running loops to true
    running = true;

    // Create a maze
    m_maze.lock();
    maze.generate();
    m_maze.unlock();

    // Initialize SDL
    if (SDL_Init(SDL_INIT_EVERYTHING) != 0) { 
        printf("error initializing SDL: %s\n", SDL_GetError()); 
        return -1;
    } 
    SDL_Window * win = SDL_CreateWindow("NetEmuC",
                                        SDL_WINDOWPOS_CENTERED, 
                                        SDL_WINDOWPOS_CENTERED, 
                                        16*18, 16*18, 0);

    // Start GUI thread
    pthread_t t_gui;
    pthread_create(&t_gui, NULL, GUI, win);

    // Creating socket
    int opt = 1;
    struct sockaddr_in address;
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));
    // Set socket options and bind socket
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8080);
    bind(sock, (struct sockaddr*)&address, sizeof(address));
    listen(sock, 10);

    // Listen loop
    std::vector<pthread_t> threads;
    while(running){
        // Accept incomming connections with a timeout of half a second
        // Set timeout for select
        fd_set fdread;
        struct timeval tv;
        struct sockaddr_in caddr;
        int caddr_len = sizeof(caddr);
        tv.tv_sec = 0;
        tv.tv_usec = 500000;
        FD_ZERO(&fdread);
        FD_SET(sock, &fdread);
        // Check if something is trying to connect
        int selectStatus = select(sock+1, &fdread, NULL, NULL, &tv);
        if(selectStatus>0){
            // Accept incomming connection
            int csock = accept(sock, (struct sockaddr*)&caddr, (socklen_t*)&caddr_len);
            // Set socket timeout to 1 second
            tv.tv_sec = 1;
            tv.tv_usec = 0;
            setsockopt(csock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
            printf("> Conneted\r\n");
            // Sending maze
            m_maze.lock();
            unsigned int plen = maze.dataLen+1;
            unsigned char tp = 2;
            send(csock, &plen, 4, 0);
            send(csock, &tp, 1, 0);
            send(csock, maze.data, maze.dataLen, 0);
            m_maze.unlock();
            // Start client thread
            pthread_t t_client = pthread_create(&t_client, NULL, client, &csock);
            threads.push_back(t_client);
        }
    }

    close(sock);
    pthread_join(t_gui, NULL);
    SDL_DestroyWindow(win);
    return EXIT_SUCCESS;
}