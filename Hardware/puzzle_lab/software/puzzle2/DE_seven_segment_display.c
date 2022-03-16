#include <sys/alt_stdio.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "alt_types.h"
#include "sys/times.h"
#include "altera_avalon_pio_regs.h"
#include "system.h"
#define CHARLIM 256	//Maximum character length of what the user places in memory.  Increase to allow longer sequences
#define CLOCKINIT 30005	//Initial speed of the display.  This is a good starting point
#define UPDATECLOCKAMT 8000	//Incremental amount the display updates by when speeding up or slowing down
#define QUITLETTER '~' 		// Letter to kill all processing

#include "altera_up_avalon_accelerometer_spi.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "sys/alt_irq.h"

void initializeDisplay();
void updateText();
char getTxt(char curr);
int getActualText();
void clearActualText();
int updateTimer(int tmr, int speedup_tog, int slowdown_tog);
int updateLocation(int loc, int len);
void updatePBState(int button_datain);
int getBinLowLow(char letter);
int getBinLow(char letter);
int getBin(char letter);
int getBinHigh(char letter);
int getBinHighHigh(char letter);
int getBinaryLetter(char letter);
void print(int let5, int let4, int let3, int let2, int let1, int let0);
void print_letters(char let5, char let4, char let3, char let2, char let1, char let0, int state);


char prevLetter;	//The last letter the user entered, used for determining whether or not the display has been updated
char enteredText[CHARLIM]; //The text that the user enters
char text[2*CHARLIM];//The text that has been adjusted for the allowed letters
int pause, reverse, toggle, speedup_toggle, slowdown_toggle, dance_state, dancing, dance_dir, upsideDown, length, re_enter, disp_off, flag;
int timer = CLOCKINIT;  //Standard speed for movement
int life = 1023;


void print_data(char *accel_x, char *accel_y, char *switchdata, char *buttondata){
	char *printMsg;
	asprintf(&printMsg, "<--> %s %s <--> %s <--> %s <--> \n", accel_x, accel_y, switchdata, buttondata); 	// Print out the strings
	alt_putstr(printMsg);
	free(printMsg);
	memset(text, 0, 2*CHARLIM);
}

void send_text(char *text) {
	char *printMsg;
	asprintf(&printMsg, "<--> %s <--> \n", text); 	// Print out the strings
	alt_putstr(printMsg);
	free(printMsg);
	memset(text, 0, 2*CHARLIM);								// Empty the text buffer for next input
}

char generate_text(char curr, int *length, char *text, int *running) {
	if(curr == '\n') return curr;								// If the line is empty, return nothing.
	int idx = 0;										// Keep track of how many characters have been sent down for later printing
	char newCurr = curr;

	while (newCurr != EOF && newCurr != '\n'){						// Keep reading characters until we get to the end of the line
		if (newCurr == QUITLETTER) { *running = 0; }					// If quitting letter is encountered, setting running to 0
		text[idx] = newCurr;								// Add the next letter to the text buffer
		idx++;										// Keep track of the number of characters read
		newCurr = alt_getchar();							// Get the next character
	}
	*length = idx;

	return newCurr;
}

void interpret_command(char* command)
{
	if ( strcmp(command, "W") == 0 )			{ ; }
	else if ( strcmp(command, "L") == 0 )		{ ; }
	else if ( strcmp(command, "LIFE+") == 0 )	{
		if (life != 1023){
			life = ((life + 1) * 2) - 1;
		}
	}
	else if ( strcmp(command, "LIFE-") == 0 )	{
		if (life != 1){
			life = ((life + 1) / 2) - 1;
		}
	}
	else if ( strcmp(command, "p") == 0 )		{ ; }
	else if ( strcmp(command, "r") == 0 )		{ life = 1023; }
	else										{ ; }
}

void read_chars() {
	char text[2*CHARLIM];									// The buffer for the printing text
	char prevLetter = '!';
	int length = 0;
	int running = 1;

	prevLetter = alt_getchar();							// Extract the first character (and create a hold until one arrives)
	prevLetter = generate_text(prevLetter, &length, text, &running);		// Process input text
	//print_text(text, length);							// Print input text

	if (strcmp(text, "") !=0 )	{ interpret_command(text); }
}

void output_switch( int new, int old )
{
	char text[2*CHARLIM];

	int x = new^old;
	int switchnum;

	if ( x != 0 ){
		for (int i = 1; i < 513; i=i*2){
			if( x == i ){
				switchnum = log2(i);
				if (new>old) 	{ sprintf(text, "SW%d ON\n", switchnum + 1); send_text(text); }
				else 			{ sprintf(text, "SW%d OFF\n", switchnum + 1); send_text(text); }
			}
		}
	}
}

