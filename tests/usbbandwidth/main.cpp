/*
 * Usb Bandwidth Test
 *
 * This program tests the usb bandwidth for the USB-to-Teensy connection - but
 * only in one direction (computer to teensy).
 * This program regularly sends packets of a given size - by default the
 * maximum USB packet size of 64.
 * Constantly call Serial.read()
 */
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sys/time.h>

using namespace std;

/*
 * Pass in a device name e.g. usbbandwidth /dev/ttyACM0 and optionally a
 * packet size after that (e.g. usbbandwidth /dev/ttyACM0 64).
 *
 * You can monitor the bandwidth that you're getting to multiple teensy at the
 * same time by launching another instance of the process with a different
 * device name and running both side-by-side.
 */
int main(int argc, char** argv) {
    if (argc <= 1) {
        cout << "Must pass in a device name! e.g. /dev/ttyACM0" << endl;
        cout << "Example: " << argv[0] << " /dev/ttyACM0 64" << endl;
        return 1;
    }

    int packet_size = 64;

    if (argc >= 3) {
    	packet_size = atoi(argv[2]);
    	if (packet_size == 0) {
    		cout << "Error: invalid packet size" << endl;
    		return 1;
    	}
    }

    int buffer_size = packet_size;

    // Open the Teensy USB device for writing
    ofstream serial_out;
    string device_name(argv[1]);

    serial_out.open(device_name.c_str());

    if (!serial_out.is_open()) {
        cout << "Error opening " << device_name << " for writing!" << endl;
        return 1;
    }

    // Prepare some data to write - here repeating the numbers from 0 to 9.
    string data;
    data.reserve(buffer_size);
    for (size_t i = 0; i < buffer_size; i++) {
        char v = '0' + (i % 10);
        data.push_back(v);
    }

    int packets_sent = 0;
    timeval start_time;
    gettimeofday(&start_time, NULL);
    while ( true ) {
    	// Write one packets to the Teensy  board
        serial_out.write(data.c_str(), data.size());
        serial_out.flush();
        packets_sent += 1;
        
        if (serial_out.bad()) {
            cout << "Something bad happened writing!" << endl;
            return 1;
        }
        
        /* Calculate bandwidth every 2000 packets sent and print it out */
        if (packets_sent >= 2000) {
            timeval now;
            gettimeofday(&now, NULL);
            // Time elapsed in microseconds
            float elapsed = (now.tv_sec - start_time.tv_sec) * 1000000 + now.tv_usec - start_time.tv_usec;
            float data_rate = (float) packet_size * packets_sent / elapsed; // in MB
            data_rate *= 1024.0; // in kB
            cout << device_name << ": " << packets_sent << " packets sent ("
                 << fixed << setprecision(2) << data_rate << " kB/s) ..." << endl;
            start_time = now;
            packets_sent -= 2000;
        }
    }
    return 0;
}
