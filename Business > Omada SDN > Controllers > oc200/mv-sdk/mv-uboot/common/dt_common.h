/*
 *  Copyright (c) 2014  TP-LINK Co., Ltd
 *
 *  TP-LINK Co., Ltd R&D SMB Product Line
 *
 */

/* dramtest common
 *
 * typedefs, structure definitions, and routine prototypes.
 */
#include <common.h>
#include <command.h>
#include <console.h>

#ifndef FALSE
#define FALSE   0
#endif
#ifndef TRUE
#define TRUE    1
#endif

#define KB      (1024ULL)
#define MB      (1024ULL*KB)
#define GB      (1024ULL*MB)

#define LowMemEnd                32*MB
#define MapSize                  5
#define MapLower                 0
#define MapUpper                 1
#define MapUser                  2
#define MapUser2                 3
#define MapNull                  4

#define POS_IN_NULL_RANGE        0
#define POS_IN_LOWER_BASE        1
#define POS_IN_UPPER_BASE        2
#define POS_IN_LOWER_RANGE       3
#define POS_IN_UPPER_RANGE       4
#define POS_IN_BOTH_RANGE        5
#define POS_IN_ASSIGN_ADR        6 


#define ERROR_LIMIT              25
#define RETRY_LIMIT              100

#define DT_UNIT_BYTE_SIZE	8
#define DT_UNIT_BIT_SIZE	64

/*------------*/
/*  Typedefs  */
/*------------*/

#define DT_UINT   uint64_t

#define CHECK_CTRL_C(op) \
{ \
	if (ctrlc()) { \
		op; \
		putc ('\n'); \
		printf("Interrupted by user\n"); \
		return -1; \
	} \
}

typedef struct {
	char      *name;
	DT_UINT    base;
	DT_UINT    extent;
} dramMemRange;

typedef struct {
	char      auto_en;
	DT_UINT   type;
} testPatten;

typedef struct {
    char     *name;
    int32_t  (*fp)(DT_UINT, DT_UINT, uint32_t);
    uint32_t core_mask;
    uint32_t bursts;
    uint32_t failures;
    uint32_t total_failures;
} testDesc;


/*-----------*/
/*  Globals  */
/*-----------*/
extern dramMemRange memoryMap[MapSize];

int dt_random_generate  (int randmask);
int dt_probe_position   (void);
int dt_dramDataBusWidth (void);
int dt_dramAddrBusWidth (void);
int dt_minutes_delay    (int minutes);

int do_dram_mtest_test  (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_fade_test   (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_stable_test (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_read_test   (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_write_test  (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_rw_test     (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_rwm_test    (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_xtalk_test  (cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_databus_test(cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_addrbus_test(cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);
int do_dram_pattern_test(cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[]);

/*---------------------*/
/* Main Test Routines  */
/*---------------------*/
int32_t run_data_bus_tests   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_addr_bus_tests   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_mtest_quick_tests(DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_mtest_alt_tests  (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_mem_fade_tests   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_mem_rmw_tests    (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t run_dram_xtalk_tests (DT_UINT area, DT_UINT max_address, uint32_t bursts);

int32_t test_mem_self_addr   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_alternating (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_leftwalk0   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_leftwalk1   (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_random      (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_rightwalk0  (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_rightwalk1  (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_solid       (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t test_mem_xor         (DT_UINT area, DT_UINT max_address, uint32_t bursts);

int32_t dram_addr_rot        (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t dram_com_addr_rot    (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t dram_half_word_access(DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t dram_byte_access     (DT_UINT area, DT_UINT max_address, uint32_t bursts);
int32_t dram_memcpy_test     (DT_UINT area, DT_UINT max_address, uint32_t bursts);

int32_t test_mem_pattern     (DT_UINT area, DT_UINT max_address, DT_UINT pattern, uint32_t passes);
int32_t test_mem_alt_pattern (DT_UINT area, DT_UINT max_address, DT_UINT pattern, uint32_t passes);