void output_button ( int new, int old)
{
	char text[2*CHARLIM];

	int x = new^old;

	if ( x != 0 ){
		if( x == 1 ){
			if (new<old) 	{ sprintf(text, "B1 pressed\n"); send_text(text); }
		}
		if( x == 2 ){
			if (new<old) 	{ sprintf(text, "B2 pressed\n"); send_text(text); }
		}
		if( x == 3 ){
			if (old == 1) 		{ sprintf(text, "B1 pressed\n"); send_text(text); }
			else if (old ==2 ) 	{ sprintf(text, "B2 pressed\n"); send_text(text); }
		}
	}
}


#define OFFSET -32
#define PWM_PERIOD 16

alt_8 pwm = 0;
alt_u8 led;
int level;

void led_write(alt_u8 led_pattern) {
    IOWR(LED_BASE, 0, led_pattern);
}

void convert_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

void sys_timer_isr() {
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);

    if (pwm < abs(level)) {

        if (level < 0) {
            led_write(led << 1);
        } else {
            led_write(led >> 1);
        }

    } else {
        led_write(led);
    }

    if (pwm > PWM_PERIOD) {
        pwm = 0;
    } else {
        pwm++;
    }
}

void timer_init(void * isr) {
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0003);
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_BASE, 0x0900);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_BASE, 0x0000);
    alt_irq_register(TIMER_IRQ, 0, isr);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0007);
}

int main(){

	// ACCELEROMTER INITIALISE
	alt_32 x_read;
	alt_32 y_read;
	alt_32 z_read;
	alt_up_accelerometer_spi_dev * acc_dev;
	acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
	if (acc_dev == NULL) { // if return 1, check if the spi ip name is "accelerometer_spi"
		return 1;
	}
	timer_init(sys_timer_isr);

	// ACCELEROMTER DATA
	char accel_data_x[4*CHARLIM];
	char accel_data_y[4*CHARLIM];
	char accel_data_z[4*CHARLIM];
	char switch_data[4*CHARLIM];
	char button_data[4*CHARLIM];

	// SWITCH
	int switch_datain, switch_data_old = IORD_ALTERA_AVALON_PIO_DATA(SWITCH_BASE);
	// BUTTON
	int button_datain, button_data_old = IORD_ALTERA_AVALON_PIO_DATA(BUTTON_BASE);

	alt_32 LED_data;

	// HEX DISPLAYS

	while (1) {
		IOWR_ALTERA_AVALON_PIO_DATA(LED_BASE, life);

		/* <--> SENDING DATA <--> */
		alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
		sprintf(accel_data_x, "%x", x_read);
		alt_up_accelerometer_spi_read_y_axis(acc_dev, & y_read);
		sprintf(accel_data_y, "%x", y_read);
		//alt_up_accelerometer_spi_read_z_axis(acc_dev, & z_read);
		//sprintf(accel_data_z, "%x", z_read);

		//SWITCH
		//switch_datain = IORD_ALTERA_AVALON_PIO_DATA(SWITCH_BASE);
		//output_switch( switch_datain, switch_data_old );
		//switch_data_old = switch_datain;
		switch_datain = IORD_ALTERA_AVALON_PIO_DATA(SWITCH_BASE);
		sprintf(switch_data, "%x", switch_datain);

		// BUTTON
		//button_datain = IORD_ALTERA_AVALON_PIO_DATA(BUTTON_BASE);
		//output_button( button_datain, button_data_old );
		//button_data_old = button_datain;
		button_datain = IORD_ALTERA_AVALON_PIO_DATA(BUTTON_BASE);
		sprintf(button_data, "%x", button_datain);

		print_data(accel_data_x, accel_data_y, switch_data, button_data);

		/* <--> RECIEVING DATA <--> */
		//read_chars();

		//sprintf(input_command, "%s", read_chars());
		//interpret_command(input_command);

		//sprintf(to_text, "Got read thing: %s\n", read_chars());
		//send_text(to_text);*/

	}

	return 0;
}

