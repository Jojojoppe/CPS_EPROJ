#include "Maze.hpp"
#include <cstdlib>
#include <tuple>

Maze::Maze(int width, int height){
    this->width = width;
    this->height = height;
    
    // Fill the grid
    for(int h=0; h<height; h++){
        for(int w=0; w<width; w++){
            Cell c = {w, h, false, true, true, true, true, false};
            this->grid[std::tuple<int,int>(w,h)] = c;
        }
    }
}

Maze::~Maze(){
    free(this->data);
}

void Maze::generate(){
    std::vector<std::tuple<int,int>> stack;
    std::tuple<int,int> initial(0, 0);

    this->grid[initial].visited = true;
    stack.push_back(initial);
    while(stack.size()>0){
        std::tuple<int,int> current = stack.back();
        stack.pop_back();
        std::vector<std::tuple<int,int>> neighbours = this->get_neighbours(current);
        if(neighbours.size()>0){
            stack.push_back(current);
            int r = rand()%neighbours.size();
            std::tuple<int,int> chosen = neighbours[r];
            // Remove wall between
            if(this->grid[current].x == this->grid[chosen].x){
                if(this->grid[current].y > this->grid[chosen].y){
                    this->grid[current].north = false;
                    this->grid[chosen].south = false;
                }else{
                    this->grid[current].south = false;
                    this->grid[chosen].north = false;
                }
            }else if(this->grid[current].y == this->grid[chosen].y){
                if(this->grid[current].x > this->grid[chosen].x){
                    this->grid[current].west = false;
                    this->grid[chosen].east = false;
                }else{
                    this->grid[current].east = false;
                    this->grid[chosen].west = false;
                }
            }
            this->grid[chosen].visited = true;
            stack.push_back(chosen);
        }
    }

    // Fill maze data
    this->dataLen = this->width*this->height*13;
    this->data = (uint8_t*) malloc(this->dataLen);
    for(int x=0; x<this->width; x++){
        for(int y=0; y<this->height; y++){
            ((uint32_t*)(this->data+13*this->height*x+y*13))[0] = (uint32_t)x;
            ((uint32_t*)(this->data+13*this->height*x+y*13))[1] = (uint32_t)y;
            uint8_t* bs = (uint8_t*) &((uint32_t*)(this->data+13*this->height*x+y*13))[2];
            bs[0] = (uint8_t) this->grid[std::tuple<int,int>(x,y)].north;
            bs[1] = (uint8_t) this->grid[std::tuple<int,int>(x,y)].east;
            bs[2] = (uint8_t) this->grid[std::tuple<int,int>(x,y)].south;
            bs[3] = (uint8_t) this->grid[std::tuple<int,int>(x,y)].west;
            bs[4] = (uint8_t) this->grid[std::tuple<int,int>(x,y)].final;
        }
    }
}

std::vector<std::tuple<int,int>> Maze::get_neighbours(std::tuple<int,int> pos){
    std::vector<std::tuple<int,int>> res;
    int x = std::get<0>(pos);
    int y = std::get<1>(pos);
    if(x+1>-1&&x+1<this->width && y>-1&&y<this->height && !this->grid[std::tuple<int,int>(x+1,y)].visited){
        res.push_back(std::tuple<int,int>(x+1,y));
    }
    if(x-1>-1&&x-1<this->width && y>-1&&y<this->height && !this->grid[std::tuple<int,int>(x-1,y)].visited){
        res.push_back(std::tuple<int,int>(x-1,y));
    }
    if(x>-1&&x<this->width && y+1>-1&&y+1<this->height && !this->grid[std::tuple<int,int>(x,y+1)].visited){
        res.push_back(std::tuple<int,int>(x,y+1));
    }
    if(x>-1&&x<this->width && y-1>-1&&y-1<this->height && !this->grid[std::tuple<int,int>(x,y-1)].visited){
        res.push_back(std::tuple<int,int>(x,y-1));
    }
    return res;
}