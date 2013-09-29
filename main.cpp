#include <iostream>
#include <fstream>
#include <cstdio>
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
    fstream serial;
    string device_name(argv[1]);
    serial.open(device_name.c_str());
    if (!serial.is_open()) {
        cout << "Error opening " << device_name << "!" << endl;
        return 1;
    }

    serial.ignore(-1);
    
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
            cout << "+" << packets_sent << " packets sent (" << data_rate << " MB/s)" << endl;
            start_time = now;
            packets_sent -= 2000;
        }
        
        serial.sync();
        char ack;
        while (!serial.readsome(&ack, 1));
        if (ack=='*'){
            cout << "got ack!" << endl;
        } else {
            cout << "false alarm!" << endl;
        }
        cout << "tellg " << serial.tellg() << endl << "tellp "<< serial.tellp() << endl;
        serial.seekg(-1);
    }
    return 0;
}
