#include <iostream>
#include <tuple>
#include <cmath> // std::floor
#include <fstream> //std::ifstream
#include <vector>
#include <string>

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
    //std::cout << std::get<0>(tup) << ", " << std::get<1>(tup) << std::endl;
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


int main()
{
    // Chunk to read from
    int chunk_x, chunk_y;
    chunk_x = 1;
    chunk_y = 0;

    // Offset in header to find chunk position within file
    int offset = get_offset(chunk_x, chunk_y);
    std::cout << "Offset is " << offset << std::endl;

    // Intialize file stream object. Opens with get() at end because of "ate"
    std::streampos size;
    std::ifstream file ("r.0.0.mca", std::ios::in | std::ios::binary | std::ios::ate);

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

        int location = (int)buffer[offset] | (int)buffer[offset+1]<<8 | (int)buffer[offset+2]<<16;
        std::cout << "Location in file: " << location << std::endl;
        int sector_count = (int)buffer[offset+3];
        std::cout << "Sectors: " << sector_count << std::endl;
    }
    else std::cout << "Could not open file" << std::endl;

    return 0;
}