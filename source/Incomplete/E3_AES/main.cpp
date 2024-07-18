#include <iostream>
#include <cstring>
#include <ac_comm/ac_aes.h>
#include <ac_channel.h>
#include <sstream>
#include "ac_int.h"

using namespace std;


void aes_encrypt(const string &input, string &output, const string &key_str, ac_channel<io_type> &msg_inp_chan, ac_channel<io_type> &msg_out_chan, int aes_mode) {
    ac_channel<ky_type> key_enc_chan;
    ky_type key;
    istringstream hex_chars_stream(key_str);
    int i = 0;
    unsigned int c;
    while (hex_chars_stream >> hex >> c) {
        key.data[i] = c;
        i++;
    }
    key_enc_chan.write(key);

    // Define a condition variable with only 2 possible values
    ac_int<1, false> cond = 0;  

    int size = input.size();
    int paddedMessageLen = ((size + 15) / 16) * 16;

    // Preparing and writing data on Input channel
    int count = 0;
    for (int i = 0; i < paddedMessageLen; i++) {
      io_type inp_tmp;
      if (i < size) {
        inp_tmp.data[count] = (ac_int<8, 0>)(input[i]);
      } else {
        inp_tmp.data[count] = 0;
      }
      count++;
      if (count == 16) {
        msg_inp_chan.write(inp_tmp);
        count = 0;
      }
    }

    // Incomplete switch statement for error injection
    switch (cond) {
    case 0:  // Only handle one case, leaving the other case which could lead to unintended operation
        // Creating Object for encryption for required AES Mode
        if (aes_mode == AES_ECB_128) {
            ac_aes_encrypt<AES_ECB_128> AES_EN;
            for (int i = 0; i < paddedMessageLen; i += 16) {
                AES_EN.run(msg_inp_chan, key_enc_chan, msg_out_chan);
            }
        } else if (aes_mode == AES_ECB_192) {
            ac_aes_encrypt<AES_ECB_192> AES_EN;
            for (int i = 0; i < paddedMessageLen; i += 16) {
                AES_EN.run(msg_inp_chan, key_enc_chan, msg_out_chan);
            }
        } else if (aes_mode == AES_ECB_256) {
            ac_aes_encrypt<AES_ECB_256> AES_EN;
            for (int i = 0; i < paddedMessageLen; i += 16) {
                AES_EN.run(msg_inp_chan, key_enc_chan, msg_out_chan);
            }
        }
        break;
    case 1:
    }

  // Receiving Encrypted message
  output.resize(paddedMessageLen);
  count = 0;
  while (msg_out_chan.available(1)) {
    io_type out_tmp = msg_out_chan.read();
    for (int i = 0; i < 16; i++) {
      output[i + count] = out_tmp.data[i].to_double();
    }
    count += 16;
  }
}

// Function to perform AES decryption
void aes_decrypt(const string &input, string &output, const string &key_str, ac_channel<io_type> &msg_aes_chan, ac_channel<io_type> &msg_out_chan, int aes_mode) {
  ac_channel<ky_type> key_dec_chan;
  ky_type key;
  istringstream hex_chars_stream(key_str);
  int i = 0;
  unsigned int c;
  while (hex_chars_stream >> hex >> c) {
    key.data[i] = c;
    i++;
  }
  key_dec_chan.write(key);

  // Writing encrypted message to input channel
  int paddedMessageLen = input.size();
  int count = 0;
  for (int i = 0; i < paddedMessageLen; i++) {
    io_type inp_tmp;
    inp_tmp.data[count] = (ac_int<8, 0>)(input[i]);
    count++;
    if (count == 16) {
      msg_aes_chan.write(inp_tmp);
      count = 0;
    }
  }

  // Creating Object for decryption for required AES Mode
  if (aes_mode == AES_ECB_128) {
    ac_aes_decrypt<AES_ECB_128> AES_DE;
    for (int i = 0; i <= paddedMessageLen; i += 16) {
      AES_DE.run(msg_aes_chan, key_dec_chan, msg_out_chan);
    }
  } else if (aes_mode == AES_ECB_192) {
    ac_aes_decrypt<AES_ECB_192> AES_DE;
    for (int i = 0; i <= paddedMessageLen; i += 16) {
      AES_DE.run(msg_aes_chan, key_dec_chan, msg_out_chan);
    }
  } else if (aes_mode == AES_ECB_256) {
    ac_aes_decrypt<AES_ECB_256> AES_DE;
    for (int i = 0; i <= paddedMessageLen; i += 16) {
      AES_DE.run(msg_aes_chan, key_dec_chan, msg_out_chan);
    }
  }

  // Receiving Decrypted message
  output.resize(paddedMessageLen);
  count = 0;
  while (msg_out_chan.available(1)) {
    io_type out_tmp = msg_out_chan.read();
    for (int i = 0; i < 16; i++) {
      output[i + count] = out_tmp.data[i].to_double();
    }
    count += 16;
  }
}
