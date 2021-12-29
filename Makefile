# Makefile for Embench-IoT

#TARGET = native
TARGET = scr1-arty
#TARGET = freedom-e310-arty

#BENCH = huffbench
#BENCH = md5sum
#BENCH = tarfind
#BENCH = nettle-aes

ABSOLUTE = --absolute

BUILDDIR = bd/${TARGET}
RESULTDIR = result

ifeq (${TARGET},native)
ARCH = native
CHIP = debug-gcc
BOARD = default
CPU_MHZ = --cpu-mhz=3000
GDB = gdb

OPT_FLAGS_SIZE  = -Os
OPT_FLAGS_SPEED = -O2

BUILD_FLAGS_DUMMYLIB = --ldflags="-nostartfiles" --dummy-libs "crt0 libc libgcc libm"
BUILD_FLAGS_USERLIB  = --user-libs "-Wl,--start-group -lc -lgcc -lm -Wl,--end-group"

else ifeq (${TARGET},scr1-arty)
ARCH = riscv32
CHIP = generic
BOARD = scr1-arty

GDB = riscv64-unknown-elf-gdb
GDBCONF = -x ../scr1-sdk/gdbconf
OPENOCD = /opt/syntacore/openocd-0.10.0-1974/bin/openocd
OPENOCDCFG = -f interface/ftdi/olimex-arm-usb-ocd-h.cfg -f target/syntacore_riscv.cfg

TARGET_INC = ${SCR1_SDK_PATH}/sw/hello/common
SCR1_CMN = ${SCR1_SDK_PATH}/sw/hello/build.arty_scr1.tcm.o2/common
SCR1_SUPPORT_OBJS = ${SCR1_CMN}/printf.o ${SCR1_CMN}/syscalls.o ${SCR1_CMN}/nlib.o ${SCR1_CMN}/uart.o ${SCR1_CMN}/ncrt0.o

OPT_FLAGS_SIZE  = -Os -msave-restore
OPT_FLAGS_SPEED = -O2
#OPT_FLAGS_SPEED += -mstrict-align -msmall-data-limit=8 -fno-common

CFLAGS_USERLIB = -I${TARGET_INC}
BUILD_FLAGS_DUMMYLIB = --dummy-libs "crt0 libc libgcc libm"
#BUILD_FLAGS_USERLIB  = --ldflags "${SCR1_SUPPORT_OBJS}" --user-libs "-Wl,--start-group -lc -lgcc -lm -Wl,--end-group"
BUILD_FLAGS_USERLIB  = --ldflags "${SCR1_SUPPORT_OBJS}" --user-libs "-lm -lc -lgcc"
#TIMEOUT = --timeout=600

else ifeq (${TARGET},freedom-e310-arty)
ARCH = riscv32
CHIP = generic
BOARD = freedom-e310-arty

GDB = riscv64-unknown-elf-gdb
GDBCONF = -x ../freedom-e-sdk/gdbconf
OPENOCD = /opt/SiFive/riscv-openocd-0.10.0-2020.12.1-x86_64-linux-ubuntu14/bin/openocd
OPENOCDCFG = -f ../freedom-e-sdk/bsp/freedom-e310-arty/openocd.cfg
# Does not work. Addresses must be updated.
#OPENOCDCFG = -f interface/ftdi/olimex-arm-usb-ocd-h.cfg -f board/sifive-e31arty.cfg

OPT_FLAGS_SIZE  = -Os -msave-restore
OPT_FLAGS_SPEED = -O2
#OPT_FLAGS_SPEED += -mcpu=sifive-e31

TARGET_INC = ${FREEDOM_E_SDK_PATH}/bsp/freedom-e310-arty/install/include
TARGET_LIB = ${FREEDOM_E_SDK_PATH}/bsp/freedom-e310-arty/install/lib/debug/

CFLAGS_USERLIB = -I${TARGET_INC}
BUILD_FLAGS_DUMMYLIB = --dummy-libs "crt0 libc libgcc libm"
BUILD_FLAGS_USERLIB  = --ldflags "-L ${TARGET_LIB}" --user-libs "-Wl,--start-group -lc -lgcc -lm -lmetal -lmetal-gloss -Wl,--end-group"
TIMEOUT = --timeout=600

else
	$(error unknown TARGET: ${TARGET}.)
endif

ifdef BENCH
BENCH_FLAGS = --benchmark $(BENCH)
EXE = bd/${TARGET}/src/$(BENCH)/$(BENCH)
else
BENCH_FLAGS = --exclude md5sum primecount tarfind
endif

.PHONY : all build_size build_speed size speed gdb clean clean_all

all:
	${MAKE} clean
	${MAKE} build_dummylib_for_size
	${MAKE} size  | tee ${RESULTDIR}/${TARGET}_size_for_size
	${MAKE} clean
	${MAKE} build_userlib_for_size
	${MAKE} speed | tee ${RESULTDIR}/${TARGET}_speed_for_size
	${MAKE} clean
	${MAKE} build_dummylib_for_speed
	${MAKE} size  | tee ${RESULTDIR}/${TARGET}_size_for_speed
	${MAKE} clean
	${MAKE} build_userlib_for_speed
	${MAKE} speed | tee ${RESULTDIR}/${TARGET}_speed_for_speed

build_dummylib_for_size:  OPT_FLAGS=--cflags "${OPT_FLAGS_SIZE} ${CFLAGS_DUMMYLIB}"
build_dummylib_for_size:  BUILD_FLAGS=${BUILD_FLAGS_DUMMYLIB}
build_dummylib_for_size:  build

build_userlib_for_size:   OPT_FLAGS=--cflags "${OPT_FLAGS_SIZE} ${CFLAGS_USERLIB}"
build_userlib_for_size:   BUILD_FLAGS=${BUILD_FLAGS_USERLIB}
build_userlib_for_size:   build

build_dummylib_for_speed: OPT_FLAGS=--cflags "${OPT_FLAGS_SPEED} ${CFLAGS_DUMMYLIB}"
build_dummylib_for_speed: BUILD_FLAGS=${BUILD_FLAGS_DUMMYLIB}
build_dummylib_for_speed: build

build_userlib_for_speed:  OPT_FLAGS=--cflags "${OPT_FLAGS_SPEED} ${CFLAGS_USERLIB}"
build_userlib_for_speed:  BUILD_FLAGS=${BUILD_FLAGS_USERLIB}
build_userlib_for_speed:  build

build:
	./build_all.py -v --arch ${ARCH} --chip ${CHIP} --board ${BOARD} --builddir ${BUILDDIR} ${BENCH_FLAGS} ${CPU_MHZ} ${OPT_FLAGS} ${BUILD_FLAGS}
size:
	./benchmark_size.py ${ABSOLUTE} --builddir ${BUILDDIR} ${BENCH_FLAGS}
speed:
	./benchmark_speed.py ${ABSOLUTE} --target-module run_${TARGET} --builddir ${BUILDDIR} ${BENCH_FLAGS} ${TIMEOUT} ${CPU_MHZ}

gdb:
ifndef BENCH
	$(error BENCH is not defined.)
endif
	${GDB} -q ${GDBCONF} ${EXE}

openocd:
	${OPENOCD} ${OPENOCDCFG}

clean:
	rm -rf ${BUILDDIR}

clean_all:
	rm -rf bd logs
