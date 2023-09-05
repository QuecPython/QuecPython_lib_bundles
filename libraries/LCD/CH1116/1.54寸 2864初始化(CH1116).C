/* IQC program */
/* IC : 1.54 sh1106  8080 8bit */
/* Module : 12864-COG */

#include "io51.h"


/*副程式*/   
void write_i(unsigned char ins)
{
	
   DC=0;
   CS=0;
   WR=1;
   P1=ins;       /*inst*/
   WR=0;
   WR=1;
   CS=1;
}

void write_d(unsigned char dat)
{ 
   DC=1;
   CS=0;
   WR=1;
   P1=dat;       /*data*/
   WR=0;
   WR=1;
   CS=1;
}


void delay(unsigned int i)							
{
   	while(i>0)
   	{
		i--;
   	}
}


                   
void  CH1116()
{
       write_i(0xAE);    /*display off*/       
       
       write_i(0x00);    /*set lower column address 0x02 */       
       write_i(0x10);    /*set higher column address*/
       
       write_i(0x40);    /*set display start line*/
       
       write_i(0xB0);    /*set page address*/
       
       write_i(0x81);    /*contract control  */
       write_i(0x65);    /*128*/
       
       write_i(0xA1);    /*set segment remap  0XA1*/
      
       write_i(0xA6);    /*normal / reverse*/
       
       write_i(0xA8);    /*multiplex ratio*/
       write_i(0x3F);    /*duty = 1/64*/
       
       write_i(0xad);    /*set charge pump enable*/
       write_i(0x8A);     /*    0x8a    外供VCC   */       
       write_i(0xC8);    /*Com scan direction   0XC8 */
       
       write_i(0xD3);    /* set display offset */
       write_i(0x00);   
       
       write_i(0xD5);    /* set osc division */
       write_i(0x80);    
       
       write_i(0xD9);    /*set pre-charge period*/
       write_i(0x22);    /*0x22*/
       
       write_i(0xDA);    /*set COM pins*/
       write_i(0x12);
       
       write_i(0xdb);    /*set vcomh*/
       write_i(0x40);     
       
       
       write_i(0xAF);    /*display ON*/                      

}