//Does initial setup of display
void initializeDisplay(){
	//These controls determine what functions the display is executing:
	flag = 0;
	pause = 0;
	reverse = 0;
	upsideDown = 0;
	//These controls handle the toggling of the switches; initially all of the toggled functions are off:
	toggle = 0;
	speedup_toggle = 0;
	slowdown_toggle = 0;
	dancing = 0;
	re_enter = 0;
	dance_state = 2; //Start with the letters in the middle
	//First Turn all six of the seven segment displays off
	print(getBin('!'), getBin('!'), getBin('!'), getBin('!'), getBin('!'), getBin('!'));
	prevLetter = '!';
	//Give the user instructions using the HAL commands
	alt_putstr("Hello from Nios II!\n");
	alt_putstr("Type what you would like to display and press ENTER\n");
	prevLetter = getTxt(prevLetter);	//Snag what the user put in
	length = getActualText();		//Adjust for special characters such as 'W' or 'M'
	alt_putstr("Got it!  If you want to change the text, press KEY1\n");
}
//Updates the text from the console once the program is running
void updateText(){
	if (re_enter){
		  alt_putstr("Put your new text into the console and press ENTER\n");
		  prevLetter = '!';
		  prevLetter = getTxt(prevLetter);
		  length = getActualText();		//Adjust for special characters such as 'W' or 'M'
		  if(length > 0)
			  text[length-1] = '\0';		//Get rid of any extra stuff at the end
		  alt_putstr("Got it!  If you want to change the text, press KEY1 \n");
		  re_enter = 0;	//We don't want to retrigger the entering process until the user does
	}
	return;
}
//Gets the text the user placed on the console
char getTxt(char curr){
	if(curr == '\n')
		return curr;
	int idx = 0;	//Keep track of what we are adding
	char newCurr = curr;
	//Keep adding characters until we get to the end of the line
	while (newCurr != '\n'){
		enteredText[idx] = newCurr;	//Add the next letter to the entered text register
		idx ++;
		newCurr = alt_getchar();	//Get the next character
	}
	length = idx;
	return newCurr;
}
//Takes the user's input and only uses the allowed letters.  Returns the length of the string entered
int getActualText(){
	int idx = 0;	//We need two indicies because the entered and actual text sequences need not be aligned
	char currentLetter; //Keeps track of the character we are wanting to add
	//Go through each letter in the entered text
	for (int i = 0; i <= length; i++){
		currentLetter = enteredText[i];
		if (currentLetter > 96){
			//Gets only the uppercase letter
			currentLetter -= 32;
		}
		switch(currentLetter){
		case 'M':
			//We build the letter "M" from two "n's," so we need to change the index twice in the actual text
			text[idx] = 'N';
			text[idx + 1] = 'N';
			idx += 2;
			break;
		case 'W':
			//We build the letter "W" from two "v's," so we need to change the index twice in the actual text
			text[idx] = 'V';
			text[idx + 1] = 'V';
			idx += 2;
			break;
		default:
			//Copy the new letter into the actual text
			text[idx] = currentLetter;
			idx++;
		}


	}
	return idx;
}
//This function clears the text on the display:
void clearActualText(){
	for(int i = 0; i <= length; i++){
		text[i] = '\0';
	}
	return;
}
//This function updates the timer based on whether the user has toggled a speedup or slowdown
int updateTimer(int tmr, int speedup_tog, int slowdown_tog){
	if (speedup_tog){
		//If the user wishes to speed the display up by pressing KEY0
		if ((tmr - UPDATECLOCKAMT) > 0)//We don't want the timer to go negative
			return tmr - UPDATECLOCKAMT;
	}
	else if (slowdown_tog)
		//If the user wishes to slow the display down by pressing KEY1
		return tmr + UPDATECLOCKAMT;
	//Return the modified timer amount so we can update what is stored in the timer variable
	return tmr;
}
//This function returns a new Location based on the previous one.
int updateLocation(int loc, int len){
	  //Move the display if we are unpaused
		  if (pause == 0){
			  dancing = 0;
			  dance_state = 2;
			  if (reverse == 0)
				  loc++;   //Move the display forwards if the backwards button is NOT toggled (KEY2)
			  else
				  loc--;  //Otherwise we go backwards if the user toggled the display to go backwards
		  }
		  //If we are paused, check to see if dancing has been pressed
		  else{
			  reverse = 0;
			  if (dancing) {
				  if (dance_dir){
					  //If the Dancing Direction switch is down (SW8), cycle through the states so the letters move down
					  dance_state = (dance_state + 1) % 5;}
				  else{
					  //If the Dancing Direction switch is up (SW8), cycle through the states so the letters move up
					  dance_state = (dance_state - 1);
					  if (dance_state < 0)
						  dance_state = dance_state + 5;
				  }
			  }
		  }
		  if (loc >= len){ //If we have reached the end of the string, reset the locator back to the beginning
			  return loc % len;
		  }
		  else if (loc < 0){ //If we have reached the end of the string backwards, we need to jump back the other way
			  return loc + len;
		  }
		  return loc;
}

