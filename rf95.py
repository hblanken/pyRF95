#!/usr/bin/env python3

import time
import sys
import spidev

FXOSC=32000000
FSTEP = FXOSC / 524288

# Register names (LoRa Mode, from table 85)
REG_00_FIFO=0x00
REG_01_OP_MODE=0x01
REG_02_RESERVED=0x02
REG_03_RESERVED=0x03
REG_04_RESERVED=0x04
REG_05_RESERVED=0x05
REG_06_FRF_MSB=0x06
REG_07_FRF_MID=0x07
REG_08_FRF_LSB=0x08
REG_09_PA_CONFIG=0x09
REG_0A_PA_RAMP=0x0a
REG_0B_OCP=0x0b
REG_0C_LNA=0x0c
REG_0D_FIFO_ADDR_PTR=0x0d
REG_0E_FIFO_TX_BASE_ADDR=0x0e
REG_0F_FIFO_RX_BASE_ADDR=0x0f
REG_10_FIFO_RX_CURRENT_ADDR=0x10
REG_11_IRQ_FLAGS_MASK=0x11
REG_12_IRQ_FLAGS=0x12
REG_13_RX_NB_BYTES=0x13
REG_14_RX_HEADER_CNT_VALUE_MSB=0x14
REG_15_RX_HEADER_CNT_VALUE_LSB=0x15
REG_16_RX_PACKET_CNT_VALUE_MSB=0x16
REG_17_RX_PACKET_CNT_VALUE_LSB=0x17
REG_18_MODEM_STAT=0x18
REG_19_PKT_SNR_VALUE=0x19
REG_1A_PKT_RSSI_VALUE=0x1a
REG_1B_RSSI_VALUE=0x1b
REG_1C_HOP_CHANNEL=0x1c
REG_1D_MODEM_CONFIG1=0x1d
REG_1E_MODEM_CONFIG2=0x1e
REG_1F_SYMB_TIMEOUT_LSB=0x1f
REG_20_PREAMBLE_MSB=0x20
REG_21_PREAMBLE_LSB=0x21
REG_22_PAYLOAD_LENGTH=0x22
REG_23_MAX_PAYLOAD_LENGTH=0x23
REG_24_HOP_PERIOD=0x24
REG_25_FIFO_RX_BYTE_ADDR=0x25
REG_26_MODEM_CONFIG3=0x26
REG_28_FREQ_ERROR=0x28
REG_31_DETECT_OPT=0x31
REG_37_DETECTION_THRESHOLD=0x37

REG_40_DIO_MAPPING1=0x40
REG_41_DIO_MAPPING2=0x41
REG_42_VERSION=0x42

REG_4B_TCXO=0x4b
REG_4D_PA_DAC=0x4d
REG_5B_FORMER_TEMP=0x5b
REG_61_AGC_REF=0x61
REG_62_AGC_THRESH1=0x62
REG_63_AGC_THRESH2=0x63
REG_64_AGC_THRESH3=0x64

# REG_01_OP_MODE                             0x01
LONG_RANGE_MODE=0x80
ACCESS_SHARED_REG=0x40
MODE=0x07
MODE_SLEEP=0x00
MODE_STDBY=0x01
MODE_FSTX=0x02
MODE_TX=0x03
MODE_FSRX=0x04
MODE_RXCONTINUOUS=0x05
MODE_RXSINGLE=0x06
MODE_CAD=0x07

# REG_09_PA_CONFIG                           0x09
PA_SELECT=0x80
MAX_POWER=0x70
OUTPUT_POWER=0x0f

# REG_0A_PA_RAMP                             0x0a
LOW_PN_TX_PLL_OFF=0x10
PA_RAMP=0x0f
PA_RAMP_3_4MS=0x00
PA_RAMP_2MS=0x01
PA_RAMP_1MS=0x02
PA_RAMP_500US=0x03
PA_RAMP_250US=0x0
PA_RAMP_125US=0x05
PA_RAMP_100US=0x06
PA_RAMP_62US=0x07
PA_RAMP_50US=0x08
PA_RAMP_40US=0x09
PA_RAMP_31US=0x0a
PA_RAMP_25US=0x0b
PA_RAMP_20US=0x0c
PA_RAMP_15US=0x0d
PA_RAMP_12US=0x0e
PA_RAMP_10US=0x0f

# REG_0B_OCP                                 0x0b
OCP_ON=0x20
OCP_TRIM=0x1f

# REG_0C_LNA                                 0x0c
LNA_GAIN=0xe0
LNA_BOOST=0x03
LNA_BOOST_DEFAULT=0x00
LNA_BOOST_150PC=0x11

