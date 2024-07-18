#include "main.cpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>


using namespace std;

#define AES_ECB_128 128
#define AES_ECB_192 192
#define AES_ECB_256 256

CCS_MAIN (int argc, char *argv[])
{
  // Macros defined for AES Mode user can choose the Macro and synthesize the DUT accordingly
#define PRINT_DEC_MSG false
#if   defined(AES_128)
  int aes_mode = AES_ECB_128;
  cout << "AES_MODE is AES_ECB_128" << endl;
#elif defined(AES_192)
  int aes_mode = AES_ECB_192;
  cout << "AES_MODE is AES_ECB_192" << endl;
#elif defined(AES_256)
  int aes_mode = AES_ECB_256;
  cout << "AES_MODE is AES_ECB_256" << endl;
#else
  cerr << "define AES_MODE, eg. AES_ECB_128" << endl;
  CCS_RETURN(-1);
#endif

  cout << "================" << endl;
  cout << " AES Encryption " << endl;
  cout << "================" << endl;

  if ((argc != 2) && (argc != 3)) {
    cerr << "Usage: " << argv[0] << " <input file for encryption>" << endl;
    cerr << "Usage: " << argv[0] << " <input file for encryption> <output file for encryption>" << endl;
    CCS_RETURN(-2);
  }

  // Defining stream containers for input message
  streampos size;
  char *memblock;

  // Channels for input and outputs
  ac_channel<io_type> msg_inp_chan;
  ac_channel<io_type> msg_aes_chan;
  ac_channel<io_type> msg_out_chan;

  // 256 Bits Key string
  string str = "60 3d eb 10 15 ca 71 be 2b 73 ae f0 85 7d 77 81 1f 35 2c 07 3b 61 08 d7 2d 98 10 a3 09 14 df f4";
  string inp_file = argv[1];
  string out_file;
  if (argc == 3) {
    out_file = argv[2];
  } else {
    out_file = "message.aes";
  }

  ifstream mgfile;
  ofstream aesfile;
  ofstream outfile;
  mgfile.open(inp_file, ios::in | ios::binary | ios::ate);

  // Reading message for encryption
  if (mgfile.is_open()) {
    // Getting size of message
    size = mgfile.tellg();
  } else {
    cout << "Unable to open " << inp_file;
    CCS_RETURN(-3);
  }

  // Assign the message memory
  memblock = new char[size];
  mgfile.seekg(0, ios::beg);
  mgfile.read(memblock, size);
  mgfile.close();

  string input_message(memblock, size);
  string encrypted_message;
  string decrypted_message;

  // Encrypt the message
  aes_encrypt(input_message, encrypted_message, str, msg_inp_chan, msg_out_chan, aes_mode);

  // Save encrypted message to file
  aesfile.open(out_file, ios::out | ios::binary);
  if (aesfile.is_open()) {
    aesfile.write(encrypted_message.c_str(), encrypted_message.size());
  } else {
    cout << "Unable to open file";
    CCS_RETURN(-4);
  }
  aesfile.close();

  cout << "Encrypted  Message: " << out_file << endl;

  // Decrypt the message
  aes_decrypt(encrypted_message, decrypted_message, str, msg_aes_chan, msg_out_chan, aes_mode);

  // If PRINT_DEC_MSG is true decrypted message will be printed in console
  if (PRINT_DEC_MSG) {
    cout << "Decrypted Message: " << decrypted_message << endl;
  }

  // Comparing decrypted message with original message and count for errors
  int error_count = 0;
  for (int i = 0; i < size; i++) {
    if (decrypted_message[i] != input_message[i]) {
      error_count++;
    }
  }

  cout << "\nUnmatch Count = " << error_count << endl;

  // Free memory
  delete[] memblock;

  CCS_RETURN(error_count);
}

