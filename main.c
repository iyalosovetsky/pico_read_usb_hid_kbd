#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "hardware/uart.h"
#include "hardware/irq.h"
#include "hardware/timer.h"
#include "pico/stdlib.h"
#include "bsp/board.h"
#include "tusb.h"

#define UART_ID uart0
#define BAUD_RATE 9600

// We are using pins 0 and 1, but see the GPIO function select table in the
// datasheet for information on which other pins can be used.
#define UART_TX_PIN 0
#define UART_RX_PIN 1

/// \tag::uart_advanced[]

#define PARITY    UART_PARITY_NONE
#define DATA_BITS 8
#define STOP_BITS 1


#define PROT_SOF 0x01
#define PROT_EOF 0x02
#define UART_BUFF_SIZE 0x08
#define PROT_BUFF_SIZE 0x04


static int chars_rxed = 0;
static uint8_t pos = 0;
static uint8_t ch[UART_BUFF_SIZE] = {0};
static uint8_t modCtrl = 0;
static uint8_t modLed = 0;
static uint8_t modChanged = 0;
// Keyboard LED control
static uint8_t lockModifiers = 0x01; // todo check for 0x00
static uint8_t prev_lockModifiers = 0xFF;
static uint8_t ledModifiers = 0x01; // todo check for 0x00
static uint8_t prev_ledModifiers = 0xFF;

static uint8_t devAddrArr[5] = {0};
static uint8_t instanceArr[5] = {0};
static uint8_t deviceCount = 0;
static uint8_t const keycode2ascii[128][2] =  { HID_KEYCODE_TO_ASCII };

static uint8_t process_kbd_report(hid_keyboard_report_t const *report);
void process_kbd_led(uint8_t dev_addr, uint8_t instance, hid_keyboard_report_t const *report);
void custom_led_send(void);


inline static uint8_t decShiftPos(uint8_t pos, uint8_t shift){
	
	return ((pos+UART_BUFF_SIZE-shift)%UART_BUFF_SIZE);
}
inline static uint8_t incShiftPos(uint8_t pos, uint8_t shift){
	
	return ((pos+UART_BUFF_SIZE+shift)%UART_BUFF_SIZE);
}

static void packet_parser(char * data, uint8_t pos){
	if((data[pos] == PROT_SOF) \
	&& (data[incShiftPos(pos, (PROT_BUFF_SIZE-1))] == PROT_EOF) \
	//&& (data[incShiftPos(pos, (1))] == ~data[incShiftPos(pos, (2))])
  )
	{
		modCtrl = data[incShiftPos(pos, (1))] / 0x10;
		modLed = (data[incShiftPos(pos, (1))] % 0x10) & 0x07;
		modChanged = 1;
	}
	
	
}


// RX interrupt handler
void on_uart_rx() {

    while (uart_is_readable(UART_ID)) {
        
		ch[pos] = uart_getc(UART_ID);
		
		if(ch[pos] == PROT_EOF){
			packet_parser(&ch[0], decShiftPos(pos, (PROT_BUFF_SIZE-1)));
		}
		
		pos = (pos + 1)%UART_BUFF_SIZE;	
    }
}



static void uartCustomInit(){
    // Set up our UART with a basic baud rate.
    uart_init(UART_ID, BAUD_RATE);

    // Set the TX and RX pins by using the function select on the GPIO
    // Set datasheet for more information on function select
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // Actually, we want a different speed
    // The call will return the actual baud rate selected, which will be as close as
    // possible to that requested
    int __unused actual = uart_set_baudrate(UART_ID, BAUD_RATE);

    // Set UART flow control CTS/RTS, we don't want these, so turn them off
    uart_set_hw_flow(UART_ID, false, false);

    // Set our data format
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);

    // Turn off FIFO's - we want to do this character by character
    uart_set_fifo_enabled(UART_ID, false);

    // Set up a RX interrupt
    // We need to set up the handler first
    // Select correct interrupt for the UART we are using
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;

    // And set up and enable the interrupt handlers
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);

    // Now enable the UART to send interrupts - RX only
    uart_set_irq_enables(UART_ID, true, false);

    // OK, all set up.
    // Lets send a basic string out, and then run a loop and wait for RX interrupts
    // The handler will count them, but also reflect the incoming data back with a slight change!
    // uart_puts(UART_ID, "\nHello, uart interrupts\n");
	
}	