# REG_11_IRQ_FLAGS_MASK                      0x11
RX_TIMEOUT_MASK=0x80
RX_DONE_MASK=0x40
PAYLOAD_CRC_ERROR_MASK=0x20
VALID_HEADER_MASK=0x10
TX_DONE_MASK=0x08
CAD_DONE_MASK=0x04
FHSS_CHANGE_CHANNEL_MASK=0x02
CAD_DETECTED_MASK=0x01

# REG_12_IRQ_FLAGS                           0x12
RX_TIMEOUT=0x80
RX_DONE=0x40
PAYLOAD_CRC_ERROR=0x20
VALID_HEADER=0x10
TX_DONE=0x08
CAD_DONE=0x04
FHSS_CHANGE_CHANNEL=0x02
CAD_DETECTED=0x01

# REG_18_MODEM_STAT                          0x18
RX_CODING_RATE=0xe0
MODEM_STATUS_CLEAR=0x10
MODEM_STATUS_HEADER_INFO_VALID=0x08
MODEM_STATUS_RX_ONGOING=0x04
MODEM_STATUS_SIGNAL_SYNCHRONIZED=0x02
MODEM_STATUS_SIGNAL_DETECTED=0x01

# REG_1C_HOP_CHANNEL                         0x1c
PLL_TIMEOUT=0x80
RX_PAYLOAD_CRC_IS_ON=0x40
FHSS_PRESENT_CHANNEL=0x3f

# REG_1D_MODEM_CONFIG1                       0x1d
BW=0xc0
BW_125KHZ=0x00
BW_250KHZ=0x40
BW_500KHZ=0x80
BW_RESERVED=0xc0
CODING_RATE=0x38
CODING_RATE_4_5=0x00
CODING_RATE_4_6=0x08
CODING_RATE_4_7=0x10
CODING_RATE_4_8=0x18
IMPLICIT_HEADER_MODE_ON=0x04
RX_PAYLOAD_CRC_ON=0x02
LOW_DATA_RATE_OPTIMIZE=0x01

# REG_1E_MODEM_CONFIG2                       0x1e
SPREADING_FACTOR=0xf0
SPREADING_FACTOR_64CPS=0x60
SPREADING_FACTOR_128CPS=0x70
SPREADING_FACTOR_256CPS=0x80
SPREADING_FACTOR_512CPS=0x90
SPREADING_FACTOR_1024CPS=0xa0
SPREADING_FACTOR_2048CPS=0xb0
SPREADING_FACTOR_4096CPS=0xc0
TX_CONTINUOUS_MOE=0x08
AGC_AUTO_ON=0x04
SYM_TIMEOUT_MSB=0x03

# REG_4D_PA_DAC                              0x4d
PA_DAC_DISABLE=0x04
PA_DAC_ENABLE=0x07

MAX_MESSAGE_LEN=255

# default params
Bw125Cr45Sf128 = (0x72,   0x74,    0x00)
Bw500Cr45Sf128 = (0x92,   0x74,    0x00)
Bw31_25Cr48Sf512 = (0x48,   0x94,    0x00)
Bw125Cr48Sf4096 = (0x78,   0xc4,    0x00)

# SPI
SPI_WRITE_MASK=0x80

# Modes
RHModeInitialising=0
RHModeSleep=1
RHModeIdle=2
RHModeTx=3
RHModeRx=4
RHModeCad=5

class RF95:
	def __init__(self,cs=0):
		# init class
		self.spi = spidev.SpiDev()
		self.cs = cs
		self.mode = RHModeInitialising

	def init(self):
		# open SPI and initialize RF95
		self.spi.open(0,self.cs)
		self.spi.max_speed_hz = 488000
		self.spi.close()

		# set sleep mode and LoRa mode
		self.spi_write(REG_01_OP_MODE, MODE_SLEEP | LONG_RANGE_MODE)
		
		time.sleep(0.01)		
		# check if we are set
		if self.spi_read(REG_01_OP_MODE) != (MODE_SLEEP | LONG_RANGE_MODE):
			return False

		# set up FIFO
		self.spi_write(REG_0E_FIFO_TX_BASE_ADDR, 0)
		self.spi_write(REG_0F_FIFO_RX_BASE_ADDR, 0)

		self.set_mode_idle()

		self.set_modem_config(Bw125Cr45Sf128)
		self.set_preamble_lenght(8)
		
		return True

	def spi_write(self, reg, data):
		self.spi.open(0,self.cs)
		self.spi.xfer2([reg | SPI_WRITE_MASK, data])
		self.spi.close()

	def spi_read(self, reg):
		self.spi.open(0,self.cs)
		data = self.spi.xfer2([reg & ~SPI_WRITE_MASK, 0])
		self.spi.close()
		return data[1]

	def spi_write_data(self, reg, data):
		self.spi.open(0, self.cs)
		self.spi.xfer2([reg | SPI_WRITE_MASK] + data)
		self.spi.close()

	def set_frequency(self, freq):
		freq_value = int((freq * 1000000.0) / FSTEP)
		
		self.spi_write(REG_06_FRF_MSB, (freq_value>>16)&0xff)
		self.spi_write(REG_07_FRF_MID, (freq_value>>8)&0xff)
		self.spi_write(REG_08_FRF_LSB, (freq_value)&0xff)
	
