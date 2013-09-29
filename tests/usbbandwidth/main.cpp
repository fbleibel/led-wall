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
    ofstream serial_out;
    ifstream serial_in;
     
    string device_name(argv[1]);
    serial_out.open(device_name.c_str());
    serial_in.open(device_name.c_str());
    if (!serial_out.is_open()) {
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
        serial_out.write(data.c_str(), data.size());
        serial_out.flush();
        packets_sent += BUFFER_PACKETS;
        
        if (serial_out.bad()) {
            cout << "Something bad happened writing!" << endl;
            return 1;
        }
        
        if (serial_in.bad()) {
            cout << "Something bad happened reading!" << endl;
            return 1;
        }
        
        if (packets_sent >= 10000) {
            timeval now;
            gettimeofday(&now, NULL);
            float elapsed = (now.tv_sec - start_time.tv_sec) * 1000000 + now.tv_usec - start_time.tv_usec;
            data_rate = (float) PACKET_SIZE * packets_sent / elapsed; // in MB
            data_rate *= 1024.0; // in kB
            cout << device_name << ": " << packets_sent << " packets sent (" << fixed << setprecision(2) << data_rate << " kB/s) ..." << endl;
            start_time = now;
            packets_sent -= 10000;
        }
        int in_avail = serial_in.rdbuf()->in_avail();
        if (in_avail) {
            char* in_buffer = new char[in_avail];
            serial_in.read(in_buffer, in_avail);
            cout << in_buffer << flush;
            delete(in_buffer);
        }
        continue;
    }
    return 0;
}