static void appLed(void){
  // how  match blink for macro1
	#define MACROREAPEAT_1 5 
  // how  match blink for macro2
	#define MACROREAPEAT_2 10
  // 3 commands which recognize from uart in
	#define MACRO1 1 
	#define MACRO2 2
  #define MACRO3 3
	#define MACROBASE 4
  // interval of blinking in us
	#define TIMECONST 500000
  // variable to store  caps num  scroll before apply macro
	static uint8_t defaultLeds = 1;
  // variable to iterate count of blink for specified macro
	static uint32_t modRepeat = 0;
  static uint8_t modInit = 1;
	static uint32_t timeout = 0;
	if(modChanged == 1){
        
		if((time_us_32() > timeout )){
      putchar_raw(PROT_SOF);
      putchar_raw(0xfe);
      putchar_raw(modCtrl*0x10+modLed);
      putchar_raw(0);
      
      putchar_raw(~0xfe);
      putchar_raw(~(modCtrl*0x10+modLed));
      putchar_raw(~0);
      putchar_raw(PROT_EOF);
			switch(modCtrl){
				case MACRO1: 
					timeout = (time_us_32() + TIMECONST) % 0xffffffff;
					modRepeat++;
          if(modInit == 1) { ledModifiers =0; modInit = 0;}
					ledModifiers = ((ledModifiers & modLed) ^ modLed);
					if(modRepeat == MACROREAPEAT_1) modCtrl = MACROBASE;
					break;
				case MACRO2: 
					timeout = (time_us_32() + TIMECONST) % 0xffffffff;
					modRepeat++;
					if(modInit == 1) { ledModifiers =0; modInit = 0;}
					ledModifiers = ((ledModifiers & modLed) ^ modLed);
					if(modRepeat == MACROREAPEAT_2) modCtrl = MACROBASE;
					break;
        case MACRO3: // infinite blinking
					timeout = (time_us_32() + TIMECONST) % 0xffffffff;
					if(modInit == 1) { ledModifiers =0; modInit = 0;}
					ledModifiers = ((ledModifiers & modLed) ^ modLed);
					break;
				default:
					timeout = 0;				
					modRepeat = 0;
					modChanged = 0;
          modInit =1;					
					ledModifiers = lockModifiers;
					break;
			}
      custom_led_send(); // for what??
		}	
		
	} else 	defaultLeds = lockModifiers;
	
}



int main() {
  board_init();

  // init serial
  uartCustomInit();

  // TinyUSB, init host stack on configured RootHub Port
  tuh_init(BOARD_TUH_RHPORT);

  // turn on onboard led
  board_led_write(true);

  while(true) {
    tuh_task();  // tinyusb host task
    busy_wait_us(5000);
	  appLed(); //keyboard led control
    busy_wait_us(5000);

  }

  return 0;
}


//--------------------------------------------------------------------+
// TinyUSB Callbacks
//--------------------------------------------------------------------+

// called after all tuh_hid_mount_cb
void tuh_mount_cb(uint8_t dev_addr)
{
  // application set-up
  printf("A device with address %d is mounted\r\n", dev_addr);
}

// called before all tuh_hid_unmount_cb
void tuh_umount_cb(uint8_t dev_addr)
{
  // application tear-down
  printf("A device with address %d is unmounted \r\n", dev_addr);
}


// // Invoked when device with hid interface is mounted
// // Report descriptor is also available for use. tuh_hid_parse_report_descriptor()
// // can be used to parse common/simple enough descriptor.
// // Note: if report descriptor length > CFG_TUH_ENUMERATION_BUFSIZE, it will be skipped
// // therefore report_desc = NULL, desc_len = 0
// void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance, uint8_t const* desc_report, uint16_t desc_len) {
//   printf("HID device address = %d, instance = %d is mounted\r\n", dev_addr, instance);

//   if(tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD) {
//     if ( !tuh_hid_receive_report(dev_addr, instance) )
//     {
//       printf("Error: cannot request to receive report\r\n");
//     }
//   }
// }


// Invoked when device with hid interface is mounted
// Report descriptor is also available for use. tuh_hid_parse_report_descriptor()
// can be used to parse common/simple enough descriptor.
// Note: if report descriptor length > CFG_TUH_ENUMERATION_BUFSIZE, it will be skipped
// therefore report_desc = NULL, desc_len = 0
void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance, uint8_t const *desc_report, uint16_t desc_len)
{
  //printf("HID device address = %d, instance = %d is mounted\r\n", dev_addr, instance);

  if (tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD)
  {
    if (!tuh_hid_receive_report(dev_addr, instance))
    {
      //printf("Error: cannot request to receive report\r\n");
    }
    if( deviceCount < 5){
      devAddrArr[deviceCount] = dev_addr;
      instanceArr[deviceCount] = instance;
      deviceCount++;
    }
    if (lockModifiers != prev_lockModifiers)
    {
      tuh_hid_set_report(dev_addr, instance, 0, HID_REPORT_TYPE_OUTPUT, &lockModifiers, sizeof(lockModifiers));
      prev_lockModifiers = lockModifiers;
    }
  }
}

