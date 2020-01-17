# NetEmu - Ad-Hoc network emulator
A program which can emulate an Ad Hoc network without having one. It acts as a TCP server and keeps track of all the positions of the connected nodes and decides wehter a specicif node can receive a sent packet.

### Relay rules
The decision wether a node can receive a packet is not directly done by distance. It calculates the free space path loss (with possible other losses) and derives a received signal strength. In combination with a set noise floor (thus being the SNR) a decision can be made (e.g. the RSSI must be higher than the noise floor) combined with a possible packet loss.

### Configuration
All parameters can be set in a configuration ini file which is read by NetEmu.

### Packet
Two types of packets can be sent to NetEmu: control packets and data packets, each having their own layout

#### data packet
| Field name | Length | Endianness | Type   |
|------------|--------|------------|--------|
| Length     | 4      | little     | int    |
| Type (=0)  | 1      | -          | char   |
| RSSI       | 1      | -          | char   |
| DATA       | -      | -          | -      |

#### config packet
| Field name | Length | Endianness | Type   |
|------------|--------|------------|--------|
| Length     | 4      | little     | int    |
| Type (=1)  | 1      | -          | char   |
| TX power   | 8      | little     | double |
| x position | 8      | little     | double |
| y position | 8      | little     | double |