//This function updates the logic based on the buttons pressed
void updatePBState(int button_datain){
        //Reverse Button/Dancing Button (if paused), KEY0 (toggle)
        if ((button_datain & 1) == 0 && toggle == 0){
              switch(flag){
                case 0:
                      disp_off=0;
                    break;
            case 1:
                  speedup_toggle=1;
                  alt_putstr("Speeding up! (Hold down to speed up more)\n");
                  break;
            case 2:
                  speedup_toggle=1;
                  alt_putstr("Even Faster (Hold down to speed up more)!!!\n");
                  break;
            case 3:
                  speedup_toggle=1;
                  alt_putstr("Faster Still!!!\n");
                        break;
            case 4:
                  speedup_toggle=0;
                      slowdown_toggle=1;
                      alt_putstr("Slowing Down...\n");
                      break;
            case 5:
                  slowdown_toggle=0;
                  alt_putstr("Backwards!\n");
                  reverse = 1;
                  break;
            case 6:
                  alt_putstr("Topsy-Turvey!\n");
                      upsideDown = 1;
                      reverse = 0;
                      break;
            case 7:
                  upsideDown = 0;
                        pause = 1;
                        dancing = 1;
                        dance_dir = 1;
                        alt_putstr("Let's Dance!\n");
                        break;
            case 8:
                  pause = 1;
                      dancing = 1;
                      alt_putstr("Keep Dancing!\n");
                      dance_dir = 0;
                      break;
            case 9:
                  pause = 0;
                      disp_off = 1;
                      alt_putstr("Taking a nap...zzzz....\n");
                      flag = -1;
                      break;
              }
              toggle = 1;
              flag++;
        } else if ((button_datain & 1) != 0) {
              toggle = 0; // So user doesn't continuously toggle
              speedup_toggle = 0;
        }

        //If the user wishes to re-enter text, KEY1
        if ((button_datain & 2) == 0){
              flag = 0;
              re_enter = 1;
        }
}

