#ifndef DB_UTILS
#define DB_UTILS

#include <stdint.h>
#include <libpq-fe.h>

#include "config.h"
#define DBPGconn "user = postgres host = db port = 5432 dbname = air_quality_db"

/*
 * A function is marked as SAFE if it does not contain (intended) vulnerabilities.
 */

uint32_t bswap_32(uint32_t x);                                //  SAFE
uint32_t bswap_64(uint64_t x);                                //  SAFE
uint8_t is_id_available(uint32_t id);                         //  SAFE
uint8_t add_entry_to_db(air_entry *entry);                    //  SAFE
uint8_t is_valid_entry_password(uint32_t id, char *password); //  SAFE
uint32_t get_entry_prng(uint32_t id);                         //  SAFE
void print_entry(uint32_t id);                                //  SAFE
void list_ids();                                              //  SAFE
uint8_t insert_bug_report(char *name, char *desc);            //  SAFE
void list_bug_reports();                                      //  SAFE

#endif