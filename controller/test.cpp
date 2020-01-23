#include <iostream>
#include <chrono>
typedef std::chrono::high_resolution_clock Clock;

int main()
{
    int x = 0;
    int* p = &x;
    auto t1 = Clock::now();
    while(1){
        auto t2 = Clock::now();
        if(std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() > 1000) {
            break;
        }
        (*p)++;
    }
    std::cout << x << std::endl;
    return 0;
}
//  3711628
// 21959267
// 48760588