// Invoked when device with hid interface is un-mounted
void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance)
{
  //printf("HID device address = %d, instance = %d is unmounted\r\n", dev_addr, instance);
  devAddrArr[deviceCount] = dev_addr;
  instanceArr[deviceCount] = instance;
  deviceCount--;
}
void custom_led_send(void){
//      if (leds != prev_leds)

    for(uint8_t i =0; i <= deviceCount; i++)
      {
        tuh_hid_set_report(devAddrArr[i], instanceArr[i], 0, HID_REPORT_TYPE_OUTPUT, &lockModifiers, sizeof(lockModifiers));
        prev_lockModifiers = lockModifiers;
      }
}




// Invoked when received report from device via interrupt endpoint (key down and key up)
void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t instance, uint8_t const* report, uint16_t len)
{
  // printf("received report from HID device address = %d, instance = %d\r\n", dev_addr, instance);

  uint8_t const itf_protocol = tuh_hid_interface_protocol(dev_addr, instance);

  switch (itf_protocol)
  {
    case HID_ITF_PROTOCOL_KEYBOARD:
      // printf("HID receive boot keyboard report\r\n");
      //report->keycode[i]
      process_kbd_report( (hid_keyboard_report_t const*) report );
      process_kbd_led(dev_addr, instance, (hid_keyboard_report_t const *)report);
      
    break;
  }

  // continue to request to receive report
  if ( !tuh_hid_receive_report(dev_addr, instance) )
  {
    printf("Error: cannot request to receive report\r\n");
  }
}


//--------------------------------------------------------------------+
// Keyboard
//--------------------------------------------------------------------+

// look up new key in previous keys
static inline bool find_key_in_report(hid_keyboard_report_t const *report, uint8_t keycode)
{
  for (uint8_t i = 0; i < 6; i++)
  {
    if ((report->keycode[i] == keycode)) 
      return true;
  }

  return false;
}
// look up new modifier in previous keys
static inline bool find_modifier_in_report(hid_keyboard_report_t const *report, uint8_t modifier)
{

  if ((report->modifier == modifier)) 
    return true;


  return false;
}



static uint8_t process_kbd_report(hid_keyboard_report_t const *report)
{
  static hid_keyboard_report_t prev_report = { 0, 0, {0} }; // previous report to check key released
  static uint8_t prev_caps = 0;
  static uint8_t prev_num = 0;
  static uint8_t prev_scroll = 0;
  uint8_t modifier = 0;
  uint8_t last_modifier = 0;
  //------------- example code ignore control (non-printable) key affects -------------//
  if ( find_modifier_in_report(&prev_report, report->modifier) == false)
  {
    modifier = report->modifier;
    last_modifier = modifier;
  }
  for(uint8_t i=0; i<6; i++)
  {
    {
      if ( find_key_in_report(&prev_report, report->keycode[i]) && (last_modifier == 0) )
      {
        // exist in previous report means the current key is holding
      }else
      {

        last_modifier = 0;
        if((report->keycode[i] == 0x39) && (report->keycode[i] != prev_caps)){
          lockModifiers = lockModifiers ^ KEYBOARD_LED_CAPSLOCK;
        }
        if((report->keycode[i] == 0x53) && (report->keycode[i] != prev_num)){
          lockModifiers = lockModifiers ^ KEYBOARD_LED_NUMLOCK;
        }
        if((report->keycode[i] == 0x47) && (report->keycode[i] != prev_scroll)){
          lockModifiers = lockModifiers ^ KEYBOARD_LED_SCROLLLOCK;
        }
        // not existed in previous report means the current key is pressed
        bool const is_shift = report->modifier & (KEYBOARD_MODIFIER_LEFTSHIFT | KEYBOARD_MODIFIER_RIGHTSHIFT);


        putchar_raw(PROT_SOF);
        putchar_raw(lockModifiers);
        putchar_raw(report->modifier);
        putchar_raw(report->keycode[i]);
        
        putchar_raw(~lockModifiers);
        putchar_raw(~report->modifier);
        putchar_raw(~report->keycode[i]);
        putchar_raw(PROT_EOF);
        
        fflush(stdout); // flush right away, else nanolib will wait for newline
      }
    }
    // TODO example skips key released
  }

  prev_report = *report;
  return lockModifiers;
}
// void tuh_hid_report_sent_cb(uint8_t dev_addr, uint8_t instance, const uint8_t *report, uint16_t len){
//         process_kbd_led(dev_addr, instance, (hid_keyboard_report_t const *)report);
// }

void process_kbd_led(uint8_t dev_addr, uint8_t instance, hid_keyboard_report_t const *report){
    if (ledModifiers != prev_ledModifiers)
    {
      tuh_hid_set_report(dev_addr, instance, 0, HID_REPORT_TYPE_OUTPUT, &ledModifiers, sizeof(ledModifiers));
      prev_ledModifiers = ledModifiers;
    }
}

