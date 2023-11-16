#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "hardware/uart.h"
#include "pico/stdlib.h"
#include "bsp/board.h"
#include "tusb.h"

#define UART_ID uart0
#define BAUD_RATE 9600
#define UART_TX_PIN 0
#define UART_RX_PIN 1

static uint8_t const keycode2ascii[128][2] =  { HID_KEYCODE_TO_ASCII };

static uint8_t process_kbd_report(hid_keyboard_report_t const *report);
void process_kbd_led(uint8_t dev_addr, uint8_t instance, hid_keyboard_report_t const *report);



int main() {
  board_init();

  // init serial
  uart_init(UART_ID, BAUD_RATE);
  gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
  gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

  // TinyUSB, init host stack on configured RootHub Port
  tuh_init(BOARD_TUH_RHPORT);

  // turn on onboard led
  board_led_write(true);

  while(true) {
    tuh_task();  // tinyusb host task
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

// Keyboard LED control
static uint8_t leds = 0x01; // todo check for 0x00
static uint8_t prev_leds = 0xFF;
// Invoked when device with hid interface is mounted
// Report descriptor is also available for use. tuh_hid_parse_report_descriptor()
// can be used to parse common/simple enough descriptor.
// Note: if report descriptor length > CFG_TUH_ENUMERATION_BUFSIZE, it will be skipped
// therefore report_desc = NULL, desc_len = 0
void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance, uint8_t const *desc_report, uint16_t desc_len)
{
  printf("HID device address = %d, instance = %d is mounted\r\n", dev_addr, instance);

  if (tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD)
  {
    if (!tuh_hid_receive_report(dev_addr, instance))
    {
      printf("Error: cannot request to receive report\r\n");
    }
    if (leds != prev_leds)
    {
      tuh_hid_set_report(dev_addr, instance, 0, HID_REPORT_TYPE_OUTPUT, &leds, sizeof(leds));
      prev_leds = leds;
    }
  }
}



// Invoked when device with hid interface is un-mounted
void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance) {
  printf("HID device address = %d, instance = %d is unmounted\r\n", dev_addr, instance);
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

// inline static uint8_t Fast_Fix(hid_keyboard_report_t const *report, uint8_t i){
//     if(report->keycode[i] == 0x0a)
//          return 0x03;
//     else return report->keycode[i];     
// }

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
          leds = leds ^ KEYBOARD_LED_CAPSLOCK;
          //todo
        }
        if((report->keycode[i] == 0x53) && (report->keycode[i] != prev_num)){
          leds = leds ^ KEYBOARD_LED_NUMLOCK;
          //todo
        }
        if((report->keycode[i] == 0x47) && (report->keycode[i] != prev_scroll)){
          leds = leds ^ KEYBOARD_LED_SCROLLLOCK;
          //todo
        }
        // not existed in previous report means the current key is pressed
        bool const is_shift = report->modifier & (KEYBOARD_MODIFIER_LEFTSHIFT | KEYBOARD_MODIFIER_RIGHTSHIFT);
        //for test
        // fix 0x0A
        // uint8_t c = Fast_Fix(report,i);


        putchar_raw(0x01);
        putchar_raw(leds);
        putchar_raw(report->modifier);
        putchar_raw(report->keycode[i]);
        
        putchar_raw(~leds);
        putchar_raw(~report->modifier);
        putchar_raw(~report->keycode[i]);
        putchar_raw(0x02);
        
        fflush(stdout); // flush right away, else nanolib will wait for newline
      }
    }
    // TODO example skips key released
  }

  prev_report = *report;
  return leds;
}

void process_kbd_led(uint8_t dev_addr, uint8_t instance, hid_keyboard_report_t const *report){
    if (leds != prev_leds)
    {
      tuh_hid_set_report(dev_addr, instance, 0, HID_REPORT_TYPE_OUTPUT, &leds, sizeof(leds));
      prev_leds = leds;
    }
}

