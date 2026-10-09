#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t u32;
#define ARRAY_COUNT(x) (sizeof(x)/sizeof((x)[0]))
struct BoxPokemon {u32 personality,otId;unsigned char header[24];union {u32 raw[12];} secure;};
#include "native-crypto.h"
int main(void){unsigned char seed[100],sample[100],roundtrip[100];FILE *f=fopen("crypto-seed-private.bin","rb");assert(f&&fread(seed,1,100,f)==100&&!fclose(f));f=fopen("baseline1304-party-private.bin","rb");assert(f&&fread(sample,1,100,f)==100&&!fclose(f));memcpy(roundtrip,seed,100);struct BoxPokemon box;assert(sizeof box==80);memcpy(&box,seed,80);DecryptBoxMon(&box);assert(!memcmp(&box,sample,80));assert(!memcmp(seed+80,sample+80,20));EncryptBoxMon(&box);memcpy(roundtrip,&box,80);assert(!memcmp(roundtrip,seed,100));puts("PASS verbatim native crypto: actual baseline1304 matches fully in-place-decrypted Donut; encrypt restores all100 seed bytes, zero emulator frames. Candidate failed value/CPU position unavailable; no candidate-state reconstruction or retry.");}