//Gets the lowest number representation of the given letter
int getBinLowLow(char letter){
	int letter_inv = ~getBinaryLetter(letter); //Get the integer representation of the letter; the inverting logic is easier to deal with
	int bit0 = (letter_inv & 0b0000001) << 3; //This logic deals with bit shifting so the letters appear higher on the display
	int res = (0b0000000) | bit0;
	return ~res; //Reinvert the binary representation of the modified letter so the display reads the correct representation
}
//Gets a lower integer representation of the given letter
int getBinLow(char letter){
	int letter_inv = ~getBinaryLetter(letter); //Get the integer representation of the letter; inverting the binary makes the logic easier
	int bit0 = (letter_inv & 0b0000001) << 6; //This logic deals with bit shifting so the letters appear higher on the display
	int bit1 = (letter_inv & 0b0000010) << 1;
	int bit5 = (letter_inv & 0b0100000) >> 1;
	int bit7 = (letter_inv & 0b1000000) >> 3;
	int res = (0b0000000) | bit0 | bit1 | bit5 | bit7;
	return ~res; //Uninvert the binary representation so the display knows which lights to turn on
}
//Gets the binary representation of the character
int getBin(char letter){
	/*Based on the character entered, we convert to binary so the 7-segment knows which lights to turn on.
	The 7-segment has inverted logic so a 0 means the light is on and a 1 means the light is off.
	The rightmost bit starts the index at HEX#[0], and the leftmost bit is HEX#[6], the pattern
	for the 7-segment is shown in the DE0_C5 User Manual*/
	switch(letter){
	case '0':
		return 0b1000000;
	case '1':
		return 0b1111001;
	case '2':
		return 0b0100100;
	case '3':
		return 0b0110000;
	case '4':
		return 0b0011001;
	case '5':
	case '6':
		return 0b0000010;
	case '7':
		return 0b1111000;
	case '8':
		return 0b0000000;
	case '9':
		return 0b0010000;
	case 'A':
		return 0b0001000;
	case 'B'://Lowercase
		return 0b0000011;
	case 'C':
		return 0b1000110;
	case 'D'://Lowercase
		return 0b0100001;
	case 'E':
		return 0b0000110;
	case 'F':
		return 0b0001110;
	case 'G':
		return 0b0010000;
	case 'H':
		return 0b0001001;
	case 'I':
		return 0b1111001;
	case 'J':
		return 0b1110001;
	case 'K':
		return 0b0001010;
	case 'L':
		return 0b1000111;
	case 'N':
		return 0b0101011;
	case 'O':
		return 0b1000000;
	case 'P':
		return 0b0001100;
	case 'Q':
		return 0b0011000;
	case 'R'://Lowercase
		return 0b0101111;
	case 'S':
		return 0b0010010;
	case 'T':
		return 0b0000111;
	case 'U':
		return 0b1000001;
	case 'V':
		return 0b1100011;
	case 'X':
		return 0b0011011;
	case 'Y':
		return 0b0010001;
	case 'Z':
		return 0b0100100;
	default:
		return 0b1111111;
	}
}
//Gets the upper binary representation of the character
int getBinHigh(char letter){
	int letter_inv = ~getBinaryLetter(letter); //Get the integer representation of the letter, the logic is easier to work with inverted
	int bit2 = (letter_inv & 0b0000100) >> 1 ; //This logic deals with bit shifting so the letters appear higher on the display
	int bit3 = (letter_inv & 0b0001000) << 3;
	int bit4 = (letter_inv & 0b0010000) << 1 ;
	int bit6 = (letter_inv & 0b1000000) >> 6;
	int res = (0b0000000) | bit2 | bit3 | bit4 | bit6;
	return ~res;//Uninvert the logic to get the correct representation
}
//Gets the highest number representation of the given letter
int getBinHighHigh(char letter){
	int letter_inv = ~getBinaryLetter(letter); //Get the integer representation of the letter, it is easier to deal with the inverted logic
	int bit3 = (letter_inv & 0b0001000) >> 3; //This logic deals with bit shifting so the letters appear higher on the display
	int res = (0b0000000) | bit3;
	return ~res; //Uninvert the logic to get the correct representation
}
//Returns the letter or the upsideDown version of the letter
int getBinaryLetter(char letter){
	int let = getBin(letter);
	if (upsideDown){
		//If the user has toggled the upsideDown switch, (SW8), we can use bit shifting to invert the display
		int letter_inv = ~let; //Inverting the binary makes the logic easier to deal with.
		int bit0 = (letter_inv & 0b0000001) << 3;
		int bit1 = (letter_inv & 0b0000010) << 1;
		int bit2 = (letter_inv & 0b0000100) >> 1;
		int bit3 = (letter_inv & 0b0001000) >> 3;
		int bit4 = (letter_inv & 0b0010000) << 1;
		int bit5 = (letter_inv & 0b0100000) >> 1;
		int bit6 = (letter_inv & 0b1000000);
		int full_inv = (0b0000000) | bit0 | bit1 | bit2 | bit3 | bit4 | bit5 | bit6;
		return ~full_inv; //Invert the logic back again
	}
	//Otherwise, if the SW8 is in the rightside-up position, we can just display the letter
	return let;
}
//Prints each of the letters out to the screen
void print(int let5, int let4, int let3, int let2, int let1, int let0){
	//Takes the binary value for each letter and places it on each of the six 7-segment displays
	IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, let5);
	IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, let4);
	IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, let3);
	IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, let2);
	IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, let1);
	IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, let0);
	return;
}
//Prints each of the letters out to the screen; takes into account the dancing letters
void print_letters(char let5, char let4, char let3, char let2, char let1, char let0, int state){
	//If the display is "muted," don't show anything
	if (disp_off){
		print(getBin('!'), getBin('!'), getBin('!'), getBin('!'), getBin('!'), getBin('!'));
		return;
	}
	//State refers to which dancing state the characters are in
	switch (state){
	//This is the case where the letters are shifted down by the maximum amount on the display
	case 0:
		IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBinLowLow(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBinLowLow(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBinLowLow(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBinLowLow(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBinLowLow(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBinLowLow(let0));
		return;
	//This is the case where the letters are shifted down a bit on the display
	case 1:
		IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBinLow(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBinLow(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBinLow(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBinLow(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBinLow(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBinLow(let0));
		return;
	//This is the "main" case, where the full letters are displayed on the display
	case 2:
		IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBinaryLetter(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBinaryLetter(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBinaryLetter(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBinaryLetter(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBinaryLetter(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBinaryLetter(let0));
		return;
	//This is the case where the letters are shifted up a bit on the display
	case 3:
		IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBinHigh(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBinHigh(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBinHigh(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBinHigh(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBinHigh(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBinHigh(let0));
		return;
	//This is the case where the letters are shifted by the maximum amount on the display
	default:
		IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, getBinHighHigh(let5));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, getBinHighHigh(let4));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, getBinHighHigh(let3));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, getBinHighHigh(let2));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, getBinHighHigh(let1));
		IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, getBinHighHigh(let0));
		return;
	}
}
