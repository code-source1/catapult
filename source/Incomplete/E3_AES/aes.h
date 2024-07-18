#ifndef AES_CONFIG_H
#define AES_CONFIG_H

#include <iostream>

#define PRINT_DEC_MSG false

#if defined(AES_128)
#define AES_MODE AES_ECB_128
    std::cout << "AES_MODE is AES_ECB_128" << std::endl;
#elif defined(AES_192)
#define AES_MODE AES_ECB_192
    std::cout << "AES_MODE is AES_ECB_192" << std::endl;
#elif defined(AES_256)
#define AES_MODE AES_ECB_256
    std::cout << "AES_MODE is AES_ECB_256" << std::endl;
#else
    std::cerr << "define AES_MODE, eg. AES_ECB_128" << std::endl;
#endif

#endif // AES_CONFIG_H
