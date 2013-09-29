#include <iostream>
#include <fstream>
#include <iomanip>
#include <sys/time.h>

using namespace std;
const size_t PACKET_SIZE = 64;
const size_t BUFFER_PACKETS = 10;
const size_t BUFFER_SIZE = PACKET_SIZE * BUFFER_PACKETS;


int main(int argc, char** argv) {
    if (argc <= 1) {
        cout << "Must pass in a device name! e.g. /dev/ttyACM0" << endl;
        return 1;
    }
    ofstream serial;
    ifstream serial_in;
    serial.rdbuf()->pubsetbuf(0, 0);
    serial_in.rdbuf()->pubsetbuf(0, 0);
    
    string device_name(argv[1]);
    serial.open(device_name.c_str());
    serial_in.open(device_name.c_str());
    if (!serial.is_open()) {
        cout << "Error opening " << device_name << " for writing!" << endl;
        return 1;
    }

    if (!serial_in.is_open()) {
        cout << "Error opening " << device_name << " for reading!" << endl;
        return 1;
    }

    serial_in.ignore(-1);
    
    string data;
    data.reserve(BUFFER_SIZE);
    for (size_t i = 0; i < BUFFER_SIZE; i++) {
        char v = '0' + (i % 10);
        data.push_back(v);
    }
    
    int packets_sent = 0;
    float data_rate = 0;
    timeval start_time;
    gettimeofday(&start_time, NULL);
    while ( true ) {
        serial.write(data.c_str(), data.size());
        serial.flush();
        packets_sent += BUFFER_PACKETS;
        
        if (serial.bad()) {
            cout << "Something bad happened!" << endl;
            serial.clear();
            //serial.close();
            //return 1;
        }
        if (packets_sent >= 2000) {
            timeval now;
            gettimeofday(&now, NULL);
            float elapsed = (now.tv_sec - start_time.tv_sec) * 1000000 + now.tv_usec - start_time.tv_usec;
            data_rate = (float) PACKET_SIZE * packets_sent / elapsed;
            cout << "+" << packets_sent << " packets sent (" << fixed << setprecision(2) << data_rate << " MB/s) ..." << endl;
            start_time = now;
            packets_sent -= 2000;
        }
        char ack;
        string test;
        getline(serial_in, test);
        if (!test.empty()) cout << "ACK: " << test << endl;
        continue;
        if ( serial_in.readsome(&ack, 1) ) {
            if (ack != '*') {
                cout << "ack symbol error!" << endl;
                return 1;
            }
            else {
                cout << "ACK" << endl;
            }
        }
    }
    return 0;
}