#	def set_modem_params(self, implicit_explicit, error_coding, bandwidth, spreading_factor, optimize_low_datarate):
#		self.spi_write(REG_1D_MODEM_CONFIG1, implicit_explicit | error_coding | bandwidth)
#		self.spi_write(REG_1E_MODEM_CONFIG2, spreading_factor | CRC_ON)
#		self.spi_write(REG_26_MODEM_CONFIG3, optimize_low_datarate | 0x04)
#		self.spi_write(REG_31_DETECT_OPT, (self.spi_read(REG_31_DETECT_OPT) & 0xf8) | (lambda: 0x05, lambda: 0x03)[spreading_factor == SPREADING_FACTOR_64CPS])
#		self.spi_write(REG_37_DETECTION_THRESHOLD, (lambda: 0x0c, lambda: 0x0a)[spreading_factor == SPREADING_FACTOR_64CPS])
#		
#		self.spi_write(REG_22_PAYLOAD_LENGTH, 255)
#		self.spi_write(REG_13_RX_NB_BYTES, 255)

	def set_mode_idle(self):
		if self.mode != RHModeIdle:
			self.spi_write(REG_01_OP_MODE, MODE_STDBY)
			self.mode = RHModeIdle

	def sleep(self):
		if self.mode != RHModeSleep:
			self.spi_write(REG_01_OP_MODE, MODE_SLEEP)
			self.mode = RHModeSleep
		return True

	def set_mode_rx(self):
		if self.mode != RHModeRx:
			self.spi_write(REG_01_OP_MODE, MODE_RXCONTINUOUS)
			self.spi_write(REG_40_DIO_MAPPING1, 0x00)
			self.mode = RHModeRx

	def set_mode_tx(self):
		if self.mode != RHModeTx:
			self.spi_write(REG_01_OP_MODE, MODE_TX)
			self.spi_write(REG_40_DIO_MAPPING1, 0x40)
			self.mode = RHModeTx	
		return True


	def set_tx_power(self, power):
		if power>23:
			power=23
		if power<5:
			power=5
		# A_DAC_ENABLE actually adds about 3dBm to all 
		# power levels. We will us it for 21, 22 and 23dBm

		if power>20:
			self.spi_write(REG_4D_PA_DAC, PA_DAC_ENABLE)
			power = power -3
		else:
			self.spi_write(REG_4D_PA_DAC, PA_DAC_DISABLE)

		self.spi_write(REG_09_PA_CONFIG, PA_SELECT | (power-5))

	def set_modem_config(self, config):
		self.spi_write(REG_1D_MODEM_CONFIG1, config[0])
		self.spi_write(REG_1E_MODEM_CONFIG2, config[1])
		self.spi_write(REG_26_MODEM_CONFIG3, config[2])
		
	def set_preamble_lenght(self, lenght):
		self.spi_write(REG_20_PREAMBLE_MSB, lenght >> 8)
		self.spi_write(REG_21_PREAMBLE_LSB, lenght & 0xff)


	def send(self, data):
		if len(data) > MAX_MESSAGE_LEN:
			return False
		
		self.set_mode_idle()
		# beggining of FIFO
		self.spi_write(REG_0D_FIFO_ADDR_PTR, 0)

		# write data
		self.spi_write_data(REG_00_FIFO, data)
		self.spi_write(REG_22_PAYLOAD_LENGTH, len(data))

		self.set_mode_tx()
		return True

	def str_to_data(self, string):
		data = []
		for i in string:
			data.append(ord(i))
		return data

	
if __name__ == "__main__":
	rf95 = RF95(0)
	if not rf95.init():
		print("RF95 not found")
		quit(1)
	else:
		print("RF95 LoRa mode ok")

	rf95.set_frequency(868.5)
	rf95.set_tx_power(5)
	#rf95.set_modem_config(Bw31_25Cr48Sf512)

	rf95.send(rf95.str_to_data("$ola ke ase"))
	time.sleep(2)
	rf95.set_mode_idle()


