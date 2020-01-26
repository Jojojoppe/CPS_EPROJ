#include <vector>
#include <tuple>
#include <map>

struct Cell{
    int x, y;
    bool visited;
    bool north, east, south, west;
    bool final;
};

class Maze{
    public:
        int width, height;
        std::map<std::tuple<int,int>, Cell> grid;

        uint8_t * data;
        size_t dataLen;
        std::tuple<int,int> exit;

        Maze(int width, int height, std::tuple<int,int> exit);
        ~Maze();
        void generate();
        std::vector<std::tuple<int,int>> get_neighbours(std::tuple<int,int> pos);
        void reload();
};