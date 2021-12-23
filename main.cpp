#include <iostream>
#include <tuple>
#include <cmath> // std::floor
#include <fstream> //std::ifstream
#include <vector>
#include <string>

#include "zlib/zlib.h"

#include <typeinfo>

// Check endianness
std::string endianness()
{
    int num = 1;
    if (*(char *)&num == 1)
    {
        return "Little";
    }
    else
    {
        return "Big";
    }
}


// Determine what region file a chunk is in
std::tuple<int, int> get_region(int chunk_x, int chunk_z)
{
    std::tuple<int, int> tup (std::floor(chunk_x/32), std::floor(chunk_z/32));
    return tup;
}


// Modulus function (to prevent negative remainders)
int mod(int a, int b)
{
    return (a%b+b)%b;
}


// Get the offset in the header for a given chunk to find its location and size (4kB sector count)
int get_offset(int chunk_x, int chunk_z)
{
    int offset = 4*((mod(chunk_x, 32))+(mod(chunk_z, 32))*32);
    return offset;
}


// Construct an integer from 4 bytes
int integer_from_4_bytes(std::vector<unsigned char> &buffer, int offset=0)
{
    std::vector<unsigned char> vec(buffer.begin()+offset, buffer.begin()+offset+5);
    return (int)vec[3] | (int)vec[2]<<8 | (int)vec[1]<<16 | (int)vec[0]<<24;
}


// Construct an integer from 3 bytes
int integer_from_3_bytes(std::vector<unsigned char> &buffer, int offset=0)
{
    std::vector<unsigned char> vec(buffer.begin()+offset, buffer.begin()+offset+4);
    return (int)vec[2] | (int)vec[1]<<8 | (int)vec[0]<<16;
}


// Construct an integer from 2 bytes
int integer_from_2_bytes(std::vector<unsigned char> &buffer, int offset=0)
{
    std::vector<unsigned char> vec(buffer.begin()+offset, buffer.begin()+offset+3);
    return (int)vec[1] | (int)vec[0]<<8;
}


// Reads a file and returns the contents in a vector of type unsigned char
std::vector<unsigned char> read_file(std::string filename)
{
    std::streampos size;
    std::ifstream file (filename, std::ios::in | std::ios::binary | std::ios::ate);

    if (file.is_open())
    {
        // Set the size of the buffer
        size = file.tellg();

        // Reset get() position to 0
        file.seekg(0, std::ios::beg);

        // Initialize signed buffer, read in data
        std::vector<char> signed_buffer(size);
        file.read(signed_buffer.data(), size);

        // Close the file
        file.close();

        // Create new buffer variable to convert char to unsigned char
        std::vector<unsigned char> buffer(size);
        for (int i=0; i<buffer.size(); i++)
        {
            buffer[i] = (unsigned char)signed_buffer[i];
        }
        return buffer;
    }
    else
    {
        return std::vector<unsigned char>();
    }
}


int main()
{
    // Read file contents into buffer
    std::vector<unsigned char> buffer = read_file("r.0.0.mca");

    for (int i=0; i<32; i++)
    {
        for (int j=0; j<32; j++)
        {
            // Offset in header to find chunk location in file, and number of sectors
            int offset = get_offset(i, j);
            std::cout << "Offset is " << offset << " at " << i << " " << j << std::endl;

            // 3-byte integer gives offset from start of file in 4kB sectors, 
            // multiply by 4096 to get byte index of start of chunk
            int location = integer_from_3_bytes(buffer, offset) * 4096; 
            std::cout << "Location in file: " << location << std::endl;

            // Length of the chunk in 4kB sectors
            int sector_count = (int)buffer[offset+3];
            std::cout << "Sectors: " << sector_count << std::endl;

            if ( (location != 0) && (sector_count != 0) )
            {
                // Remaining chunk length (bytes)
                int chunk_length = integer_from_4_bytes(buffer, location);
                std::cout << "Chunk length (bytes) is: " << chunk_length << std::endl;

                // Compression scheme (should be 2 for zlib scheme)
                int compression_scheme = (int)buffer[location+4];
                std::cout << "Compression scheme is " << compression_scheme << std::endl;

                // Compressed data
                std::vector<unsigned char> compressed_data(buffer.begin()+location+4, buffer.begin()+location+4+chunk_length-1);
                std::cout << compressed_data.size() << std::endl;
            }
            else
            {
                // Location and sector count are zero here, meaning chunk not in region file
                std::cout << "Chunk is empty" << std::endl;
            }

            std::cout << "\n";
        }
    }
    
    return 0;
}